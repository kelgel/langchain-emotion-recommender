import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import OpenAI
import uvicorn

load_dotenv()

app = FastAPI(title="AI Service")

# CORS 설정 (Spring Boot와 통신용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# LLM 초기화
llm = OpenAI(temperature=0)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "AI Service is running"}

@app.get("/health")  # 👈 이 부분 추가
async def health():
    return {
        "status": "healthy",
        "timestamp": time.time_ns(),
        "service": "AI Service",
        "version": "1.0.0"
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    response = llm(request.message)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 👈 핫 리로드 활성화
    )