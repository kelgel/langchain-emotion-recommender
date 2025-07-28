"""
llm.py
한 파일에 목적별로 필요한 LLM 객체 모두 정의
"""

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set.")
#embedding_model = OpenAIEmbeddings()

# 목적별로 필요한 LLM 객체 정의
query_analysis_llm = ChatOpenAI(api_key=api_key, temperature=0.0)
intent_classify_llm = ChatOpenAI(api_key=api_key, temperature=0.0)
clarification_llm = ChatOpenAI(api_key=api_key, temperature=0.5)
recommendation_llm = ChatOpenAI(api_key=api_key, temperature=0.7)
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
