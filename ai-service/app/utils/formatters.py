# # 상품 상세 정보 출력 위한 유틸
# from typing import List
# from langchain_core.documents import Document
#
# def format_recommendation_result_with_isbn(docs: List[Document]) -> str:
#     formatted = []
#     for i, doc in enumerate(docs):
#         content = doc.page_content
#         isbn = doc.metadata.get("isbn", "")
#         product_name = doc.metadata.get("product_name", "제목 없음")
#         author = doc.metadata.get("author", "저자 미상")
#         url = f"http://localhost:8080/product/detail?isbn={isbn}" if isbn else "URL 없음"
#
#         entry = (
#             f"{i+1}. 📚 {product_name} - {author}\n"
#             f"   📄 {content[:200]}...\n"
#             f"   🔗 <a href='{url}' target='_blank'>상세 보기</a>"
#         )
#         formatted.append(entry)
#     return "\n\n".join(formatted)
#

from typing import List
from langchain_core.documents import Document

def format_recommendation_result_with_isbn(docs: List[Document]) -> str:
    formatted = []
    seen = set()

    for doc in docs:
        isbn = doc.metadata.get("isbn", "")
        title = doc.metadata.get("product_name", "")
        unique_key = isbn or title  # ISBN이 없으면 title 기준

        # ✅ 중복 제거
        if unique_key in seen:
            continue
        seen.add(unique_key)

        content = doc.page_content
        author = doc.metadata.get("author", "저자 미상")
        url = f"http://localhost:8080/product/detail?isbn={isbn}" if isbn else "URL 없음"

        entry = (
            f"{len(formatted)+1}. 📚 {title} - {author}\n"
            f"   📄 {content[:200]}...\n"
            f"   🔗 [상세 보기]({url})"
        )
        formatted.append(entry)

        # ✅ 3권만 출력
        if len(formatted) >= 3:
            break

    return "\n\n".join(formatted)
