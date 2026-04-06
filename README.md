# 🦾 Siemens S7-1200 AI Maintenance Assistant

An advanced **Agentic RAG (Retrieval-Augmented Generation)** system designed to assist engineers in diagnosing and troubleshooting Siemens S7-1200 PLC faults using **Gemini 2.0 Flash** and **LangGraph**.

---

## 🚀 Key Features

* **Agentic Self-Correction:** Built with **LangGraph**, the system includes a **Critic Node** that validates technical solutions against the official manual before outputting them to the user.
* **Multimodal Analysis:** Capable of extracting error codes and fault descriptions directly from **TIA Portal screenshots** using Gemini Vision.
* **Industrial-Grade RAG:** Uses a local vector database (**ChromaDB**) containing the Siemens S7-1200 Service Manual for high-precision, offline-capable retrieval.
* **Safety-First Design:** Prioritizes industrial safety warnings and official Siemens protocols in every generated solution.

---

## 🛠️ Tech Stack

* **Orchestration:** LangGraph (Stateful Multi-Agent Workflows)
* **LLM:** Google Gemini 2.5 Flash (Reasoning & Vision)
* **Framework:** LangChain (LCEL)
* **Vector Database:** ChromaDB
* **Embeddings:** HuggingFace (all-MiniLM-L6-v2)
* **Automation Ready:** Designed for integration with n8n and FastAPI.

---

## 🧠 System Architecture

The system operates in a **Closed-Loop Feedback** cycle:
1. **Input:** User provides text or an image of a PLC error.
2. **Research:** The Agent retrieves technical context from the Siemens Manual.
3. **Critique:** A dedicated "Critic Agent" reviews the solution for accuracy.
4. **Loop:** If the solution is incomplete, it loops back for refinement (up to 3 iterations).
5. **Output:** A verified, safe technical remedy.

---

## 📥 Installation & Setup

**1. Clone the repository:**

    git clone https://github.com/karimmontaser0/Siemens-AI-Maintenance-Assistant.git
    cd Siemens-AI-Maintenance-Assistant

**2. Create a Virtual Environment:**

    python -m venv ai_env
    source ai_env/bin/activate  # On Windows: ai_env\Scripts\activate

**3. Install Dependencies:**

    pip install -r requirements.txt

**4. Environment Variables:**
Create a .env file and add your Google API Key:

    GOOGLE_API_KEY=your_api_key_here

**5. Run the Assistant:**

    python main.py

---

## 👨‍💻 Author

**Kareem Montaser**
*Mechatronics Engineer | Backend & AI Automation Specialist*
[LinkedIn](https://www.linkedin.com/in/karim-montaser-bb608a313) | [GitHub](https://github.com/karimmontaser0)
