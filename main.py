import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 1. CONFIGURATION & SECURITY ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. VECTOR DATABASE SETUP ---
# Using local embedding model for RAG
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Loading the Siemens S7-1200 Manual Database
print("🧠 Loading existing Vector Database...")
vector_db = Chroma(persist_directory="./siemens_db", embedding_function=embedding_model)
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# --- 3. AI CORE FUNCTIONS ---

def extract_error_from_image(image_path):
    """
    Extracts technical fault descriptions from TIA Portal screenshots using Gemini Vision.
    """
    print(f"📸 Analyzing Image: {image_path}")
    
    # Use direct Google GenAI SDK for better image handling
    model = genai.GenerativeModel('gemini-2.0-flash') # Or 2.5 if verified in your region
    
    img = Image.open(image_path)
    vision_prompt = (
        "Identify the error code, Event ID, or technical fault shown in this "
        "TIA Portal screenshot. Describe the technical issue briefly."
    )
    
    response = model.generate_content([vision_prompt, img])
    return response.text

def format_docs(docs):
    """Formats retrieved manual pages for the context prompt."""
    return "\n\n".join(doc.page_content for doc in docs)

def run_maintenance_assistant(user_input, is_image=False):
    """
    Main RAG pipeline that combines User Input (Text/Image) with Siemens Manual Context.
    """
    # Quick filter for basic greetings
    greetings = ["hello", "hi", "سلام", "ازيك", "hey"]
    if not is_image and user_input.lower().strip() in greetings:
        return ("Hello! I am your Siemens AI Assistant. Please provide a "
                "specific error description or a screenshot from TIA Portal.")

    query = user_input
    if is_image:
        query = extract_error_from_image(user_input)
        print(f"🔍 AI detected from image: {query}")

    # Initialize Gemini for RAG reasoning
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0
    )
    
    # Expert Engineer Prompt Template
    template = """You are a Siemens Expert Engineer.
    Based ONLY on the provided manual context, solve the following issue: {question}
    
    If the context doesn't contain enough information, state that based on the manual.
    
    Context: {context}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # LangChain Runnable Protocol (LCEL)
    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt 
        | llm 
        | StrOutputParser()
    )
    
    return qa_chain.invoke(query)

if __name__ == "__main__":
    print("🦾 Siemens AI Assistant Engine is ready.")