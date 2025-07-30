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

    def __init__(self, llm_client=None):
        """체인을 초기화하고 필요한 컴포넌트들을 설정."""
        self.tool = WikipediaSearchTool()
        self.prompt = WikiSearchPrompt()
        
        # LLM 클라이언트는 Agent에서 전달받음 (의존성 주입)
        self.llm_client = llm_client
        
        # 정보 추출기 import
        from wiki_information_extractor import WikiInformationExtractor

    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """메인 질의 처리 함수: clarification/context/fresh 검색 분기 명확화"""
        # print(f"[DEBUG] execute() 시작 - query: {query}")
        # print(f"[DEBUG] context: {context}")
        
        # 1. clarification(추가 정보 요청) 분기
        if context.get('waiting_for_clarification', False):
            # print("[DEBUG] clarification 분기")
            return self._handle_clarification_response(query, context)
        
        # 2. 복합 질문 처리 (최우선)
        compound_result = self._handle_compound_query(query, context)
        if compound_result:
            # print("[DEBUG] 복합 질문 처리")
            return compound_result
        
        # 3. context 체크를 먼저 수행 (더 정교한 우선순위)
        context_check = self._check_context_priority(query, context)
        # print(f"[DEBUG] context_check: {context_check}")
        if context_check['should_use_context']:
            # print("[DEBUG] context question 분기")
            # 컨텍스트 질문을 위한 기본 의도 생성
            query_intent = WikiQueryIntent.create_context_question(query, InfoType.GENERAL).to_dict()
            return self._handle_context_question(query, query_intent, context)
            
        # 4. 질문에 작가명이 있으면 fresh 검색
        contains_author = self._contains_author_name(query)
        # print(f"[DEBUG] contains_author_name: {contains_author}")
        if contains_author:
            # print("[DEBUG] fresh search (작가명 있음)")
            return self._fresh_search_flow(query, context)
            
        # 5. 나머지는 fresh 검색
        # print("[DEBUG] fresh search (기본)")
        return self._fresh_search_flow(query, context)

    def _fresh_search_flow(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """[수정됨] LLM intent 분석 결과를 기반으로 명확하게 워크플로우를 분기."""
        # print(f"[DEBUG] _fresh_search_flow() 시작 - query: {query}")
        
        # 관련 없는 질문 먼저 필터링
        if self._is_irrelevant_query(query):
            return {
                'action': 'error',
                'message': "죄송합니다. 도서, 작가, 출판사에 대한 질문만 답변드릴 수 있습니다. 다른 질문을 해주세요.",
                'update_context': {}
            }
        
        # 1. LLM으로 사용자 의도 분석 (이 결과를 유일한 진실로 간주)
        query_intent = self._analyze_query_intent(query, context)
        intent_type = query_intent.get('type')

        # 2. 의도에 따라 명확히 다른 핸들러 호출
        if intent_type == 'book_to_author':
            book_title = query_intent.get('book_title')
            if book_title:
                return self._handle_book_to_author_query(book_title, query_intent, context)
            else:
                return {
                    'action': 'error',
                    'message': '작품명을 정확히 파악하지 못했습니다. 더 명확하게 질문해주시겠어요?',
                    'update_context': {}
                }

        elif intent_type == 'author_search':
            keywords = query_intent.get('keywords', [])
            author_name = keywords[0] if keywords else None
            # print(f"[DEBUG] author_search - author_name: {author_name}")
            if author_name:
                return self._handle_author_search_query(query, author_name, query_intent, context)
            else:
                return {
                    'action': 'error',
                    'message': '작가명을 정확히 파악하지 못했습니다. 더 명확하게 질문해주시겠어요?',
                    'update_context': {}
                }

        elif intent_type == 'context_question':
            return self._handle_context_question(query, query_intent, context)

        else:
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
                if self._is_title_similar(author_name, temp_result.get('title', '')):
                    if self._is_author_result(temp_result):
                        search_result = temp_result
                        final_author_name = temp_result.get('title', '').split('(')[0].strip()
                        break
        
        if not search_result:
            temp_result = self.tool.search_page(author_name)
            if temp_result['success']:
                if self._is_author_result(temp_result):
                    if self._is_title_similar(author_name, temp_result.get('title', '')):
                        search_result = temp_result
                        final_author_name = temp_result.get('title', '').split('(')[0].strip()
                elif '다음 사람을 가리킨다' in temp_result.get('summary', ''):
                    return {
                        'action': 'ask_clarification',
                        'message': f"'{author_name}'에 대한 여러 인물이 있습니다. 찾으시는 분의 직업이나 대표작을 알려주시겠어요?",
                        'update_context': {
                            'waiting_for_clarification': True,
                            'current_author': author_name
                        }
                    }

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
            specific_info_type = self._extract_specific_info_request(query)
            # print(f"[DEBUG] specific_info_type: {specific_info_type}")
            
            if specific_info_type:
                # print(f"[DEBUG] 구체적 정보 추출 시작 - {specific_info_type}")
                response = self._extract_specific_answer(search_result, specific_info_type, final_author_name)
                # print(f"[DEBUG] 구체적 정보 추출 완료")
                return {
                    'action': 'show_result',
                    'message': response,
                    'update_context': {
                        'waiting_for_clarification': False,
                        'current_author': final_author_name,
                        'last_search_result': search_result
                    }
                }
            else:
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
        parsed_info = self._parse_clarification_with_llm(query, context.get('current_author'))
        book_title = parsed_info.get('book_title')
        author_name = parsed_info.get('author_name', context.get('current_author'))

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

        search_patterns = self._generate_search_patterns(author_name, book_title)
        best_result = None
        for pattern in search_patterns:
            search_result = self.tool.search_page(pattern)
            if search_result['success'] and self._is_author_result(search_result):
                best_result = search_result
                break

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
- 사용자 답변: "책 제목이 개미야" -> {{\"book_title\": \"개미\", \"author_name\": null, \"is_new_query\": false}}
- 사용자 답변: "베르나르 베르베르가 쓴 개미" -> {{\"book_title\": \"개미\", \"author_name\": \"베르나르 베르베르\", \"is_new_query\": false}}
- 사용자 답변: "아니 그냥 김영하 작가 알려줘" -> {{\"book_title\": null, \"author_name\": \"김영하\", \"is_new_query\": true}}
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
        # print(f"[DEBUG] LLM client available: {self.llm_client is not None}")
        if self.llm_client:
            try:
                result = self._llm_analyze_intent(query, context)
                # print(f"[DEBUG] LLM analysis result: {result}")
                return result
            except Exception as e:
                # print(f"[DEBUG] LLM analysis failed: {e}")
                return self._fallback_analyze_intent(query)
        else:
            # print("[DEBUG] Using fallback analysis")
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
            return self._fallback_analyze_intent(query)
    
    def _fallback_analyze_intent(self, query: str) -> Dict[str, Any]:
        """간단한 키워드 기반 의도 분석."""
        query_lower = query.lower()
        import re
        
        if any(word in query_lower for word in ['저자', '작가', '지은이', '쓴 사람']):
            book_title = query_lower
            for word in ['저자', '작가', '지은이', '쓴 사람', '누가', '정보', '는', '은', '의']:
                book_title = book_title.replace(word, '').strip()
            return WikiQueryIntent.create_book_to_author(query, book_title).to_dict()
        
        author_patterns = [
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)',
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, query)
            if matches:
                author_name = max(matches, key=len).strip()
                if author_name not in ['출생일', '사망일', '알려줘', '정보', '대해', '나이']:
                    return WikiQueryIntent.create_author_search(query, author_name).to_dict()
        
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
                    prompt += f"- {role}: {item['content'][:80]}...\n"
        
        return prompt

    def _handle_book_to_author_query(self, book_title: str, query_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """[개선] 작품명으로 작가를 찾는 쿼리 처리. 저자 추출 실패해도 작품 요약은 항상 보여줌."""
        search_patterns = [
            f"{book_title} (소설)",
            f"{book_title} (책)",
            book_title,
            f"{book_title} (문학)",
            f"{book_title} (작품)",
        ]
        if ' ' not in book_title and len(book_title) > 2:
            for i in range(1, len(book_title)):
                spaced_title = book_title[:i] + ' ' + book_title[i:]
                search_patterns.insert(0, f"{spaced_title} (소설)")
                search_patterns.insert(1, spaced_title)
        search_result = None
        author_name = None
        for pattern in search_patterns:
            temp_result = self.tool.search_page(pattern)
            if temp_result['success']:
                if self._is_title_similar(book_title, temp_result.get('title', '')):
                    search_result = temp_result
                    extracted_author = self._extract_author_with_llm(search_result)
                    if extracted_author:
                        author_name = extracted_author
                    break
        if search_result:
            book_actual_title = search_result.get('title', book_title).split('(')[0].strip()
            summary = search_result.get('summary', '')
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if author_name:
                message = f"**{book_actual_title}**\n\n**저자:** {author_name}\n\n**요약:** {summary}\n\n**상세 정보:** {url}"
            else:
                message = f"**{book_actual_title}**\n\n**저자 정보를 찾을 수 없습니다.**\n\n**요약:** {summary}\n\n**상세 정보:** {url}"
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

    def _is_title_similar(self, query_title: str, result_title: str, threshold: float = 0.5) -> bool:
        """두 제목 간의 유사도를 계산하여 임계값 이상인지 확인. (더 관대하게 완화)"""
        query_norm = query_title.lower().replace(' ', '')
        result_norm = result_title.lower().replace(' ', '')
        if not query_norm or not result_norm:
            return False
        import re
        result_core = re.sub(r'\(.*?\)', '', result_norm).strip()
        if query_norm in result_core or result_core in query_norm:
            return True
        return False

    def _handle_context_question(self, query: str, query_intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """[재설계 5.0] 맥락 기반 질문 처리. 안정성 강화 및 컨텍스트 누락 대응."""
        
        # 0. 관련 없는 질문 필터링
        if self._is_irrelevant_query(query):
            return {
                'action': 'error',
                'message': "죄송합니다. 도서, 작가, 출판사에 대한 질문만 답변드릴 수 있습니다.",
                'update_context': context
            }
        
        # 1. 컨텍스트에서 정보 추출 (필수)
        author_name = context.get('current_author')
        last_search_result = context.get('last_search_result')

        # 2. 컨텍스트 누락 시, 새로운 검색 시도
        if not author_name or not last_search_result:
            # 컨텍스트가 없으면, 이 질문을 새로운 검색으로 처리
            return self._fresh_search_flow(query, context)

        # 3. 구체적인 정보 요청 키워드 매칭
        query_lower = query.lower()
        specific_request = self._extract_specific_info_request(query_lower)

        # 4. 매칭된 키워드가 있으면, 정보 추출 시도
        if specific_request:
            message = self._extract_specific_answer(last_search_result, specific_request, author_name)
            return {
                'action': 'show_result',
                'message': message,
                'update_context': context  # 컨텍스트 유지
            }

        # 5. 구체적인 키워드가 없으면, LLM을 통해 일반적인 답변 생성
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
        return {'author_name': query.strip()}

    def _extract_author_from_context_question(self, query: str) -> str:
        return WikiTextProcessor.extract_author_from_context_question(query)

    def _search_author_automatically(self, author_name: str) -> Dict[str, Any]:
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
        
        return self.tool.search_page(author_name)

    def _extract_context_specific_answer(self, query: str, search_result: Dict[str, Any]) -> str:
        query_lower = query.lower()
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        title = search_result.get('title', '작가')
        url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
        
        if any(word in query_lower for word in ['대표작', '작품', '소설', '책']):
            works_info = WikiInformationExtractor.find_works_info(content, self.llm_client)
            if works_info:
                return f"**{title}의 주요 작품:**\n{works_info}\n\n**상세 정보**: {url}"
            else:
                import re
                work_mentions = re.findall(r'《([^》]+)》', content)
                if work_mentions:
                    unique_works = []
                    for work in work_mentions:
                        if work not in unique_works:
                            unique_works.append(work)
                    formatted_works = '\n'.join([f"- {work}" for work in unique_works[:5]])
                    return f"**{title}의 작품들:**\n{formatted_works}\n\n**상세 정보**: {url}"
                else:
                    return f"{title}의 구체적인 작품 정보를 찾을 수 없습니다.\n\n**전체 정보**: {url}"
        
        elif any(word in query_lower for word in ['대학', '학교', '학력', '출신']):
            if any(word in query_lower for word in ['고등학교', '고교', '중학교', '초등학교']):
                return self._extract_specific_answer(search_result, 'school', title.split('(')[0].strip())
            else:
                return self._extract_specific_answer(search_result, 'university', title.split('(')[0].strip())
        
        elif any(word in query_lower for word in ['출생', '나이', '태어', '언제']):
            return self._extract_specific_answer(search_result, 'birth', title.split('(')[0].strip())
        
        elif any(word in query_lower for word in ['상', '수상', '받은', '경력']):
            return self._extract_specific_answer(search_result, 'awards', title.split('(')[0].strip())
        
        return None

    def _is_author_result(self, search_result: Dict[str, Any]) -> bool:
        if not search_result.get('success', False):
            return False

        summary = search_result.get('summary', '').lower()
        content = search_result.get('content', '').lower()
        title = search_result.get('title', '').lower()
        
        if '다음 사람을 가리킨다' in summary:
            return False

        first_sentence = summary.split('.')[0]
        primary_occupations = ['소설가', '작가', '시인', '만화가', '극작가', '저술가']
        if any(job in first_sentence for job in primary_occupations):
            return True
        
        work_indicators = [
            '소설', '시집', '수필집', '작품', '책', '도서', 
            '장편소설', '단편소설', '연작소설', '수필', '시', '만화'
        ]
        if any(indicator in first_sentence for indicator in work_indicators):
            return True
            
        if any(indicator in title for indicator in ['(소설)', '(시집)', '(수필집)', '(작품)']):
            return True
            
        if '## 저서' in content or '## 작품' in content:
            return True

        content_full = (title + ' ' + summary + ' ' + content).lower()
        author_keywords = ['작가', '소설가', '시인', '저자', '만화가', '지은이', '쓴이']
        if any(keyword in content_full for keyword in author_keywords):
            return True

        return False

    def _is_new_author_query(self, query: str) -> bool:
        author_query_keywords = ['작가', '소설가', '시인', '에 대해', '알려줘', '정보', '누구', '누군데', '뭔데', '어떤 사람', '무엇', '어디서']
        
        import re
        if re.search(r'[가-힣A-Za-z\s]+[이은는]\s*(누구|뭔데|누군데|어떤|무엇)', query):
            return True
            
        if len(query.strip().split()) == 1 and not any(keyword in query for keyword in author_query_keywords):
            return False
            
        return any(keyword in query for keyword in author_query_keywords)

    def _generate_search_patterns(self, author_name: str, book_title: str) -> list:
        patterns = [
            f"{author_name} (작가)",
            f"{author_name} (소설가)",
            f"{author_name} (만화가)",
            f"{author_name} (시인)",
            book_title,
            f"{author_name} {book_title}",
            f"{author_name} 작가",
            f"{author_name} 소설가",
            f"{author_name} 만화가",
            author_name
        ]
        return patterns

    def _extract_specific_info_request(self, query: str) -> str:
        query_lower = query.lower()
        import re
        if any(word in query_lower for word in ['고등학교', '중학교', '초등학교']):
            return 'school'
        if any(word in query_lower for word in ['대학', '대학교', '학교', '출신']):
            return 'university'
        if '아버지' in query_lower or '부친' in query_lower:
            return 'father'
        if '어머니' in query_lower or '모친' in query_lower:
            return 'mother'
        if '가족' in query_lower or '부모' in query_lower:
            return 'family'
        if '대표작품' in query_lower or '대표작' in query_lower or '작품' in query_lower:
            return 'works'
        if re.search(r'(태어|출생)', query_lower) and re.search(r'(죽|사망)', query_lower):
            return 'birth_death'
        if '출생일' in query_lower and '사망일' in query_lower:
            return 'birth_death'
        if any(word in query_lower for word in ['죽었', '사망', '사혼', '언제 죽', '몇년에 죽', '언제 죽', '죽은', '사망일']):
            return 'death'
        if any(word in query_lower for word in ['출생', '태어', '나이', '출생일']) or ('언제' in query_lower and not any(death_word in query_lower for death_word in ['죽', '사망'])):
            return 'birth'
        if any(word in query_lower for word in ['수상', '상', '받은']):
            return 'awards'
        return None

    def _extract_specific_answer(self, search_result: Dict[str, Any], info_type: str, author_name: str) -> str:
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        title = author_name
        url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
        
        if info_type == 'school':
            school_info = WikiInformationExtractor.find_school_info(content, self.llm_client)
            if school_info:
                particle = "을" if school_info[-1] in "라마바사아자차카타파하" else "를"
                if "졸업" in content:
                    action = "졸업했습니다"
                elif "입학" in content:
                    action = "다녔습니다"
                else:
                    action = "출신입니다"
                return f"{title}은(는) {school_info}{particle} {action}.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 고등학교 정보는 위키피디아에서 확인할 수 없습니다.\n\n혹시 다른 학력 정보가 궁금하시면 '대학교'나 '학력' 등으로 질문해보세요.\n\n**전체 정보**: {url}"
        
        elif info_type == 'university':
            university_info = WikiInformationExtractor.find_university_info(content, self.llm_client)
            if university_info:
                if "졸업" in content and university_info in content:
                    particle = "을" if university_info[-1] in "라마바사아자차카타파하" else "를"
                    return f"{title}은(는) {university_info}{particle} 졸업했습니다.\n\n**상세 정보**: {url}"
                else:
                    school_info = WikiInformationExtractor.find_school_info(content, self.llm_client)
                    if school_info:
                        particle = "을" if school_info[-1] in "라마바사아자차카타파하" else "를"
                        return f"{title}은(는) {school_info}{particle} 졸업했습니다 (최종학력).\n\n**상세 정보**: {url}"
                    else:
                        return f"{title}의 학력 정보를 찾을 수 없습니다.\n\n**전체 정보**: {url}"
            else:
                school_info = self._find_school_info(content)
                if school_info:
                    particle = "을" if school_info[-1] in "라마바사아자차카타파하" else "를"
                    return f"{title}은(는) {school_info}{particle} 졸업했습니다 (최종학력).\n\n**상세 정보**: {url}"
                else:
                    return f"{title}의 대학교 정보는 위키피디아에서 확인할 수 없습니다.\n\n혹시 다른 학력 정보가 궁금하시면 '고등학교' 등으로 질문해보세요.\n\n**전체 정보**: {url}"
        
        elif info_type == 'birth':
            birth_info = WikiInformationExtractor.find_birth_info(content, self.llm_client)
            if birth_info:
                return f"{title}은(는) {birth_info}에 태어났습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 출생 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
                
        elif info_type == 'death':
            death_info = WikiInformationExtractor.find_death_info(content, self.llm_client)
            if death_info:
                return f"{title}은(는) {death_info}에 사망했습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 사망 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        elif info_type == 'birth_death':
            birth_info = WikiInformationExtractor.find_birth_info(content, self.llm_client)
            death_info = WikiInformationExtractor.find_death_info(content, self.llm_client)
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
            works_list = WikiInformationExtractor.find_works_info(content, self.llm_client)
            if works_list:
                works_info = '\n'.join([f"- {work}" for work in works_list])
                return f"{title}의 주요 작품:\n{works_info}\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 작품 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        elif info_type == 'awards':
            awards_list = WikiInformationExtractor.find_awards_info(content, self.llm_client)
            if awards_list:
                awards_info = '\n'.join([f"- {award}" for award in awards_list])
                return f"{title}의 주요 수상 내역:\n{awards_info}\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 수상 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        elif info_type == 'father':
            father_info = WikiInformationExtractor.find_father_info(content)
            if father_info:
                return f"{title}의 아버지 이름은 {father_info}입니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 아버지 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        elif info_type == 'mother':
            mother_info = WikiInformationExtractor.find_mother_info(content)
            if mother_info:
                return f"{title}의 어머니 이름은 {mother_info}입니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 어머니 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        elif info_type == 'spouse':
            spouse_info = WikiInformationExtractor.find_spouse_info(content)
            if spouse_info:
                return f"{title}의 배우자는 {spouse_info}입니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 배우자 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        elif info_type == 'family':
            try:
                family_info = WikiInformationExtractor.find_enhanced_family_info(content, self.llm_client)
                # print(f"[DEBUG] family_info 결과: {family_info}")
                result_parts = []
                has_family_info = False
                if family_info:
                    has_family_info = (family_info.get('father') or 
                                     family_info.get('mother') or 
                                     family_info.get('siblings') or 
                                     any(member.get('relation') == 'parent_unknown' for member in family_info.get('family', [])))
                
                if has_family_info:
                    if family_info.get('father'):
                        result_parts.append(f"아버지: {family_info['father']}")
                    if family_info.get('mother'):
                        result_parts.append(f"어머니: {family_info['mother']}")
                    if family_info.get('siblings'):
                        sibling_names = [s['name'] for s in family_info['siblings']]
                        result_parts.append(f"형제자매: {', '.join(sibling_names)}")
                    
                    known_parents = set()
                    if family_info.get('father'):
                        known_parents.add(family_info['father'])
                    if family_info.get('mother'):
                        known_parents.add(family_info['mother'])
                    
                    for family_member in family_info.get('family', []):
                        if (family_member.get('relation') == 'parent_unknown' and 
                            family_member['name'] not in known_parents):
                            result_parts.append(f"부모: {family_member['name']} (성별 불명)")
                    
                    # print(f"[DEBUG] result_parts: {result_parts}")
                
                if result_parts:
                    # print(f"[DEBUG] 구체적 정보 추출 완료")
                    return f"{title}의 가족 정보:\n" + "\n".join(result_parts) + f"\n\n**상세 정보**: {url}"
                else:
                    return f"{title}의 가족 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
                    
            except Exception as e:
                # print(f"[DEBUG] family 정보 추출 에러: {e}")
                import traceback
                traceback.print_exc()
                return f"{title}의 가족 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        return f"'{author_name}'에 대한 요청하신 정보를 찾을 수 없습니다."

    def _find_university_info(self, content: str) -> str:
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 대학교 학력 정보를 추출하세요.\n\nJSON 형식으로 응답:\n{\n    "university": "대학교명",\n    "department": "학과명(있는 경우)",\n    "degree": "학위(있는 경우)", \n    "found": true/false,\n    "note": "추가 정보"\n}\n\n추출 규칙:\n- 졸업, 진학, 입학한 대학교만 추출\n- 교수로 재직하는 대학은 제외\n- 정확한 대학교 이름 사용\n- 정보가 없으면 found: false"""

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
                pass
        
        return self._fallback_find_university(content)
    
    def _fallback_find_university(self, content: str) -> str:
        import re
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
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 출생 정보를 추출하세요.\n\nJSON 형식으로 응답:\n{\n    "birth_date": "출생일",\n    "birth_year": "출생년도",\n    "age_info": "나이 관련 정보",\n    "found": true/false\n}\n\n추출 규칙:\n- 출생일, 출생년도, 현재 나이 등 생년월일 관련 정보만 추출\n- 정확한 날짜 형식으로 표시 (예: 1975년 8월 27일)\n- 나이 계산이 가능한 경우 현재 나이도 포함\n- 정보가 없으면 found: false"""

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
                    if birth_date:
                        return birth_date
                
            except Exception as e:
                pass
        
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
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 사망 관련 정보를 추출하세요.\n\nJSON 형식으로 응답:\n{\n    "death_date": "사망일",\n    "death_year": "사망년도", \n    "death_cause": "사망원인",\n    "death_age": "사망 당시 나이",\n    "found": true/false\n}\n\n추출 규칙:\n- 사망일, 사망년도, 사망원인, 사망 당시 나이 등 사망 관련 정보만 추출\n- 정확한 날짜 형식으로 표시 (예: 1950년 1월 21일)\n- 사망원인이 명시되어 있으면 포함\n- 사망 당시 나이도 포함 가능하면 포함\n- 정보가 없으면 found: false"""

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
                    if death_date:
                        return death_date
                
            except Exception as e:
                pass
        
        return self._fallback_find_death(content)

    def _fallback_find_death(self, content: str) -> str:
        import re
        death_patterns = [
            r'~\s*(\d{4}년)',
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
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 고등학교 학력 정보를 추출하세요.\n\nJSON 형식으로 응답:\n{\n    "school": "고등학교명",\n    "found": true/false\n}\n\n추출 규칙:\n- 고등학교, 중학교, 초등학교 정보만 추출\n- 졸업, 진학, 입학한 학교만 추출\n- 정확한 학교 이름 사용\n- 정보가 없으면 found: false"""

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
                pass
        
        return self._fallback_find_school(content)
    
    def _fallback_find_school(self, content: str) -> str:
        import re
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
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 작가의 주요 작품을 추출하세요.\n\nJSON 형식으로 응답:\n{\n    "works": ["작품명1", "작품명2", "작품명3"],\n    "found": true/false\n}\n\n추출 규칙:\n- 소설, 시집, 에세이 등 모든 작품 포함\n- 《》 따옴표는 제거하고 작품명만\n- 대표작 우선으로 정렬\n- 중복 제거\n- 최대 6개까지"""

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
                pass
        
        return self._fallback_find_works(content)
    
    def _fallback_find_works(self, content: str) -> str:
        import re
        works = re.findall(r'《([^》]+)》', content)
        if works:
            unique_works = []
            for work in works:
                if work not in unique_works:
                    unique_works.append(work)
            return '\n'.join(['- ' + work for work in unique_works[:5]])
        
        return None

    def _find_awards_info(self, content: str) -> str:
        if self.llm_client:
            try:
                system_prompt = """주어진 텍스트에서 수상내역을 추출하세요.\n\nJSON 형식으로 응답:\n{\n    "awards": ["수상명1", "수상명2", "수상명3"],\n    "found": true/false\n}\n\n추출 규칙:\n- 문학상, 예술상, 대상 등 모든 상 포함\n- 연도 정보가 있으면 포함 (예: "2016년 국제부커상")\n- 정확한 상 이름만 추출\n- 중복 제거\n- 최대 7개까지"""

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
                if result.get('found') and result.get('awards'):
                    return '\n'.join(['- ' + award for award in result['awards']])
                    
            except Exception as e:
                pass
        
        return self._fallback_find_awards(content)
    
    def _fallback_find_awards(self, content: str) -> str:
        import re
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

    def _is_entity_in_last_response(self, query: str, context: Dict[str, Any]) -> bool:
        """질문 속 개체(이름)가 마지막 AI 응답에 포함되었는지 확인."""
        last_history = context.get('conversation_history', [])
        if not last_history or len(last_history) < 1:
            return False

        last_response = ""
        for msg in reversed(last_history):
            if msg.get('role') == 'assistant':
                last_response = msg.get('message', '')
                break
        
        if not last_response:
            return False

        query_author = self._extract_author_from_query(query)
        if query_author and query_author in last_response:
            return True
            
        return False

    def _check_context_priority(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """대화 맥락을 우선적으로 확인할지 결정하는 새로운 로직."""
        current_author = context.get('current_author')
        if not current_author:
            return {'should_use_context': False, 'reasoning': 'No current author in context.'}

        query_author = self._extract_author_from_query(query)

        # 1. 새로운 작가에 대한 명시적 질문인 경우 -> 컨텍스트 사용 안함
        if query_author and query_author.lower() != current_author.lower():
            if not self._is_entity_in_last_response(query, context):
                return {
                    'should_use_context': False,
                    'reasoning': f"New author detected: '{query_author}' is not '{current_author}' and not in last response."
                }

        # 2. 맥락을 이어가는 질문인지 키워드로 확인
        context_keywords = [
            '나이', '대학', '학교', '작품', '대표작', '수상', '언제', '어디',
            '학력', '졸업', '아버지', '어머니', '가족', '부모', '사망', '죽었',
            '태어', '그', '그의', '그녀', '아내', '남편', '배우자'
        ]
        has_context_keyword = any(keyword in query.lower() for keyword in context_keywords)

        # 3. 작가명 없이 맥락 키워드만 있거나, 이전 답변에 나온 인물에 대한 질문이면 -> 컨텍스트 사용
        if (has_context_keyword and not query_author) or self._is_entity_in_last_response(query, context):
            return {
                'should_use_context': True,
                'reasoning': f"Context keyword found or query is about an entity in the last response."
            }

        # 4. 위 모든 경우에 해당하지 않으면, 새로운 검색으로 처리
        return {'should_use_context': False, 'reasoning': 'Query does not seem to follow the context.'}
    
    def _contains_author_name(self, query: str) -> bool:
        """질문에 작가명(한글 2글자 이상, 띄어쓰기 포함, 영어 이름 등)이 포함되어 있는지 완화된 정규식으로 판별"""
        import re
        return bool(re.search(r'([가-힣]{2,}(\s[가-힣]{2,})*|[A-Za-z]{2,}(\s[A-Za-z\.]{1,})*)', query))
    
    def _extract_author_from_query(self, query: str) -> str:
        """질문에서 작가명을 추출."""
        import re
        
        explicit_patterns = [
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)\s*(?:의|이|가|은|는)?\s*(?:출생|사망|태어|죽었|나이|대학|학교|아버지|어머니|부모|가족)',
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)\s*작가',  
            r'([가-힣]{2,5}(?:\s[가-힣]{2,5})*)\s*소설가',
        ]
        
        japanese_patterns = [
            r'(다자이\s*오사무|무라카미\s*하루키|요시모토\s*바나나)',
            r'([가-힣]{2,3}\s+[가-힣]{2,3})',
        ]
        
        for pattern in explicit_patterns + japanese_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        korean_matches = re.findall(r'[가-힣]{2,5}(?:\s[가-힣]{2,5})*', query)
        english_matches = re.findall(r'[A-Za-z]{2,}(?:\s[A-Za-z\.]{1,})*', query)
        
        all_matches = korean_matches + english_matches
        if all_matches:
            filtered_matches = [m for m in all_matches if m not in ['출생일', '사망일', '알려줘', '정보', '대해']]
            if filtered_matches:
                return max(filtered_matches, key=len).strip()
        
        return None


    def _contains_author_info(self, search_result: Dict[str, Any]) -> bool:
        """검색 결과에 작가 정보가 포함되어 있는지 확인."""
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        
        author_indicators = [
            '작가', '저자', '소설가', '시인', '문학가', '작품', '쓴', '지은', 
            '집필', '창작', '발표', '출간', '출판', '연재'
        ]
        
        return any(keyword in content for keyword in author_indicators)
    
    def _extract_author_from_work_page(self, search_result: Dict[str, Any]) -> str:
        """작품 페이지에서 작가명 추출."""
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        
        import re
        author_patterns = [
            r'저자[:\s]*([가-힣A-Za-z\s]+)',
            r'작가[:\s]*([가-힣A-Za-z\s]+)',
            r'([가-힣A-Za-z\s]+)의\s*\d+년\s*[가-힣]*\s*소설',
            r'([가-힣A-Za-z\s]+)이\s*집필한',
            r'([가-힣A-Za-z\s]+)이\s*쓴',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content)
            if match:
                author_name = match.group(1).strip()
                if len(author_name) >= 2 and len(author_name) <= 10:
                    return author_name
        
        return None

    def _extract_author_with_llm(self, search_result: Dict[str, Any]) -> str:
        """[신규] LLM을 사용하여 작품 페이지에서 작가명을 추출."""
        if not self.llm_client:
            return self._extract_author_from_work_page(search_result)

        try:
            content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
            
            system_prompt = """당신은 주어진 텍스트에서 작품의 원저자(원작자) 이름을 정확히 추출하는 AI입니다.\n\n**CRITICAL: 번역가는 절대 저자가 아닙니다!**\n\n추출 규칙:\n- **번역가, 옮긴이, 역자, 영어로 번역한 사람은 절대 추출하지 마세요**\n- **원작을 쓴 사람, 창작한 사람만 저자입니다**\n- "번역했다", "옮겼다", "영어로 번역", "translated" 같은 표현이 있으면 그 사람은 번역가입니다\n- 원저자의 이름만 정확히 추출하세요\n- 여러 명의 원저자가 있을 경우만 쉼표로 구분하여 나열하세요\n- "저자:", "작가:" 같은 부가적인 설명 없이 이름만 반환하세요\n- 원저자가 언급되지 않았거나 찾을 수 없으면 "None"이라고만 응답하세요\n\n예시:\n- 입력: "...이 작품은 현진건에 의해 발표되었다..." -> 출력: 현진건\n- 입력: "...한강이 쓴 소설을 데보라 스미스가 영어로 번역했다..." -> 출력: 한강\n- 입력: "...데보라 스미스와 원 에밀리 애가 영어로 번역했다..." -> 출력: None (번역가만 언급됨)\n- 입력: "...이 소설의 작가는 알려져 있지 않다..." -> 출력: None\n"""
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
            return self._extract_author_from_work_page(search_result)

    def _is_book_to_author_pattern(self, query: str) -> bool:
        """쿼리가 작품명→작가명 패턴인지 확인."""
        import re
        
        book_to_author_patterns = [
            r'.+\s+작가\s*(?:가|는|을|를)?\s*(?:누구|뭐)',
            r'.+(?:을|를|은)?\s*(?:누가|누구가)\s*(?:쓴|썼)',
            r'.+(?:을|를)?\s*쓴\s+(?:작가|사람)\s*(?:은|는|가|를)?\s*(?:누구|뭐)',
            r'.+\s+쓴\s+(?:작가|사람)\s*(?:누구|뭐)',
            r'.+\s+(?:저자|지은이)\s*(?:가|는|을|를)?\s*(?:누구|뭐)',
        ]
        
        for pattern in book_to_author_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_book_title_from_query(self, query: str) -> str:
        """쿼리에서 작품명을 추출."""
        import re
        
        extract_patterns = [
            r'(.+?)(?:을|를|은)?\s*(?:누가|누구가)\s*(?:쓴|썼)',
            r'(.+?)(?:을|를)?\s*쓴\s+(?:작가|사람)\s*(?:은|는|가|를)?\s*(?:누구|뭐)',
            r'(.+?)\s+쓴\s+(?:작가|사람)\s*(?:가|는|을|를)?\s*(?:누구|뭐)',
            r'(.+?)\s+(?:저자|지은이)\s*(?:가|는|을|를)?\s*(?:누구|뭐)',
            r'(.+?)\s+작가\s*(?:가|는|을|를)?\s*(?:누구|뭐)',
        ]
        
        for pattern in extract_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                extracted = re.sub(r'[은는이가을를의]$', '', extracted).strip()
                
                if "그리고" in extracted:
                    extracted = self._handle_conjunction_in_title(extracted, query)
                
                return extracted
        
        return None

    def _handle_conjunction_in_title(self, extracted: str, original_query: str) -> str:
        """'그리고'가 포함된 작품명을 스마트하게 처리."""
        
        parts = extracted.split("그리고")
        
        if len(parts) == 2:
            first_part = parts[0].strip()
            second_part = parts[1].strip()
            
            if len(first_part) == 0 or (len(first_part) <= 2 and not first_part.isdigit()):
                return extracted
            
            if (2 <= len(first_part) <= 8 and 
                not first_part.isdigit() and
                not any(word in first_part for word in ['소설', '책', '작품', '시집', '영화'])):
                return extracted
            
            if first_part.isdigit() or len(first_part) > 8:
                return first_part
            else:
                return second_part
        
        return extracted

    def _generate_llm_answer(self, query: str, search_result: Dict[str, Any], author_name: str, intent_type: str = 'author_search') -> str:
        """[수정] LLM을 사용해서 자연스러운 답변 생성. 의도에 따라 프롬프트 분기."""
        if not self.llm_client:
            return self.prompt.format_author_response(search_result)
        
        try:
            content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            if intent_type == 'book_to_author':
                system_prompt = self.prompt.get_book_summary_prompt()
                user_prompt = f"""사용자 질문: {query}\n\n위키피디아 정보:\n{content[:3000]}\n\n위 정보를 바탕으로 책의 핵심 내용, 저자, 특징을 설명해주세요."""
            else:
                system_prompt = self.prompt.get_author_summary_prompt()
                question_type = self._determine_question_type(query)
                user_prompt = f"""사용자 질문: {query}\n작가명: {author_name}\n질문 유형: {question_type}\n\n위키피디아 정보:\n{content[:3000]}\n\n위의 정보를 바탕으로 질문 유형에 맞게 적절한 범위의 답변을 제공해주세요."""

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

        irrelevant_patterns = [
            '웃긴다', '웃기네', '웃겨', '재밌다', '재밌네', '재미있다',
            '안녕', '반가워', '고마워', '감사', '미안', '죄송',
            'ㅋㅋ', 'ㅎㅎ', '하하', '헤헤',
            '날씨', '뭐해', '어디', '어떻게',
            '좋다', '나쁘다', '싫다', '좋아해', '싫어해',
            '밥', '먹어', '마셔', '자자', '졸려',
            '몰라', '모르겠다', '뭐야', '왜',
            '너는', '당신은', '넌', '너'
        ]
        
        if len(query_lower) <= 3 and not any(word in query_lower for word in ['작가', '책', '소설', '시', '작품']):
            return True
        
        for pattern in irrelevant_patterns:
            if pattern in query_lower:
                if any(word in query_lower for word in ['쓴', '지은', '작가', '저자', '소설', '작품', '책', '정보']):
                    continue
                return True
        
        return False
    
    def _is_work_context(self, search_result: Dict[str, Any]) -> bool:
        """현재 컨텍스트가 작품인지 판단."""
        if not search_result or not search_result.get('success', False):
            return False
            
        title = search_result.get('title', '').lower()
        summary = search_result.get('summary', '').lower()
        
        work_indicators = ['소설', '시집', '수필집', '작품', '책', '도서', '장편소설', '단편소설']
        
        return any(indicator in title or indicator in summary for indicator in work_indicators)
    
    def _is_author_info_question(self, query: str) -> bool:
        """작가 정보에 대한 질문인지 판단."""
        author_info_keywords = [
            '아버지', '어머니', '부모', '가족', '출생', '태어', '사망', '죽었', 
            '배우자', '아내', '남편', '나이', '학교', '대학', '수상'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in author_info_keywords)
    
    def _extract_author_from_work_page(self, search_result: Dict[str, Any]) -> str:
        """작품 페이지에서 작가명 추출."""
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        
        import re
        author_patterns = [
            r'저자[:\s]*([가-힣A-Za-z\s]+)',
            r'작가[:\s]*([가-힣A-Za-z\s]+)',
            r'([가-힣A-Za-z\s]+)의\s*\d+년\s*[가-힣]*\s*소설',
            r'([가-힣A-Za-z\s]+)이\s*집필한',
            r'([가-힣A-Za-z\s]+)이\s*쓴',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content)
            if match:
                author_name = match.group(1).strip()
                if len(author_name) >= 2 and len(author_name) <= 10:
                    return author_name
        
        return None
    
    def _handle_compound_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """복합 질문을 처리하는 함수 (예: '박경리와 한강에 대해 각각 알려줘')"""
        compound_info = WikiInformationExtractor.detect_compound_query(query)
        
        if compound_info['is_compound']:
            subjects = compound_info['subjects']
            return self._process_compound_authors(subjects[0], subjects[1], context)
        
        return None
    
    def _process_compound_authors(self, author1: str, author2: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """두 작가 정보를 각각 검색하여 합성된 답변 생성"""
        results = []
        
        for author in [author1, author2]:
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