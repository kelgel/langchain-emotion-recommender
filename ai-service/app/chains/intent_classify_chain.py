from langchain_core.runnables import RunnableLambda
from utils.parse_intent import parse_intent
from prompts.intent_classify_prompt import  intent_classify_prompt
from config.llm import intent_classify_llm

intent_classify_chain = intent_classify_prompt | intent_classify_llm | RunnableLambda(parse_intent)
