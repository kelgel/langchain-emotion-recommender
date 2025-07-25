from langchain_core.runnables import RunnableLambda
from prompts.clarification_prompt  import get_clarification_prompt
from utils.parse_keywords import parse_keywords
from config.llm import clarification_llm

def get_clarification_chain(intent: str):
    prompt = get_clarification_prompt(intent)
    return prompt | clarification_llm | RunnableLambda(parse_keywords)



