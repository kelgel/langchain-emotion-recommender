# -*- coding: utf-8 -*-
"""
위키피디아 검색 도구 - Tool 계층
순수한 위키피디아 API 호출 기능만 제공
"""

import wikipediaapi

class WikipediaSearchTool:
    """위키피디아 검색 도구 클래스."""

    def __init__(self, language='ko'):
        """
        위키피디아 검색 도구를 초기화.

        Args:
            language (str): 검색할 언어 코드 (기본값: 'ko')
        """
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            user_agent='BookstoreAI/1.0 (https://example.com/contact)'
        )

    def search_page(self, search_term: str) -> dict:
        """
        위키피디아에서 페이지를 검색.

        순수한 검색 기능만 제공하며, 비즈니스 로직은 포함하지 않음.

        Args:
            search_term (str): 검색할 용어

        Returns:
            Dict: 검색 결과 딕셔너리
                - success (bool): 검색 성공 여부
                - title (str): 위키피디아 페이지 제목 (성공시)
                - summary (str): 요약 정보 (성공시)
                - content (str): 전체 내용 일부 (성공시)
                - url (str): 위키피디아 URL (성공시)
                - error (str): 오류 메시지 (실패시)

        Raises:
            None: 모든 예외는 내부적으로 처리되어 결과 딕셔너리로 반환
        """
        try:
            page = self.wiki.page(search_term)

            if page.exists():
                # 학력 정보가 있을 수 있는 섹션들을 우선적으로 포함
                full_text = page.text
                important_sections = self._extract_important_sections(full_text)
                
                # 중요 섹션 + 처음 부분 조합 (최대 4000자)
                content = (full_text[:2000] + "\n\n" + important_sections)[:4000]
                
                return {
                    'success': True,
                    'title': page.title,
                    'summary': page.summary,
                    'content': content,
                    'url': page.fullurl
                }
            else:
                return {
                    'success': False,
                    'error': f'위키피디아에서 "{search_term}"를 찾을 수 없습니다.'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'검색 중 오류 발생: {str(e)}'
            }

    def search_multiple_terms(self, search_terms: list) -> list:
        """
        여러 검색어로 순차적으로 검색.

        Args:
            search_terms (list): 검색어 리스트

        Returns:
            list: 각 검색어에 대한 결과 리스트
        """
        results = []
        for term in search_terms:
            result = self.search_page(term)
            results.append(result)
            # 성공한 첫 번째 결과를 우선적으로 반환할 수도 있지만,
            # 그런 판단은 상위 계층에서 하도록 모든 결과를 반환
        return results

    def _extract_important_sections(self, full_text: str) -> str:
        """위키피디아 텍스트에서 학력/이력 관련 중요 섹션 추출."""
        import re
        
        # 중요한 섹션 키워드들
        important_keywords = [
            '학력', '학교', '교육', '출생', '이력', '약력', '생애', 
            '고등학교', '대학교', '대학', '졸업', '입학', '진학',
            '수상', '경력', '작품', '활동'
        ]
        
        # 텍스트를 섹션별로 분할 (== 제목 == 형태)
        sections = re.split(r'\n==+\s*([^=]+)\s*==+\n', full_text)
        
        important_text = ""
        for i in range(1, len(sections), 2):  # 제목과 내용이 번갈아 나옴
            if i + 1 < len(sections):
                section_title = sections[i].strip()
                section_content = sections[i + 1].strip()
                
                # 중요 키워드가 포함된 섹션 추출
                if any(keyword in section_title.lower() for keyword in important_keywords):
                    important_text += f"\n\n=== {section_title} ===\n{section_content[:800]}"
                
                # 내용에서 학력 관련 정보가 있는 섹션도 포함
                elif any(keyword in section_content.lower() for keyword in ['고등학교', '대학', '졸업', '입학']):
                    important_text += f"\n\n=== {section_title} ===\n{section_content[:800]}"
        
        # 중요 섹션이 없으면 전체 텍스트에서 학력 관련 부분 찾기
        if not important_text:
            education_matches = re.findall(
                r'.{0,100}(?:고등학교|대학교|대학|졸업|입학|진학).{0,200}', 
                full_text, 
                re.IGNORECASE
            )
            if education_matches:
                important_text = "\n".join(education_matches[:3])
        
        return important_text[:1500]  # 최대 1500자