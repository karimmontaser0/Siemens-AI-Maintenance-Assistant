from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from main import run_maintenance_assistant
import shutil
import os

app = FastAPI(title="Siemens AI Maintenance API")

@app.get("/")
def home():
    return {"message": "Siemens AI Maintenance API is running! 🦾"}

from typing import Optional

@app.post("/ask-ai")
async def ask_ai(
    question: Optional[str] = Form(None), 
    file: Optional[UploadFile] = File(None)
):
    # حالة 1: لو بعت صورة (زي اللي بيحصل في n8n لما ترفع ملف)
    if file:
        temp_file = f"api_temp_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            print(f"📸 API received image: {file.filename}")
            result = run_maintenance_assistant(temp_file, is_image=True)
            return {"source": "image_analysis", "solution": result}
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    # حالة 2: لو بعت نص بس
    if question:
        print(f"💬 API received question: {question}")
        result = run_maintenance_assistant(question, is_image=False)
        return {"source": "text_query", "solution": result}

    raise HTTPException(status_code=400, detail="Please provide either a question or an image.")

# لتشغيل الـ API: uvicorn api:app --reload