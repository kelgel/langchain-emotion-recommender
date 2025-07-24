#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 체인 - Chain 계층
비즈니스 로직과 워크플로우 제어, 엣지케이스 매니징을 담당
"""

from typing import Dict, Any
import sys
import os
import json

# 모델 및 유틸 import를 위한 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(os.path.dirname(current_dir), 'models')
utils_dir = os.path.join(os.path.dirname(current_dir), 'utils')
sys.path.insert(0, models_dir)
sys.path.insert(0, utils_dir)

from wiki_query_intent import WikiQueryIntent, IntentType, InfoType
from wiki_text_processing import WikiTextProcessor
from wiki_information_extractor import WikiInformationExtractor
from wiki_pattern_matcher import WikiPatternMatcher

# OpenAI 모듈 안전하게 import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()  # .env 파일에서 환경변수 로드
except ImportError:
    # python-dotenv가 설치되지 않은 경우 패스
    pass

# 명시적 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
tools_dir = os.path.join(os.path.dirname(current_dir), 'tools')
prompts_dir = os.path.join(os.path.dirname(current_dir), 'prompts')

sys.path.insert(0, tools_dir)
sys.path.insert(0, prompts_dir)

from wiki_search_tool import WikipediaSearchTool
from wiki_search_prompt import WikiSearchPrompt


class WikiSearchChain:
    """위키피디아 검색 워크플로우 체인 클래스."""

    def __init__(self):
        """체인을 초기화하고 필요한 컴포넌트들을 설정."""
        self.tool = WikipediaSearchTool()
        self.prompt = WikiSearchPrompt()
        
        # OpenAI 클라이언트 초기화 (환경변수에서 API 키 로드)
        self.llm_client = None
        if OPENAI_AVAILABLE:
            try:
                self.llm_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except Exception:
                # API 키가 없으면 폴백 모드로 동작
                pass

    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """메인 질의 처리 함수: clarification/context/fresh 검색 분기 명확화"""
        print(f"[DEBUG] execute() 시작 - query: {query}")
        
        # 1. clarification(추가 정보 요청) 분기
        if context.get('waiting_for_clarification', False):
            print("[DEBUG] clarification 분기")
            return self._handle_clarification_response(query, context)
        
        # 2. 복합 질문 처리 (최우선)
        compound_result = self._handle_compound_query(query, context)
        if compound_result:
            print("[DEBUG] 복합 질문 처리")
            return compound_result
        
        # 3. context 체크를 먼저 수행 (더 정교한 우선순위)
        context_check = self._check_context_priority(query, context)
        print(f"[DEBUG] context_check: {context_check}")
        if context_check['should_use_context']:
            print("[DEBUG] context question 분기")
            return self._handle_context_question(query, context)
            
        # 4. 질문에 작가명이 있으면 fresh 검색
        contains_author = self._contains_author_name(query)
        print(f"[DEBUG] contains_author_name: {contains_author}")
        if contains_author:
            print("[DEBUG] fresh search (작가명 있음)")
            return self._fresh_search_flow(query, context)
            
        # 5. 나머지는 fresh 검색
        print("[DEBUG] fresh search (기본)")
        return self._fresh_search_flow(query, context)

    def _fresh_search_flow(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """[수정됨] LLM intent 분석 결과를 기반으로 명확하게 워크플로우를 분기."""
        print(f"[DEBUG] _fresh_search_flow() 시작 - query: {query}")
        
        # 관련 없는 질문 먼저 필터링
        if self._is_irrelevant_query(query):
            return {
                'action': 'error',
                'message': "죄송합니다. 도서, 작가, 출판사에 대한 질문만 답변드릴 수 있습니다. 다른 질문을 해주세요.",
                'update_context': {}
            }
        
        # 1. LLM으로 사용자 의도 분석 (이 결과를 유일한 진실로 간주)
        query_intent = self._analyze_query_intent(query, context)
        print(f"[DEBUG] query_intent: {query_intent}")
        intent_type = query_intent.get('type')
        print(f"[DEBUG] intent_type: {intent_type}")

        # 2. 의도에 따라 명확히 다른 핸들러 호출
        if intent_type == 'book_to_author':
            # 책 -> 작가 찾기
            book_title = query_intent.get('book_title')
            if book_title:
                return self._handle_book_to_author_query(book_title, query_intent, context)
            else:
                # LLM이 책 제목을 못찾은 경우
                return {
                    'action': 'error',
                    'message': '작품명을 정확히 파악하지 못했습니다. 더 명확하게 질문해주시겠어요?',
                    'update_context': {}
                }

        elif intent_type == 'author_search':
            # 작가 정보 검색
            author_name = query_intent.get('keywords', [None])[0]
            if author_name:
                return self._handle_author_search_query(query, author_name, query_intent, context)
            else:
                # LLM이 작가명을 못찾은 경우
                return {
                    'action': 'error',
                    'message': '작가명을 정확히 파악하지 못했습니다. 더 명확하게 질문해주시겠어요?',
                    'update_context': {}
                }

        elif intent_type == 'context_question':
            # 이전 대화 기반 질문
            return self._handle_context_question(query, query_intent, context)

        else:
            # 의도를 파악하지 못한 경우
            return {
                'action': 'error',
                'message': '죄송합니다. 질문의 의도를 명확히 파악하지 못했습니다. 다시 질문해주세요.',
                'update_context': {}
            }

    def _handle_author_search_query(self, query: str, author_name: str, query_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """[신규] 작가명으로 정보를 검색하고 답변을 생성하는 워크플로우."""
        search_patterns = [
            f"{author_name} (작가)",
            f"{author_name} (소설가)",
            f"{author_name} (만화가)",
            author_name
        ]
        search_result = None
        final_author_name = None

        for pattern in search_patterns:
            temp_result = self.tool.search_page(pattern)
            if temp_result['success']:
                # [핵심 수정] 작가 검색에도 제목 유사도 검증 추가
                if self._is_title_similar(author_name, temp_result.get('title', '')):
                    if self._is_author_result(temp_result):
                        search_result = temp_result
                        final_author_name = temp_result.get('title', '').split('(')[0].strip()
                        break
        
        # 만약 위에서 못찾았으면, 괄호 없이 이름으로만 다시 검색
        if not search_result:
            temp_result = self.tool.search_page(author_name)
            if temp_result['success'] and self._is_author_result(temp_result):
                 if self._is_title_similar(author_name, temp_result.get('title', '')):
                    search_result = temp_result
                    final_author_name = temp_result.get('title', '').split('(')[0].strip()

        if not search_result:
            return {
                'action': 'ask_clarification',
                'message': self.prompt.get_search_failure_message(author_name),
                'update_context': {
                    'waiting_for_clarification': True,
                    'current_author': author_name
                }
            }

        if self._is_author_result(search_result):
            # LLM으로 자연스러운 답변 생성
            llm_answer = self._generate_llm_answer(query, search_result, final_author_name, intent_type='author_search')
            return {
                'action': 'show_result',
                'message': llm_answer,
                'update_context': {
                    'current_author': final_author_name,
                    'last_search_result': search_result,
                    'waiting_for_clarification': False,
                }
            }
        else:
            # [수정] 검색은 됐지만 작가가 아닌 경우, 명확한 메시지와 함께 에러 처리
            return {
                'action': 'error',
                'message': '도서/작가/출판사와 관련된 정보만 질문해주세요.',
                'update_context': {
                    'waiting_for_clarification': False,
                    'current_author': None,
                }
            }

    def _handle_clarification_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """[수정] 사용자가 대표작품을 제공한 후의 처리. LLM으로 사용자 의도 파악."""
        # 1. LLM을 사용하여 사용자 답변에서 책 제목과 작가명 추출
        parsed_info = self._parse_clarification_with_llm(query, context.get('current_author'))
        book_title = parsed_info.get('book_title')
        author_name = parsed_info.get('author_name', context.get('current_author'))

        # 2. 새로운 작가에 대한 질문이면, 컨텍스트를 리셋하고 새로운 검색 시작
        if parsed_info.get('is_new_query', False):
            result = self._fresh_search_flow(query, {})
            if 'update_context' not in result:
                result['update_context'] = {}
            result['update_context']['reset_conversation'] = True
            return result

        if not book_title or not author_name:
            return {
                'action': 'error',
                'message': self.prompt.get_ambiguous_query_message(),
                'update_context': {'waiting_for_clarification': True}
            }

        # 3. 추출된 정보로 검색 재시도
        search_patterns = self._generate_search_patterns(author_name, book_title)
        best_result = None
        for pattern in search_patterns:
            search_result = self.tool.search_page(pattern)
            if search_result['success'] and self._is_author_result(search_result):
                best_result = search_result
                break

        # 4. 결과 처리
        if best_result:
            return {
                'action': 'show_result',
                'message': self.prompt.format_author_response(best_result),
                'update_context': {
                    'waiting_for_clarification': False,
                    'current_author': author_name,
                    'last_search_result': best_result
                }
            }
        else:
            return {
                'action': 'ask_clarification',
                'message': self.prompt.get_combined_search_failure_message(author_name, book_title),
                'update_context': {
                    'waiting_for_clarification': True,
                    'current_author': author_name
                }
            }

    def _parse_clarification_with_llm(self, query: str, original_author: str) -> Dict[str, Any]:
        """LLM을 사용하여 사용자 명확화 답변을 파싱하는 함수."""
        if not self.llm_client:
            return {'book_title': query.strip()} # 폴백

        system_prompt = f"""당신은 사용자의 답변을 분석하여 책 제목과 작가명을 추출하는 AI입니다.
