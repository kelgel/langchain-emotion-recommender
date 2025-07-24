from langchain_core.runnables import RunnableLambda
from utils.parse_keywords import parse_keywords
from prompts.query_analysis_prompt import query_analysis_prompt
from config.llm import query_analysis_llm

query_analysis_chain = query_analysis_prompt | query_analysis_llm | RunnableLambda(parse_keywords)
