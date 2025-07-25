from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import sys
import os

# 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'app', 'agents')
sys.path.insert(0, agents_dir)

from wiki_search_agent import WikiSearchAgent

load_dotenv()

app = FastAPI(title="AI Bookstore Service")

# CORS 설정 (Spring Boot와 통신용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# WikiSearchAgent 초기화
wiki_agent = WikiSearchAgent()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "AI Service is running"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # WikiSearchAgent를 통해 처리
        result = wiki_agent.process(request.message)
        
        if result.get('success', True):
            return {"response": result.get('message', ''), "success": True}
        else:
            return {"response": result.get('message', '오류가 발생했습니다.'), "success": False}
            
    except Exception as e:
        return {"response": f"AI 서비스 연결에 실패했습니다: {str(e)}", "success": False}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)