원래 질문했던 작가 이름은 '{original_author}'입니다.

사용자 답변을 분석하여 다음 JSON 형식으로 응답하세요:
{{
    "book_title": "추출된 책 제목",
    "author_name": "추출된 작가명(있을 경우)",
    "is_new_query": true/false
}}

추출 규칙:
- is_new_query: 사용자의 답변이 완전히 새로운 검색 요청(예: "그냥 다른 작가 알려줘")이면 true, 아니면 false.
- author_name: 사용자가 작가명을 명시하면(예: "베르나르 베르베르의 개미"), 해당 이름을 추출합니다. 명시하지 않으면 null을 반환합니다.
- book_title: 사용자가 말한 책 제목을 정확히 추출합니다.

예시:
- 사용자 답변: "책 제목이 개미야" -> {{"book_title": "개미", "author_name": null, "is_new_query": false}}
- 사용자 답변: "베르나르 베르베르가 쓴 개미" -> {{"book_title": "개미", "author_name": "베르나르 베르베르", "is_new_query": false}}
- 사용자 답변: "아니 그냥 김영하 작가 알려줘" -> {{"book_title": null, "author_name": "김영하", "is_new_query": true}}
"""
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"사용자 답변: {query}"}
                ],
                temperature=0.1,
                max_tokens=200
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {'book_title': query.strip()} # 예외 발생 시 폴백

    def _analyze_query_intent(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """쿼리 의도를 분석하여 적절한 처리 방식 결정 (LLM 기반)."""
        print(f"[DEBUG] LLM client available: {self.llm_client is not None}")
        if self.llm_client:
            try:
                result = self._llm_analyze_intent(query, context)
                print(f"[DEBUG] LLM analysis result: {result}")
                return result
            except Exception as e:
                print(f"[DEBUG] LLM analysis failed: {e}")
                return self._fallback_analyze_intent(query)
        else:
            print("[DEBUG] Using fallback analysis")
            return self._fallback_analyze_intent(query)
    
    def _llm_analyze_intent(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """LLM을 사용한 쿼리 의도 분석."""
        try:
            system_prompt = self.prompt.get_intent_analysis_prompt()
            user_prompt = self._format_intent_query(query, context)
            
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # WikiQueryIntent 모델 사용
            if result.get('intent_type') == 'book_to_author':
                intent = WikiQueryIntent.create_book_to_author(
                    query, result.get('extracted_keywords', [query])[0]
                )
            elif result.get('intent_type') == 'context_question':
                info_type = InfoType.GENERAL
                if result.get('specific_info_request'):
                    info_map = {
                        'university': InfoType.UNIVERSITY, 'birth': InfoType.BIRTH,
                        'death': InfoType.DEATH, 'school': InfoType.SCHOOL,
                        'works': InfoType.WORKS, 'awards': InfoType.AWARDS
                    }
                    info_type = info_map.get(result.get('specific_info_request'), InfoType.GENERAL)
                intent = WikiQueryIntent.create_context_question(query, info_type)
            else:
                intent = WikiQueryIntent.create_author_search(
                    query, result.get('extracted_keywords', [])
                )
            
            return intent.to_dict()
                
        except Exception as e:
            # LLM 실패시 폴백
            return self._fallback_analyze_intent(query)
    
    def _fallback_analyze_intent(self, query: str) -> Dict[str, Any]:
        """간단한 키워드 기반 의도 분석."""
        query_lower = query.lower()
        import re
        
        # 1. 작품명 + 저자 질문: "삼국지 저자", "희랍어시간 작가"
        if any(word in query_lower for word in ['저자', '작가', '지은이', '쓴 사람']):
            # 저자/작가 키워드 제거해서 작품명 추출
            book_title = query_lower
            for word in ['저자', '작가', '지은이', '쓴 사람', '누가', '정보', '는', '은', '의']:
                book_title = book_title.replace(word, '').strip()
            return WikiQueryIntent.create_book_to_author(query, book_title).to_dict()
        
        # 2. 작가명이 포함된 질문은 무조건 author_search로 처리
        # 한글 2-5글자 이름 패턴 찾기
        author_patterns = [
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)',  # 일반 한글 이름 (다자이 오사무 등)
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, query)  # 원본 쿼리에서 매칭
            if matches:
                # 가장 긴 매치를 작가명으로 간주
                author_name = max(matches, key=len).strip()
                # 일반적인 단어들 제외
                if author_name not in ['출생일', '사망일', '알려줘', '정보', '대해', '나이']:
                    return WikiQueryIntent.create_author_search(query, author_name).to_dict()
        
        # 3. 기본값: 전체 쿼리를 작가 검색으로 처리
        return WikiQueryIntent.create_author_search(query, query).to_dict()

    def _format_intent_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """LLM 의도 분석을 위한 쿼리 포맷."""
        prompt = f"사용자 질문: {query}\n\n"
        
        if context:
            if context.get('current_author'):
                prompt += f"현재 대화 주제: {context['current_author']} 작가\n"
            
            if context.get('waiting_for_clarification'):
                prompt += "상태: 사용자에게 추가 정보를 요청한 상태\n"
            
            if context.get('conversation_history'):
                recent_history = context['conversation_history'][-3:]
                prompt += "최근 대화 내용:\n"
                for item in recent_history:
                    role = "사용자" if item['role'] == 'user' else "AI"
                    prompt += f"- {role}: {item['message'][:80]}...\n"
        
        return prompt

    def _handle_book_to_author_query(self, book_title: str, query_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """[수정] 작품명으로 작가를 찾는 쿼리 처리. 제목 유사도 검증 추가."""
        
        search_patterns = [
            f"{book_title} (소설)",
            f"{book_title} (책)",
            book_title,
            f"{book_title} (문학)",
            f"{book_title} (작품)",
        ]
        
        # [수정] 띄어쓰기 없는 검색어를 위한 패턴 추가
        if ' ' not in book_title and len(book_title) > 2:
            # e.g., "희랍어시간" -> "희랍어 시간"
            for i in range(1, len(book_title)):
                spaced_title = book_title[:i] + ' ' + book_title[i:]
                search_patterns.insert(0, f"{spaced_title} (소설)")
                search_patterns.insert(1, spaced_title)

        search_result = None
        author_name = None
        
        for pattern in search_patterns:
            temp_result = self.tool.search_page(pattern)
            if temp_result['success']:
                # [핵심 수정] 검색된 제목과 원본 제목의 유사도 검증
                if self._is_title_similar(book_title, temp_result.get('title', '')):
                    search_result = temp_result
                    extracted_author = self._extract_author_with_llm(search_result)
                    if extracted_author:
                        author_name = extracted_author
                    break # 정확한 결과를 찾았으므로 루프 종료

        if search_result:
            # [수정] 구체적인 저자 정보 요청인지 확인 
            book_actual_title = search_result.get('title', book_title).split('(')[0].strip()
            
            # "저자" 키워드가 질문에 포함된 경우 간결한 답변
            if any(word in query.lower() for word in ['저자', '작가', '쓴 사람', '누가 썼', '지은이']):
                if author_name:
                    message = f"'{book_actual_title}'의 저자는 {author_name}입니다.\n\n**상세 정보**: {search_result.get('url', '').replace('(', '%28').replace(')', '%29')}"
                else:
                    message = f"'{book_actual_title}'의 저자 정보를 찾을 수 없습니다.\n\n**상세 정보**: {search_result.get('url', '').replace('(', '%28').replace(')', '%29')}"
            else:
                # 기존처럼 전체 요약 답변 생성
                message = self._generate_llm_answer(
                    query=book_title, 
                    search_result=search_result, 
                    author_name=author_name if author_name else book_title,
                    intent_type='book_to_author'
                )
            
            return {
                'action': 'show_result', 
                'message': message,
                'update_context': {
                    'current_author': author_name if author_name else book_title,
                    'last_search_result': search_result,
                    'waiting_for_clarification': False
                }
            }
        else:
            return {
                'action': 'error',
                'message': f"'{book_title}'에 대한 정보를 찾을 수 없습니다. 정확한 작품명이나 작가명을 알려주시겠어요?",
                'update_context': {
                    'waiting_for_clarification': False
                }
            }

    def _is_title_similar(self, query_title: str, result_title: str, threshold: float = 0.7) -> bool:
        """두 제목 간의 유사도를 계산하여 임계값 이상인지 확인."""
        # 간단한 유사도 계산: (긴 제목에서 겹치는 부분) / (긴 제목의 길이)
        query_norm = query_title.lower().replace(' ', '')
        result_norm = result_title.lower().replace(' ', '')
        
        if not query_norm or not result_norm:
            return False

        # 괄호 안의 내용(예: (소설))을 제거하여 핵심 제목만 비교
        import re
        result_core = re.sub(r'\(.*?\)', '', result_norm).strip()

        if query_norm in result_core or result_core in query_norm:
            return True
        
        # Jaccard 유사도와 유사한 방식
        s1 = set(query_norm)
        s2 = set(result_core)
        similarity = len(s1.intersection(s2)) / len(s1.union(s2))
        
        return similarity >= threshold

    def _handle_context_question(self, query: str, query_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """[재설계 4.0] 맥락 기반 질문 처리. 규칙 기반 키워드 매칭 우선 적용."""
        
        # 관련 없는 질문 필터링
        if self._is_irrelevant_query(query):
            return {
                'action': 'error',
                'message': "죄송합니다. 도서, 작가, 출판사에 대한 질문만 답변드릴 수 있습니다. 다른 질문을 해주세요.",
                'update_context': {}
            }
        
        author_name = context.get('current_author')
        last_search_result = context.get('last_search_result')

        if not author_name or not last_search_result:
            return {
                'action': 'error',
                'message': self.prompt.get_ambiguous_query_message(),
                'update_context': {}
            }

        # [핵심] LLM 분석보다 규칙 기반 키워드 매칭을 우선
        query_lower = query.lower()
        specific_request = None
        
        author_keywords = ['저자', '작가', '쓴 사람', '누가 썼', '지은이']
        family_keywords = ['아버지', '어머니', '가족', '부모']
        birth_keywords = ['출생', '태어', '나이']
        death_keywords = ['사망', '죽었', '별세']
        works_keywords = ['작품', '대표작', '책들']

        if any(keyword in query_lower for keyword in author_keywords):
            specific_request = 'author'
        elif any(keyword in query_lower for keyword in family_keywords):
            specific_request = 'family' # 세부 추출은 _extract_specific_answer가 담당
        elif any(keyword in query_lower for keyword in birth_keywords):
            specific_request = 'birth'
        elif any(keyword in query_lower for keyword in death_keywords):
            specific_request = 'death'
        elif any(keyword in query_lower for keyword in works_keywords):
            specific_request = 'works'

        # 규칙 기반으로 구체적 요청을 찾았을 경우
        if specific_request:
            if specific_request == 'author':
                book_title = last_search_result.get('title', '해당 작품').split('(')[0].strip()
                true_author = self._extract_author_with_llm(last_search_result)
                if true_author and true_author.lower() != 'none':
                    message = f"'{book_title}'의 저자는 {true_author}입니다."
                else:
                    message = f"'{book_title}'의 저자는 {author_name}입니다."
            else:
                message = self._extract_specific_answer(last_search_result, specific_request, author_name)
            
            return {
                'action': 'show_result',
                'message': message,
                'update_context': context
            }

        # 규칙으로 찾지 못한 일반적인 질문만 LLM으로 처리
        llm_answer = self._generate_llm_answer(
            query, 
            last_search_result, 
            author_name, 
            intent_type='context_question'
        )
        return {
            'action': 'show_result',
            'message': llm_answer,
            'update_context': context
        }


    def _parse_clarification_response(self, query: str) -> Dict[str, str]:
        """clarification 응답에서 작품명과 작가명을 파싱."""
        # 간단히 기존 방식으로 처리
        return {'author_name': query.strip()}

    def _extract_author_from_context_question(self, query: str) -> str:
        """컨텍스트 질문에서 작가명 추출."""
        return WikiTextProcessor.extract_author_from_context_question(query)

    def _search_author_automatically(self, author_name: str) -> Dict[str, Any]:
        """작가를 자동으로 검색."""
        # 기본 검색 시도 (동명이인 대비 여러 패턴)
        search_patterns = [
            f"{author_name} (작가)",
            f"{author_name} (소설가)",
            f"{author_name} (시인)",
            author_name
        ]
        
        for pattern in search_patterns:
            search_result = self.tool.search_page(pattern)
            if search_result['success'] and self._is_author_result(search_result):
                return search_result
        
        # 모든 패턴 실패시 마지막 시도
        return self.tool.search_page(author_name)

    def _extract_context_specific_answer(self, query: str, search_result: Dict[str, Any]) -> str:
        """컨텍스트 질문에 대한 구체적 답변 추출."""
        query_lower = query.lower()
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        title = search_result.get('title', '작가')
        url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
        
        # 대표작/작품 질문
        if any(word in query_lower for word in ['대표작', '작품', '소설', '책']):
            works_info = self._find_works_info(content)
            if works_info:
                return f"**{title}의 주요 작품:**\n{works_info}\n\n**상세 정보**: {url}"
            else:
                # 작품 정보가 명시적으로 없으면 내용에서 작품명 찾기
                import re
                work_mentions = re.findall(r'《([^》]+)》', content)
                if work_mentions:
                    # 중복 제거하면서 순서 유지
                    unique_works = []
                    for work in work_mentions:
                        if work not in unique_works:
                            unique_works.append(work)
                    formatted_works = '\n'.join([f"- {work}" for work in unique_works[:5]])
                    return f"**{title}의 작품들:**\n{formatted_works}\n\n**상세 정보**: {url}"
                else:
                    return f"{title}의 구체적인 작품 정보를 찾을 수 없습니다.\n\n**전체 정보**: {url}"
        
        # 대학/학력 질문
        elif any(word in query_lower for word in ['대학', '학교', '학력', '출신']):
            # 고등학교 vs 대학 구분
            if any(word in query_lower for word in ['고등학교', '고교', '중학교', '초등학교']):
                return self._extract_specific_answer(search_result, 'school', title.split('(')[0].strip())
            else:
                return self._extract_specific_answer(search_result, 'university', title.split('(')[0].strip())
        
        # 출생/나이 질문
        elif any(word in query_lower for word in ['출생', '나이', '태어', '언제']):
            return self._extract_specific_answer(search_result, 'birth', title.split('(')[0].strip())
        
        # 수상 경력
        elif any(word in query_lower for word in ['상', '수상', '받은', '경력']):
            return self._extract_specific_answer(search_result, 'awards', title.split('(')[0].strip())
        
        return None

    def _is_author_result(self, search_result: Dict[str, Any]) -> bool:
        """[수정] 검색 결과가 작가 정보인지 더 명확하게 판단."""
        if not search_result.get('success', False):
            return False

        summary = search_result.get('summary', '').lower()
        content = search_result.get('content', '').lower()
        
        # 1. 요약의 첫 문장에서 직업 확인 (가장 신뢰도 높음)
        # 마침표나 개행으로 첫 문장 분리
        first_sentence = summary.split('.')[0].split('\n')[0]
        
        primary_occupations = ['소설가', '작가', '시인', '만화가', '극작가', '저술가']
        if any(job in first_sentence for job in primary_occupations):
            return True
            
        # 2. '저서' 또는 '작품' 섹션 존재 여부 확인 (차선책)
        if '## 저서' in content or '## 작품' in content:
            return True

        # 3. 기존의 키워드 기반 로직 (최후의 보루)
        content_full = (search_result.get('title', '') + ' ' + summary + ' ' + content).lower()
        author_keywords = ['작가', '소설가', '시인', '저자', '만화가', '지은이', '쓴이']
        if any(keyword in content_full for keyword in author_keywords):
            return True

        return False

    def _is_new_author_query(self, query: str) -> bool:
        """새로운 작가에 대한 질문인지 판단."""
        # 작가 관련 질문 패턴 체크
        author_query_keywords = ['작가', '소설가', '시인', '에 대해', '알려줘', '정보', '누구']
        
        # 단순한 단어 한개는 작품명으로 간주
        if len(query.strip().split()) == 1 and not any(keyword in query for keyword in author_query_keywords):
            return False
            
        # 작가 관련 키워드가 있으면 새로운 질문으로 간주
        return any(keyword in query for keyword in author_query_keywords)

    def _generate_search_patterns(self, author_name: str, book_title: str) -> list:
        """작가명과 작품명을 조합한 검색 패턴들을 생성."""
        patterns = [
            "{} (작가)".format(author_name),        # 소설가용
            "{} (소설가)".format(author_name),      
            "{} (만화가)".format(author_name),      # 만화가용 추가
            "{} (시인)".format(author_name),        # 시인용 추가
            book_title,                            # 작품명 단독 검색 (작품 페이지에서 작가 정보 얻기)
            "{} {}".format(author_name, book_title),  # 조합 검색
            "{} 작가".format(author_name),         
            "{} 소설가".format(author_name),
            "{} 만화가".format(author_name),       # 만화가 추가
            author_name                            # 마지막 시도
        ]
        return patterns

    def _extract_specific_info_request(self, query: str) -> str:
        query_lower = query.lower()
        import re
        # 1. 학교 관련 분기 (가장 앞에)
        if any(word in query_lower for word in ['고등학교', '중학교', '초등학교']):
            return 'school'
        if any(word in query_lower for word in ['대학', '대학교', '학교', '출신']):
            return 'university'
        # 2. 가족/대표작 등
        if '아버지' in query_lower or '부친' in query_lower:
            return 'father'
        if '어머니' in query_lower or '모친' in query_lower:
            return 'mother'
        if '가족' in query_lower or '부모' in query_lower:
            return 'family'
        if '대표작품' in query_lower or '대표작' in query_lower or '작품' in query_lower:
            return 'works'
        # 출생과 사망을 모두 포함한 질문 (최우선)
        if re.search(r'(태어|출생)', query_lower) and re.search(r'(죽|사망)', query_lower):
            return 'birth_death'
        if '출생일' in query_lower and '사망일' in query_lower:
            return 'birth_death'
        # 사망 정보만
        if any(word in query_lower for word in ['죽었', '사망', '사혼', '언제 죽', '몇년에 죽', '언제 죽', '죽은', '사망일']):
            return 'death'
        # 출생 정보만
        if any(word in query_lower for word in ['출생', '태어', '나이', '출생일']) or ('언제' in query_lower and not any(death_word in query_lower for death_word in ['죽', '사망'])):
            return 'birth'
        if any(word in query_lower for word in ['수상', '상', '받은']):
            return 'awards'
        return None

    def _extract_specific_answer(self, search_result: Dict[str, Any], info_type: str, author_name: str) -> str:
        """검색 결과에서 특정 정보를 추출하여 답변 생성."""
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        title = author_name # [핵심 수정] 답변의 주어를 컨텍스트의 작가명으로 고정
        
        if info_type == 'school':
            # 고등학교 정보 추출
            school_info = self._find_school_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if school_info:
                # 조사 자동 선택 (을/를)
                particle = "을" if school_info[-1] in "라마바사아자차카타파하" else "를"
                
                # 졸업/입학 구분하여 답변
                if "졸업" in content:
                    action = "졸업했습니다"
                elif "입학" in content:
                    action = "다녔습니다"
                else:
                    action = "출신입니다"
                
                return "{}은(는) {}{} {}.\n\n**상세 정보**: {}".format(
                    title, school_info, particle, action, url
                )
            else:
                return "{}의 고등학교 정보는 위키피디아에서 확인할 수 없습니다.\n\n혹시 다른 학력 정보가 궁금하시면 '대학교'나 '학력' 등으로 질문해보세요.\n\n**전체 정보**: {}".format(
                    title, url
                )
        
        elif info_type == 'university':
            # 대학 정보 추출
            university_info = self._find_university_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            if university_info:
                # 대학교 졸업 여부 확인
                if "졸업" in content and university_info in content:
                    # 대학교 졸업한 경우
                    particle = "을" if university_info[-1] in "라마바사아자차카타파하" else "를"
                    return "{}은(는) {}{} 졸업했습니다.\n\n**상세 정보**: {}".format(
                        title, university_info, particle, url
                    )
                else:
                    # 대학교 졸업 안한 경우 → 고등학교가 최종학력
                    school_info = self._find_school_info(content)
                    if school_info:
                        particle = "을" if school_info[-1] in "라마바사아자차카타파하" else "를"
                        return "{}은(는) {}{} 졸업했습니다 (최종학력).\n\n**상세 정보**: {}".format(
                            title, school_info, particle, url
                        )
                    else:
                        return "{}의 학력 정보를 찾을 수 없습니다.\n\n**전체 정보**: {}".format(
                            title, url
                        )
            else:
                # 대학 정보 없으면 고등학교가 최종학력
                school_info = self._find_school_info(content)
                if school_info:
                    particle = "을" if school_info[-1] in "라마바사아자차카타파하" else "를"
                    return "{}은(는) {}{} 졸업했습니다 (최종학력).\n\n**상세 정보**: {}".format(
                        title, school_info, particle, url
                    )
                else:
                    return "{}의 대학교 정보는 위키피디아에서 확인할 수 없습니다.\n\n혹시 다른 학력 정보가 궁금하시면 '고등학교' 등으로 질문해보세요.\n\n**전체 정보**: {}".format(
                        title, url
                    )
        
        elif info_type == 'birth':
            # 출생 정보 추출
            birth_info = WikiInformationExtractor.find_birth_info(content, self.llm_client)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            if birth_info:
                return f"{title}은(는) {birth_info}에 태어났습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 출생 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
                
        elif info_type == 'death':
            # 사망 정보 추출
            death_info = WikiInformationExtractor.find_death_info(content, self.llm_client)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            if death_info:
                return f"{title}은(는) {death_info}에 사망했습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 사망 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        elif info_type == 'birth_death':
            # 출생과 사망 정보 모두 추출
            birth_info = WikiInformationExtractor.find_birth_info(content, self.llm_client)
            death_info = WikiInformationExtractor.find_death_info(content, self.llm_client)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            response = f"{title}은(는) "
            if birth_info:
                response += f"{birth_info}에 태어나 "
            if death_info:
                response += f"{death_info}에 사망했습니다."
            if not birth_info and not death_info:
                response += "출생과 사망 정보를 찾을 수 없습니다."
            elif birth_info and not death_info:
                response += "현재까지 생존해 있는 것으로 확인됩니다."
            response += f"\n\n**상세 정보**: {url}"
            return response
        
        elif info_type == 'works':
            # 작품 정보 추출
            works_list = WikiInformationExtractor.find_works_info(content, self.llm_client)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if works_list:
                works_info = '\n'.join([f"- {work}" for work in works_list])
                return f"{title}의 주요 작품:\n{works_info}\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 작품 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        elif info_type == 'awards':
            # 수상 정보 추출
            awards_list = WikiInformationExtractor.find_awards_info(content, self.llm_client)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if awards_list:
                awards_info = '\n'.join([f"- {award}" for award in awards_list])
                return f"{title}의 주요 수상 내역:\n{awards_info}\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 수상 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        elif info_type == 'father':
            # 아버지 정보 추출
            father_info = WikiInformationExtractor.find_father_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if father_info:
                return f"{title}의 아버지 이름은 {father_info}입니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 아버지 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        elif info_type == 'mother':
            # 어머니 정보 추출
            mother_info = WikiInformationExtractor.find_mother_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if mother_info:
                return f"{title}의 어머니 이름은 {mother_info}입니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 어머니 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        elif info_type == 'family':
            # 가족 정보 추출
            family_info = WikiInformationExtractor.find_enhanced_family_info(content, self.llm_client)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if family_info and (family_info.get('father') or family_info.get('mother') or family_info.get('siblings')):
                result_parts = []
                if family_info.get('father'):
                    result_parts.append(f"아버지: {family_info['father']}")
                if family_info.get('mother'):
                    result_parts.append(f"어머니: {family_info['mother']}")
                if family_info.get('siblings'):
                    sibling_names = [s['name'] for s in family_info['siblings']]
                    result_parts.append(f"형제자매: {', '.join(sibling_names)}")
                
                if result_parts:
                    return f"{title}의 가족 정보:\n" + "\n".join(result_parts) + f"\n\n**상세 정보**: {url}"
                else:
                    return f"{title}의 가족 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 가족 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        # [수정] 기본값: 전체 정보 반환 대신, 정보 찾기 실패 메시지 반환
        return f"'{author_name}'에 대한 요청하신 정보를 찾을 수 없습니다."

    def _find_university_info(self, content: str) -> str:
        """텍스트에서 대학교 정보 추출 - LLM 기반."""
        # LLM으로 먼저 시도
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 대학교 학력 정보를 추출하세요.

JSON 형식으로 응답:
{
    "university": "대학교명",
    "department": "학과명(있는 경우)",
    "degree": "학위(있는 경우)", 
    "found": true/false,
    "note": "추가 정보"
}

추출 규칙:
- 졸업, 진학, 입학한 대학교만 추출
- 교수로 재직하는 대학은 제외
- 정확한 대학교 이름 사용
- 정보가 없으면 found: false"""

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"텍스트: {content[:1200]}"}
                    ],
                    temperature=0.1,
                    max_tokens=200
                )
                
                result = json.loads(response.choices[0].message.content)
                if result.get('found') and result.get('university'):
                    return result['university']
                    
            except Exception as e:
                pass  # 폴백으로 진행
        
        # 폴백: 간단한 정규식
        return self._fallback_find_university(content)
    
    def _fallback_find_university(self, content: str) -> str:
        """폴백용 대학교 정보 추출."""
        import re
        
        # 간단한 패턴만 사용
        patterns = [
            r'([가-힣]+대학교?)\s*(?:졸업|진학|입학)',
            r'(?:졸업|진학|입학).*?([가-힣]+대학교?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                university = matches[0]
                if not university.endswith(('대학교', '대학')):
                    university += '대학교'
                return university
        
        return None

    def _find_birth_info(self, content: str) -> str:
        """텍스트에서 출생 정보 추출 - LLM 기반."""
        # LLM으로 먼저 시도
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 출생 정보를 추출하세요.

JSON 형식으로 응답:
{
    "birth_date": "출생일",
    "birth_year": "출생년도",
    "age_info": "나이 관련 정보",
    "found": true/false
}

추출 규칙:
- 출생일, 출생년도, 현재 나이 등 생년월일 관련 정보만 추출
- 정확한 날짜 형식으로 표시 (예: 1975년 8월 27일)
- 나이 계산이 가능한 경우 현재 나이도 포함
- 정보가 없으면 found: false"""

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"텍스트: {content[:2000]}"}
                    ],
                    temperature=0.1
                )
                
                result = json.loads(response.choices[0].message.content)
                
                if result.get('found'):
                    birth_date = result.get('birth_date', '')
                    # age_info = result.get('age_info', '')
                    # 나이 정보는 무시하고 날짜만 반환
                    if birth_date:
                        return birth_date
                
            except Exception as e:
                pass
        
        # LLM 실패시 정규식 폴백
        import re
        patterns = [
            r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',
            r'(\d{4}\.\s*\d{1,2}\.\s*\d{1,2})',
            r'(\d{4}년)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[0]
        
        return None

    def _find_death_info(self, content: str) -> str:
        """텍스트에서 사망 정보 추출 - LLM 기반."""
        # LLM으로 먼저 시도
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 사망 관련 정보를 추출하세요.

JSON 형식으로 응답:
{
    "death_date": "사망일",
    "death_year": "사망년도", 
    "death_cause": "사망원인",
    "death_age": "사망 당시 나이",
    "found": true/false
}

추출 규칙:
- 사망일, 사망년도, 사망원인, 사망 당시 나이 등 사망 관련 정보만 추출
- 정확한 날짜 형식으로 표시 (예: 1950년 1월 21일)
- 사망원인이 명시되어 있으면 포함
- 사망 당시 나이도 포함 가능하면 포함
- 정보가 없으면 found: false"""

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"텍스트: {content[:2000]}"}
                    ],
                    temperature=0.1
                )
                
                result = json.loads(response.choices[0].message.content)
                
                if result.get('found'):
                    death_date = result.get('death_date', '')
                    # death_cause = result.get('death_cause', '')
                    # death_age = result.get('death_age', '')
                    # 사망일만 반환
                    if death_date:
                        return death_date
                
            except Exception as e:
                pass
        
        # 폴백 처리 - 기존 regex 방식
        return self._fallback_find_death(content)

    def _fallback_find_death(self, content: str) -> str:
        """폴백용 사망 정보 추출."""
        import re
        
        # 사망 관련 패턴
        death_patterns = [
            r'~\s*(\d{4}년)',  # 233년 ~ 297년 같은 패턴
            r'(\d{4}년 \d{1,2}월 \d{1,2}일)에 사망',
            r'사망일은 (\d{4}년 \d{1,2}월 \d{1,2}일)',
            r'(\d{4}년 \d{1,2}월 \d{1,2}일) 세상을 떠났다',
            r'(\d{4}년)에 사망',
        ]
        
        for pattern in death_patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[0]
        
        return None

    def _find_school_info(self, content: str) -> str:
        """텍스트에서 고등학교 정보 추출 - LLM 기반."""
        # LLM으로 먼저 시도
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 고등학교 학력 정보를 추출하세요.

