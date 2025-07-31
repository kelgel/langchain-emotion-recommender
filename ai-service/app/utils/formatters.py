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
import re
from typing import List
from langchain_core.documents import Document

def format_links_only(docs: List[Document]) -> List[str]:  # 🔄 반환값을 리스트로
    links = []
    for doc in docs:
        isbn = doc.metadata.get("isbn", "")
        if isbn:
            url = f"http://localhost:8080/product/detail?isbn={isbn}"
            links.append(f"🔗 {url}")
    return links

def combine_response_with_links(llm_response: str, docs: List[Document]) -> str:
    links = format_links_only(docs)  # 🔄 이제는 리스트
    llm_lines = llm_response.strip().split("\n")
    combined_output = []

    doc_index = 0
    for line in llm_lines:
        combined_output.append(line)
        # 번호로 시작하는 줄일 때 링크 삽입
        if re.match(rf"^{doc_index+1}\.", line.strip()):
            if doc_index < len(links):
                combined_output.append(links[doc_index])  # 번호 없는 🔗 링크
            doc_index += 1

    return "\n".join(combined_output)

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

