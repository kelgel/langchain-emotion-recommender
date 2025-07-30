from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import sys
import os

# 경로 설정
# current_dir = os.path.dirname(os.path.abspath(__file__))
# agents_dir = os.path.join(current_dir, 'app', 'agents')
# sys.path.insert(0, agents_dir)
#
# from wiki_search_agent import WikiSearchAgent
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "app"))

# ✨ main_agent import
from main_agent.main_agent import run_main_agent

load_dotenv()

app = FastAPI(title="AI Bookstore Service")

# CORS 설정 (Spring Boot와 통신용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8001", "http://localhost:8003"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# WikiSearchAgent 초기화
#wiki_agent = WikiSearchAgent()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "AI Service is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "AI Service is running"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # WikiSearchAgent를 통해 처리
        # result = wiki_agent.process(request.message)
        result = run_main_agent(request.message)

        # ✅ 수정: 'response' 키에서 가져오기
        return {
            "response": result.get("response", ""),  # ← 이게 실제 message
            "success": True,
            "clarification_needed": result.get("clarification_needed", False),
            "query": result.get("query", {}),
            "intent": result.get("intent", "")
        }

        # 우선 출력 형태를 맞추기 위해서 조건문은 주석처리
        # if result.get('success', True):
        #     return {"response": result.get('message', ''), "success": True}
        # else:
        #     return {"response": result.get('message', '오류가 발생했습니다.'), "success": False}
        #
    except Exception as e:
        return {"response": f"AI 서비스 연결에 실패했습니다: {str(e)}", "success": False}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)