JSON 형식으로 응답:
{
    "school": "고등학교명",
    "found": true/false
}

추출 규칙:
- 고등학교, 중학교, 초등학교 정보만 추출
- 졸업, 진학, 입학한 학교만 추출
- 정확한 학교 이름 사용
- 정보가 없으면 found: false"""

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"텍스트: {content[:1200]}"}
                    ],
                    temperature=0.1,
                    max_tokens=150
                )
                
                result = json.loads(response.choices[0].message.content)
                if result.get('found') and result.get('school'):
                    return result['school']
                else:
                    pass
                    
            except Exception as e:
                pass  # 폴백으로 진행
        
        # 폴백: 간단한 정규식
        return self._fallback_find_school(content)
    
    def _fallback_find_school(self, content: str) -> str:
        """폴백용 고등학교 정보 추출."""
        import re
        
        # 간단한 패턴만 사용
        patterns = [
            r'([가-힣]+고등학교)\s*(?:졸업|진학|입학)',
            r'(?:졸업|진학|입학).*?([가-힣]+고등학교)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                return matches[0]
        
        return None

    def _find_works_info(self, content: str) -> str:
        """텍스트에서 작품 정보 추출 - LLM 기반."""
        # LLM으로 먼저 시도
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 작가의 주요 작품을 추출하세요.

JSON 형식으로 응답:
{
    "works": ["작품명1", "작품명2", "작품명3"],
    "found": true/false
}

추출 규칙:
- 소설, 시집, 에세이 등 모든 작품 포함
- 《》 따옴표는 제거하고 작품명만
- 대표작 우선으로 정렬
- 중복 제거
- 최대 6개까지"""

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"텍스트: {content[:1500]}"}
                    ],
                    temperature=0.1,
                    max_tokens=300
                )
                
                result = json.loads(response.choices[0].message.content)
                if result.get('found') and result.get('works'):
                    return '\n'.join(['- ' + work for work in result['works']])
                    
            except Exception as e:
                pass  # 폴백으로 진행
        
        # 폴백: 정규식 방식
        return self._fallback_find_works(content)
    
    def _fallback_find_works(self, content: str) -> str:
        """폴백용 작품 정보 추출."""
        import re
        
        # 《작품명》 패턴
        works = re.findall(r'《([^》]+)》', content)
        if works:
            # 중복 제거
            unique_works = []
            for work in works:
                if work not in unique_works:
                    unique_works.append(work)
            return '\n'.join(['- ' + work for work in unique_works[:5]])
        
        return None

    def _find_awards_info(self, content: str) -> str:
        """텍스트에서 수상 정보 추출 - LLM 기반."""
        # LLM으로 먼저 시도
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 수상내역을 추출하세요.

