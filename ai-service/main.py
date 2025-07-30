from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
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

# 세션 미들웨어 추가 (브라우저 종료까지 유지)
app.add_middleware(
    SessionMiddleware,
    secret_key="ai-bookstore-secret-key-2024",
    max_age=None,  # 브라우저 종료까지
    https_only=False,  # 개발환경에서는 False
    same_site='lax',  # 개발환경에서는 lax 사용
    session_cookie="ai_session"  # 쿠키 이름 명시
)

# CORS 설정 (Spring Boot와 통신용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8001", "http://localhost:8003"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,  # 쿠키 전송 허용
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
async def chat(request: ChatRequest, http_request: Request):
    try:
        # WikiSearchAgent를 통해 처리
        # result = wiki_agent.process(request.message)
        # 세션 ID를 헤더에서 가져오거나 생성
        session_id = http_request.headers.get("X-Session-ID")
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
        
        # 전역 세션 및 에이전트 인스턴스 딕셔너리 생성
        if not hasattr(chat, 'sessions'):
            chat.sessions = {}
        if not hasattr(chat, 'agent_instances'):
            chat.agent_instances = {}
        
        if session_id not in chat.sessions:
            chat.sessions[session_id] = {
                "conversation_history": [],
                "current_agent": None
            }
            chat.agent_instances[session_id] = {} # 새 세션을 위한 에이전트 인스턴스 딕셔너리
        
        if request.message.lower() in ['quit', 'exit', '종료', '나가기']:
            if session_id in chat.sessions:
                del chat.sessions[session_id]
            if session_id in chat.agent_instances:
                del chat.agent_instances[session_id]
            return {
                "response": "대화를 종료하고 모든 대화 내역을 삭제했습니다.",
                "success": True,
                "session_id": session_id,
                "clarification_needed": False,
                "query": {},
                "intent": "exit"
            }
        
        print(f"세션 ID: {session_id}")
        print(f"세션 전 상태: {chat.sessions[session_id]}")
            
        result = run_main_agent(request.message, chat.sessions[session_id], chat.agent_instances[session_id])
        
        print(f"세션 후 상태: {chat.sessions[session_id]}")

        # ✅ 수정: clarification과 response 둘 다 처리
        response_text = result.get("response", "") or result.get("message", "")
        
        return {
            "response": response_text,
            "success": True,
            "session_id": session_id,  # 세션 ID 반환
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)