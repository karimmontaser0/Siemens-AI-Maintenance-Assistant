from fastapi import FastAPI, UploadFile, File
from main import run_maintenance_assistant
import uvicorn

app = FastAPI(title="Siemens AI Maintenance API")

# --- API ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "Online", "model": "Gemini 2.0 Flash", "domain": "Siemens S7-1200"}

@app.post("/ask")
async def ask_question(query: str):
    """Endpoint for text-based PLC troubleshooting."""
    result = run_maintenance_assistant(query, is_image=False)
    return {"query": query, "solution": result}

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """Endpoint for vision-based diagnostic buffer analysis."""
    # Logic to save and process image
    file_path = f"api_temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    result = run_maintenance_assistant(file_path, is_image=True)
    return {"filename": file.filename, "analysis": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)