JSON 형식으로 응답:
{
    "awards": ["수상명1", "수상명2", "수상명3"],
    "found": true/false
}

추출 규칙:
- 문학상, 예술상, 대상 등 모든 상 포함
- 연도 정보가 있으면 포함 (예: "2016년 국제부커상")
- 정확한 상 이름만 추출
- 중복 제거
- 최대 7개까지"""

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"텍스트: {content[:1500]}"}  # 토큰 제한
                    ],
                    temperature=0.1,
                    max_tokens=300
                )
                
                result = json.loads(response.choices[0].message.content)
                if result.get('found') and result.get('awards'):
                    return '\n'.join(['- ' + award for award in result['awards']])
                    
            except Exception as e:
                pass  # 폴백으로 진행
        
        # 폴백: 정규식 방식
        return self._fallback_find_awards(content)
    
    def _fallback_find_awards(self, content: str) -> str:
        """폴백용 수상 정보 추출."""
        import re
        
        # 간단한 패턴만 사용
        award_patterns = [
            r'([가-힣\s]+(?:상|문학상|예술상|대상))[을를]?\s*(?:수상|받았)',
            r'(\d{4}년)\s*([가-힣\s]+(?:상|문학상|예술상|대상))',
        ]
        
        awards = []
        for pattern in award_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    award = ' '.join(match).strip()
                else:
                    award = match.strip()
                
                if award and len(award) > 3 and award not in awards:
                    awards.append(award)
        
        if awards:
            return '\n'.join(['- ' + award for award in awards[:5]])
        
        return None

    def _check_context_priority(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """대화 맥락을 우선적으로 확인하는 코드 레벨 로직."""
        
        # 1. 현재 작가가 설정되어 있는지 확인
        current_author = context.get('current_author')
        has_recent_conversation = bool(context.get('conversation_history'))
        
        # 2. 질문에 작가명이 포함되어 있는지 확인
        has_author_name = self._contains_author_name(query)
        
        # 3. 맥락 키워드 확인 (더 포괄적으로)
        context_keywords = [
            '나이', '대학', '고등학교', '학교', '작품', '대표작품', 
            '수상', '언제', '어디', '몇살', '학력', '졸업', '아버지', 
            '어머니', '가족', '부모', '사망', '죽었', '태어'
        ]
        has_context_keyword = any(keyword in query for keyword in context_keywords)
        
        # 4. 현재 작가와 질문 작가가 다른지 확인
        is_different_author = False
        if has_author_name and current_author:
            # 질문에서 작가명 추출
            query_author = self._extract_author_from_query(query)
            if query_author and query_author.lower() != current_author.lower():
                is_different_author = True
        
        # 5. 명시적으로 다른 작가를 언급한 경우 강제로 새로운 검색
        if has_author_name and current_author:
            query_author = self._extract_author_from_query(query)
            if query_author and query_author.lower() != current_author.lower():
                # 완전히 다른 작가에 대한 질문이므로 컨텍스트 사용 안 함
                return {
                    'should_use_context': False,
                    'current_author': current_author,
                    'has_author_name': has_author_name,
                    'has_context_keyword': has_context_keyword,
                    'is_different_author': True,
                    'reasoning': f"새로운 작가 질문 감지: {query_author} != {current_author}"
                }
        
        # 6. 우선순위 판단 로직 (더 정교하게)
        should_use_context = (
            current_author and  # 현재 작가가 설정되어 있고
            has_context_keyword and  # 맥락 키워드가 있고
            has_recent_conversation and  # 최근 대화가 있고
            not has_author_name  # 새로운 작가명이 없을 때만
        )
        
        return {
            'should_use_context': should_use_context,
            'current_author': current_author,
            'has_author_name': has_author_name,
            'has_context_keyword': has_context_keyword,
            'is_different_author': is_different_author,
            'reasoning': f"현재작가:{current_author}, 작가명포함:{has_author_name}, 맥락키워드:{has_context_keyword}, 다른작가:{is_different_author}"
        }
    
    def _contains_author_name(self, query: str) -> bool:
        """질문에 작가명(한글 2글자 이상, 띄어쓰기 포함, 영어 이름 등)이 포함되어 있는지 완화된 정규식으로 판별"""
        import re
        # 한글 2글자 이상(띄어쓰기 포함), 영어 이름(대소문자, 띄어쓰기 포함) 모두 허용
        # 예: '한강', '제인 오스틴', 'Agatha Christie', 'J. K. Rowling'
        return bool(re.search(r'([가-힣]{2,}(\s[가-힣]{2,})*|[A-Za-z]{2,}(\s[A-Za-z\.]{1,})*)', query))
    
    def _extract_author_from_query(self, query: str) -> str:
        """질문에서 작가명을 추출."""
        import re
        
        # 명시적 작가명 패턴 (더 정확하게)
        explicit_patterns = [
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)\s*(?:의|이|가|은|는)?\s*(?:출생|사망|태어|죽었|나이|대학|학교)',
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)\s*작가',  
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)\s*소설가',
        ]
        
        # 일본 작가명 패턴
        japanese_patterns = [
            r'(다자이\s*오사무|무라카미\s*하루키|요시모토\s*바나나)',
            r'([가-힣]{2,3}\s+[가-힣]{2,3})',  # "다자이 오사무" 형태
        ]
        
        # 먼저 명시적 패턴으로 찾기
        for pattern in explicit_patterns + japanese_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        # 일반적인 한글 이름 패턴 (2-5글자, 공백 포함)
        korean_matches = re.findall(r'[가-힣]{2,5}(?:\s[가-힣]{2,5})*', query)
        
        # 영어 이름 패턴
        english_matches = re.findall(r'[A-Za-z]{2,}(?:\s[A-Za-z\.]{1,})*', query)
        
        # 가장 긴 매치를 작가명으로 간주
        all_matches = korean_matches + english_matches
        if all_matches:
            # 일반적인 단어들은 제외
            filtered_matches = [m for m in all_matches if m not in ['출생일', '사망일', '알려줘', '정보', '대해']]
            if filtered_matches:
                return max(filtered_matches, key=len).strip()
        
        return None


    def _contains_author_info(self, search_result: Dict[str, Any]) -> bool:
        """검색 결과에 작가 정보가 포함되어 있는지 확인."""
        content = search_result.get('content', '') + search_result.get('summary', '')
        
        # 작가 관련 키워드 확인
        author_indicators = [
            '작가', '저자', '소설가', '시인', '문학가', '작품', '쓴', '지은', 
            '집필', '창작', '발표', '출간', '출판', '연재'
        ]
        
        return any(keyword in content for keyword in author_indicators)
    
    def _extract_author_from_work_page(self, search_result: Dict[str, Any]) -> str:
        """작품 페이지에서 작가명을 추출."""
        content = search_result.get('content', '') + search_result.get('summary', '')
        import re
        
        # 다양한 작가명 추출 패턴 (외국 작가명 포함)
        author_patterns = [
            r'([가-힣]{2,4}(?:\s+[가-힣]{2,4})?)\s*(?:이|가)\s*(?:쓴|지은|창작한|발표한)',  # "김영하가 쓴", "베르나르 베르베르가 쓴"
            r'(?:작가|저자|소설가)\s*([가-힣]{2,4}(?:\s+[가-힣]{2,4})?)',                # "작가 김영하", "작가 베르나르 베르베르"
            r'([가-힣]{2,4}(?:\s+[가-힣]{2,4})?)\s*(?:의|이)\s*(?:작품|소설|대표작)',     # "김영하의 작품"
            r'([가-힣]{2,4}(?:\s+[가-힣]{2,4})?)\s*\([^)]*(?:작가|소설가|시인)[^)]*\)',   # "김영하 (작가)"
            r'([A-Za-z]+\s+[A-Za-z]+)\s*(?:이|가)?\s*(?:쓴|지은|창작한)',              # "George Orwell이 쓴"
            r'([가-힣]+\s+[가-힣]+)\s*(?:이|가)?\s*(?:쓴|지은)',                        # "베르나르 베르베르가 쓴"
            r'([가-힣]+\s+[가-힣]+)의\s*(?:장편|추리|소설|작품)',               # "애거사 크리스티의 장편"
            r'([A-Za-z]+\s+[A-Za-z]+)의?\s*(?:장편|추리|소설|작품)',             # "Agatha Christie의 장편"
            r'([A-Za-z]+\s+[A-Za-z]+)\s*\([^)]*(?:작가|소설가|작가|소설가)[^)]*\)',     # "Agatha Christie (작가)"
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # 추출된 작가명에서 조사 제거
                author_name = matches[0].strip()
                # "의", "이", "가" 등 조사 제거
                author_name = re.sub(r'[의이가을를는]$', '', author_name)
                return author_name.strip()
        
        return None

    def _extract_author_with_llm(self, search_result: Dict[str, Any]) -> str:
        """[신규] LLM을 사용하여 작품 페이지에서 작가명을 추출."""
        if not self.llm_client:
            # LLM이 없으면 기존 폴백 메소드 사용
            return self._extract_author_from_work_page(search_result)

        try:
            content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
            
            system_prompt = """당신은 주어진 텍스트에서 작품의 원저자(원작자) 이름을 정확히 추출하는 AI입니다.

