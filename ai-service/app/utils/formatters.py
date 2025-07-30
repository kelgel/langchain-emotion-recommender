# 상품 상세 정보 출력 위한 유틸
from typing import List
from langchain_core.documents import Document

def format_recommendation_result_with_isbn(docs: List[Document]) -> str:
    formatted = []
    for i, doc in enumerate(docs):
        content = doc.page_content
        isbn = doc.metadata.get("isbn", "")
        product_name = doc.metadata.get("product_name", "제목 없음")
        author = doc.metadata.get("author", "저자 미상")
        url = f"http://localhost:8080/product/detail?isbn={isbn}" if isbn else "URL 없음"

        entry = (
            f"{i+1}. 📚 **{product_name}** - {author}\n"
            f"   📄 {content[:200]}...\n"
            f"   🔗 [상세 보기]({url})"
        )
        formatted.append(entry)
    return "\n\n".join(formatted)

