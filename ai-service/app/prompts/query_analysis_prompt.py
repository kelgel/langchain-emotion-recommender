"""
query_analysis_prompt.py
query_analysis_prompt 질의 분석 프롬프트
"""

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 1. .env 파일에서 환경변수 불러오기
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set.")

# 프롬프트 템플릿 정의
query_analysis_prompt = PromptTemplate(
    input_variables = ["user_input"],
    template="""
당신은 감정 기반 도서 추천 시스템의 텍스트 분석 AI입니다.

사용자의 요청을 분석하여 다음 정보를 추출하세요:
- emotion(감정): 예)우울, 행복, 사랑 등
- genre(장르) :  예)에세이, 판타지, 스릴러 등
- keywords(중요 단어): 사용자의 요구에서 중심이 되는 핵심 단어들

사용자 입력: {user_input}

응답 형식 (JSON):
{{
    "emotion": "...",
    "genre": "..."
    "keywords": ["...", "...", "..."]
}}
    """
)

# LLM 객체 정의 (실행은 다른 곳에서 사용)
query_analysis_llm = ChatOpenAI(api_key=openai_api_key, temperature=0.0)