**CRITICAL: 번역가는 절대 저자가 아닙니다!**

추출 규칙:
- **번역가, 옮긴이, 역자, 영어로 번역한 사람은 절대 추출하지 마세요**
- **원작을 쓴 사람, 창작한 사람만 저자입니다**
- "번역했다", "옮겼다", "영어로 번역", "translated" 같은 표현이 있으면 그 사람은 번역가입니다
- 원저자의 이름만 정확히 추출하세요
- 여러 명의 원저자가 있을 경우만 쉼표로 구분하여 나열하세요
- "저자:", "작가:" 같은 부가적인 설명 없이 이름만 반환하세요
- 원저자가 언급되지 않았거나 찾을 수 없으면 "None"이라고만 응답하세요

예시:
- 입력: "...이 작품은 현진건에 의해 발표되었다..." -> 출력: 현진건
- 입력: "...한강이 쓴 소설을 데보라 스미스가 영어로 번역했다..." -> 출력: 한강
- 입력: "...데보라 스미스와 원 에밀리 애가 영어로 번역했다..." -> 출력: None (번역가만 언급됨)
- 입력: "...이 소설의 작가는 알려져 있지 않다..." -> 출력: None
"""
            user_prompt = f"다음 텍스트에서 이 작품의 저자(작가) 이름을 추출하세요:\n\n{content[:2500]}"

            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            author_name = response.choices[0].message.content.strip()
            
            if author_name.lower() == 'none':
                return None
            
            return author_name
            
        except Exception as e:
            # 예외 발생 시 폴백
            return self._extract_author_from_work_page(search_result)

    def _is_book_to_author_pattern(self, query: str) -> bool:
        """쿼리가 작품명→작가명 패턴인지 확인."""
        import re
        
        # 작품명→작가명 패턴들
        book_to_author_patterns = [
            r'.+\s+작가\s*(?:가|는|을|를)?\s*(?:누구|뭐)',      # "1984 작가 누구야"
            r'.+(?:을|를|은)?\s*(?:누가|누구가)\s*(?:쓴|썼)',  # "노르웨이의 숲은 누가 썼어"
            r'.+(?:을|를)?\s*쓴\s+(?:작가|사람)\s*(?:은|는|가|를)?\s*(?:누구|뭐)',          # "인간실격을 쓴 사람은 누구야"
            r'.+\s+쓴\s+(?:작가|사람)\s*(?:누구|뭐)',          # "화차 쓴 작가 누구야"
            r'.+\s+(?:저자|지은이)\s*(?:가|는|을|를)?\s*(?:누구|뭐)',  # "개미 저자 누구야"
        ]
        
        for pattern in book_to_author_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_book_title_from_query(self, query: str) -> str:
        """쿼리에서 작품명을 추출."""
        import re
        
        # 작품명 추출 패턴들 (구체적 패턴을 먼저 확인)
        extract_patterns = [
            r'(.+?)(?:을|를|은)?\s*(?:누가|누구가)\s*(?:쓴|썼)',     # "노르웨이의 숲은 누가 썼어" → "노르웨이의 숲"
            r'(.+?)(?:을|를)?\s*쓴\s+(?:작가|사람)\s*(?:은|는|가|를)?\s*(?:누구|뭐)',  # "인간실격을 쓴 사람은 누구야" → "인간실격"
            r'(.+?)\s+쓴\s+(?:작가|사람)\s*(?:가|는|을|를)?\s*(?:누구|뭐)',   # "화차 쓴 작가 누구야" → "화차"
            r'(.+?)\s+(?:저자|지은이)\s*(?:가|는|을|를)?\s*(?:누구|뭐)',      # "개미 저자 누구야" → "개미"
            r'(.+?)\s+작가\s*(?:가|는|을|를)?\s*(?:누구|뭐)',           # "1984 작가 누구야" → "1984"
        ]
        
        for pattern in extract_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                # 작품명 끝의 조사 제거
                extracted = re.sub(r'[은는이가을를의]$', '', extracted).strip()
                
                # "그리고"가 포함된 경우 스마트 처리
                if "그리고" in extracted:
                    extracted = self._handle_conjunction_in_title(extracted, query)
                
                return extracted
        
        return None

    def _handle_conjunction_in_title(self, extracted: str, original_query: str) -> str:
        """'그리고'가 포함된 작품명을 스마트하게 처리."""
        
        # "그리고"로 분리
        parts = extracted.split("그리고")
        
        if len(parts) == 2:
            first_part = parts[0].strip()
            second_part = parts[1].strip()
            
            # 1. "그리고"가 작품명의 일부인지 확인
            # - 첫 번째 부분이 비어있거나 매우 짧으면 작품명의 일부
            # - "그리고 아무도 없었다" 같은 경우
            if len(first_part) == 0 or (len(first_part) <= 2 and not first_part.isdigit()):
                return extracted
            
            # 2. 첫 번째 부분이 작품명으로 보이는 경우도 전체를 유지
            # - 길이가 적절하고 숫자가 아닌 경우 전체 제목일 가능성 높음
            if (2 <= len(first_part) <= 8 and 
                not first_part.isdigit() and
                not any(word in first_part for word in ['소설', '책', '작품', '시집', '영화'])):
                return extracted
            
            # 3. 두 개의 독립적인 항목으로 보이는 경우 (예: "1984 그리고 동물농장")
            # 첫 번째가 숫자나 명확한 작품명인 경우
            if first_part.isdigit() or len(first_part) > 8:
                return first_part
            else:
                return second_part
        
        # 분리가 제대로 되지 않은 경우 원본 반환
        return extracted

    def _generate_llm_answer(self, query: str, search_result: Dict[str, Any], author_name: str, intent_type: str = 'author_search') -> str:
        """[수정] LLM을 사용해서 자연스러운 답변 생성. 의도에 따라 프롬프트 분기."""
        if not self.llm_client:
            return self.prompt.format_author_response(search_result)
        
        try:
            content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            # [수정] 의도에 따라 시스템 프롬프트와 유저 프롬프트를 다르게 설정
            if intent_type == 'book_to_author':
                # 책 중심의 프롬프트
                system_prompt = self.prompt.get_book_summary_prompt()
                user_prompt = f"""사용자 질문: {query}

