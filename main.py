import os
from typing import TypedDict, List
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END

# --- 1. CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("Your_Gemini_Api_Key")
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. VECTOR DB SETUP ---
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="./siemens_db", embedding_function=embedding_model)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# --- 3. STATE DEFINITION ---
class AgentState(TypedDict):
    original_query: str
    current_generation: str
    critique_feedback: str
    is_valid: bool
    iterations: int

# --- 4. NODES (The Engine Parts) ---

def extract_error_node(state: AgentState):
    """If image path is provided, extract error using Gemini Vision."""
    query = state["original_query"]
    if query.lower().endswith(('.png', '.jpg', '.jpeg')):
        print("📸 Analyzing Image with Gemini Vision...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        img = Image.open(query)
        response = model.generate_content(["Identify the Siemens error code/fault in this TIA Portal screenshot.", img])
        return {"original_query": response.text}
    return {"original_query": query}

def researcher_node(state: AgentState):
    """RAG Node: Generates solution based on Manual + Feedback."""
    print(f"🧠 Generation Attempt #{state['iterations'] + 1}")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    docs = retriever.invoke(state["original_query"])
    context = "\n\n".join(doc.page_content for doc in docs)
    
    feedback = f"\nNote: Previous attempt was rejected. Feedback: {state['critique_feedback']}" if state['critique_feedback'] else ""
    
    template = """You are a Siemens Expert Engineer. 
    Use the context below to solve the issue. If you have feedback from a previous attempt, address it.
    
    Context: {context}
    Question: {question} {feedback}
    
    Answer clearly and technically:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"context": context, "question": state["original_query"], "feedback": feedback})
    return {"current_generation": response, "iterations": state["iterations"] + 1}

def critic_node(state: AgentState):
    """Validation Node: Checks if the answer is accurate and safe."""
    print("⚖️ Critiquing Solution...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    critic_prompt = f"""Review this Siemens technical solution for accuracy and safety.
    Solution: {state['current_generation']}
    
    Is this solution complete and safe? Answer only 'YES' or 'NO'. 
    If 'NO', provide a very brief technical reason why."""
    
    response = llm.invoke(critic_prompt).content
    is_valid = "YES" in response.upper()
    feedback = response if not is_valid else ""
    
    return {"is_valid": is_valid, "critique_feedback": feedback}

# --- 5. GRAPH CONSTRUCTION ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("vision_extractor", extract_error_node)
workflow.add_node("researcher", researcher_node)
workflow.add_node("critic", critic_node)

# Set Flow
workflow.set_entry_point("vision_extractor")
workflow.add_edge("vision_extractor", "researcher")
workflow.add_edge("researcher", "critic")

# Conditional Logic (The Self-Correction Loop)
def should_continue(state: AgentState):
    if state["is_valid"] or state["iterations"] >= 3:
        return "end"
    return "researcher"

workflow.add_conditional_edges("critic", should_continue, {
    "end": END,
    "researcher": "researcher"
})

# Compile
app = workflow.compile()

# --- 6. RUNNER ---
if __name__ == "__main__":
    print("🚀 Starting Technical Test...")
    
    # جرب سؤال فني محدد عن S7-1200
    user_input = "My PLC has a red error light. How do I fix it quickly?" 
    
    initial_state = {
        "original_query": user_input,
        "current_generation": "",
        "critique_feedback": "",
        "is_valid": False,
        "iterations": 0
    }
    
    # تشغيل الـ Graph
    final_output = app.invoke(initial_state)
    
    print("\n--- FINAL REPORT ---")
    print(f"Total Iterations: {final_output['iterations']}")
    print(f"Final Solution: {final_output['current_generation'][:200]}...") # أول 200 حرف للتأكد