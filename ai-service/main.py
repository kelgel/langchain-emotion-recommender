# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from dotenv import load_dotenv
# import uvicorn
# import app.main_agent.main_agent
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import BaseModel
from starlette.middleware.cors import CORSMiddleware

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

app = FastAPI(title="AI Bookstore Service")

# CORS 미들웨어 설정
# 특정 출처에서의 요청을 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8001", "http://localhost:8003"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 요청 본문의 데이터 모델을 정의합니다.
class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "AI Service is running"}

@app.get("/health")
async def health():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "message": "AI Service is running"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """채팅 요청을 처리하고 AI 에이전트의 응답을 반환합니다."""
    try:
        # user_input = request.message.strip() # 개발 끝나면 수정하기
        user_input = "호전적인 역사 소설 추천해줘"
        # 입력 메시지가 비어 있는지 확인합니다.
        if not user_input:
            return {"response": "메시지를 입력해주세요.", "success": False}
        # 메인 에이전트 실행
        response = await app.main_agent.main_agent.run_pipeline(user_input)

        if response.get('success', True):
            return {"response": response.get('message', ''), "success": True}
        else:
            return {"response": response.get('message', '오류가 발생했습니다.'), "success": False}

    except Exception as e:
        # 예외 발생 시 에러 메시지를 반환합니다.
        return {"response": f"AI 서비스 연결에 실패했습니다: {str(e)}", "success": False}

# 이 스크립트가 직접 실행될 때 FastAPI 서버를 시작합니다.
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