위키피디아 정보:
{content[:3000]}

위 정보를 바탕으로 책의 핵심 내용, 저자, 특징을 설명해주세요."""
            else:
                # 기존의 작가 중심 프롬프트
                system_prompt = self.prompt.get_author_summary_prompt()
                question_type = self._determine_question_type(query)
                user_prompt = f"""사용자 질문: {query}
작가명: {author_name}
질문 유형: {question_type}

위키피디아 정보:
{content[:3000]}

위의 정보를 바탕으로 질문 유형에 맞게 적절한 범위의 답변을 제공해주세요."""

            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            llm_answer = response.choices[0].message.content.strip()
            
            if "**상세 정보**" not in llm_answer:
                llm_answer += f"\n\n**상세 정보**: {url}"
            
            return llm_answer
            
        except Exception as e:
            return self.prompt.format_author_response(search_result)

    def _determine_question_type(self, query: str) -> str:
        """질문의 유형을 판단하는 헬퍼 함수."""
        query_lower = query.lower()
        if any(word in query_lower for word in ['부모', '아버지', '어머니', '가족', '형제', '자매', '자녀', '딸', '아들', '친척']):
            return "구체적 정보 질문 - 가족"
        elif any(word in query_lower for word in ['대표작', '작품', '소설', '책']):
            return "구체적 정보 질문 - 작품"
        elif any(word in query_lower for word in ['출생', '태어', '언제', '나이']):
            return "구체적 정보 질문 - 출생"
        elif any(word in query_lower for word in ['학력', '대학', '고등학교', '학교']):
            return "구체적 정보 질문 - 학력"
        else:
            return "기본 소개 질문"

    def _find_father_info(self, content: str) -> str:
        family_info = self._find_family_info(content)
        return family_info.get('father')

    def _find_mother_info(self, content: str) -> str:
        family_info = self._find_family_info(content)
        return family_info.get('mother')

    def _find_family_info(self, content: str) -> dict:
        """가족 정보 추출 - WikiInformationExtractor 사용"""
        return WikiInformationExtractor.find_enhanced_family_info(content, self.llm_client)
    
    def _is_irrelevant_query(self, query: str) -> bool:
        """질문이 도서/작가/출판사와 관련이 없는지 판단."""
        query_lower = query.lower().strip()
        
        # 완전히 관련 없는 표현들
        irrelevant_patterns = [
            '웃긴다', '웃기네', '웃겨', '재밌다', '재밌네', '재미있다',
            '안녕', '반가워', '고마워', '감사', '미안', '죄송',
            'ㅋㅋ', 'ㅎㅎ', '하하', '헤헤',
            '날씨', '시간', '뭐해', '어디', '어떻게',
            '좋다', '나쁘다', '싫다', '좋아해', '싫어해',
            '밥', '먹어', '마셔', '자자', '졸려',
            '몰라', '모르겠다', '뭐야', '왜',
            '너는', '당신은', '넌', '너'
        ]
        
        # 너무 짧은 질문 (3글자 이하이면서 의미있는 키워드가 없는 경우)
        if len(query_lower) <= 3 and not any(word in query_lower for word in ['작가', '책', '소설', '시', '작품']):
            return True
        
        # 관련 없는 패턴들
        for pattern in irrelevant_patterns:
            if pattern in query_lower:
                return True
        
        return False
    
    def _handle_compound_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """복합 질문을 처리하는 함수 (예: '박경리와 한강에 대해 각각 알려줘')"""
        # WikiInformationExtractor 사용
        compound_info = WikiInformationExtractor.detect_compound_query(query)
        
        if compound_info['is_compound']:
            subjects = compound_info['subjects']
            return self._process_compound_authors(subjects[0], subjects[1], context)
        
        return None
    
    def _process_compound_authors(self, author1: str, author2: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """두 작가 정보를 각각 검색하여 합성된 답변 생성"""
        results = []
        
        for author in [author1, author2]:
            # 각 작가별로 검색 수행
            author_result = self._handle_author_search_query(
                query=f"{author} 작가 정보", 
                author_name=author, 
                query_intent={'type': 'author_search', 'keywords': [author]}, 
                context={}
            )
            
            if author_result.get('action') == 'show_result':
                results.append(f"**{author}**\n{author_result['message']}")
            else:
                results.append(f"**{author}**\n{author}에 대한 정보를 찾을 수 없습니다.")
        
        # 결과 통합
        combined_message = "\n\n".join(results)
        
        return {
            'action': 'show_result',
            'message': combined_message,
            'update_context': {
                'compound_query': True,
                'authors': [author1, author2],
                'waiting_for_clarification': False
            }
        }
