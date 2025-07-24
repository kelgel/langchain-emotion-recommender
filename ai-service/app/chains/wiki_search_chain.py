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
        # 1. clarification(추가 정보 요청) 분기
        if context.get('waiting_for_clarification', False):
            return self._handle_clarification_response(query, context)
        # 2. 질문에 작가명이 있으면 무조건 fresh 검색 (context 무시)
        if self._contains_author_name(query):
            return self._fresh_search_flow(query, context)
        # 3. context(이전 작가 활용) 분기 (작가명 없을 때만)
        context_check = self._check_context_priority(query, context)
        if context_check['should_use_context']:
            return self._handle_context_question(query, context)
        # 4. 나머지(LLM intent 분석 등)도 fresh 검색
        return self._fresh_search_flow(query, context)

    def _fresh_search_flow(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """LLM intent 분석, fresh 검색, 답변 생성, context 갱신까지 한 번에 처리"""
        query_intent = self._analyze_query_intent(query, context)
        if query_intent['type'] == 'context_question':
            # context_question이어도 새로운 작가명이 키워드에 있으면 새로 검색
            if query_intent.get('extracted_keywords') and len(query_intent.get('extracted_keywords', [])) > 0:
                # 키워드에서 작가명을 찾았으니 새로운 검색으로 처리
                pass  # 아래로 계속 진행해서 author_search로 처리
            else:
                return self._handle_context_question(query, context)
        if query_intent['type'] == 'book_to_author':
            book_title = self._extract_book_title_from_query(query)
            if not book_title and query_intent.get('keywords'):
                book_title = query_intent['keywords'][0]
            if book_title:
                return self._handle_book_to_author_query(book_title, context)
        elif query_intent['type'] not in ['new_search', 'author_search']:
            if self._is_book_to_author_pattern(query):
                book_title = self._extract_book_title_from_query(query)
                if book_title:
                    return self._handle_book_to_author_query(book_title, context)
            return {
                'action': 'error',
                'message': '죄송합니다. 작가 정보 검색만 가능합니다. 작가에 대해 질문해주세요.',
                'update_context': {}
            }
        if self._is_book_to_author_pattern(query):
            book_title = self._extract_book_title_from_query(query)
            if book_title:
                return self._handle_book_to_author_query(book_title, context)
        if query_intent.get('keywords'):
            author_name = query_intent['keywords'][0]
        elif query_intent.get('extracted_keywords') and len(query_intent.get('extracted_keywords', [])) > 0:
            author_name = query_intent['extracted_keywords'][0]
        else:
            author_name = WikiTextProcessor.extract_author_name(query, self.llm_client)
        if not author_name:
            return {
                'action': 'error',
                'message': self.prompt.get_ambiguous_query_message(),
                'update_context': {}
            }
        search_patterns = [
            f"{author_name} (작가)",
            f"{author_name} (소설가)",
            f"{author_name} (만화가)",
            author_name
        ]
        search_result = None
        for pattern in search_patterns:
            temp_result = self.tool.search_page(pattern)
            if temp_result['success'] and self._is_author_result(temp_result):
                search_result = temp_result
                break
        if not search_result:
            search_result = self.tool.search_page(author_name)
        if not search_result['success']:
            return {
                'action': 'ask_clarification',
                'message': self.prompt.get_search_failure_message(author_name),
                'update_context': {
                    'waiting_for_clarification': True,
                    'current_author': author_name
                }
            }
        if self._is_author_result(search_result):
            llm_specific_info = query_intent.get('specific_info_request')
            fallback_specific_info = self._extract_specific_info_request(query)
            specific_info = fallback_specific_info if fallback_specific_info else llm_specific_info
            if specific_info:
                # LLM으로 자연스러운 답변 생성
                llm_answer = self._generate_llm_answer(query, search_result, author_name)
                return {
                    'action': 'show_result',
                    'message': llm_answer,
                    'update_context': {
                        'current_author': author_name,
                        'last_search_result': search_result
                    }
                }
            # LLM으로 자연스러운 답변 생성
            llm_answer = self._generate_llm_answer(query, search_result, author_name)
            return {
                'action': 'show_result',
                'message': llm_answer,
                'update_context': {
                    'current_author': author_name,
                    'last_search_result': search_result
                }
            }
        return {
            'action': 'ask_clarification',
            'message': self.prompt.get_clarification_request(author_name),
            'update_context': {
                'waiting_for_clarification': True,
                'current_author': author_name
            }
        }


    def _handle_clarification_response(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """사용자가 대표작품을 제공한 후의 처리."""
        # 새로운 작가 질문인지 체크
        if self._is_new_author_query(query):
            # 새로운 작가에 대한 질문 → fresh 검색으로 재처리 (컨텍스트 완전 초기화)
            result = self._fresh_search_flow(query, {})
            
            # Agent에게 컨텍스트를 완전히 리셋하라고 지시
            if 'update_context' not in result:
                result['update_context'] = {}
            result['update_context']['reset_conversation'] = True
            
            return result
        
        # "채식주의자 쓴 한강 말이야" 같은 패턴 파싱
        parsed_info = self._parse_clarification_response(query)
        book_title = parsed_info.get('book_title', query.strip())
        suggested_author = parsed_info.get('author_name')
        
        # 기존 컨텍스트에서 작가명 가져오기 
        original_author = context.get('current_author')
        
        # 새로운 작가명이 제시된 경우 업데이트
        author_name = suggested_author if suggested_author else original_author
        
        if not book_title or not author_name:
            return {
                'action': 'error',
                'message': self.prompt.get_ambiguous_query_message(),
                'update_context': {}
            }

        # 여러 검색 패턴으로 시도
        search_patterns = self._generate_search_patterns(author_name, book_title)
        best_result = None
        
        for pattern in search_patterns:
            search_result = self.tool.search_page(pattern)
            
            if search_result['success'] and self._is_author_result(search_result):
                best_result = search_result
                break

        # 결과 처리
        if best_result:
            # 성공: 작가 정보 반환
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
            # 엣지케이스: 조합 검색도 실패 → 다른 작품 요청
            return {
                'action': 'ask_clarification',
                'message': self.prompt.get_combined_search_failure_message(author_name, book_title),
                'update_context': {
                    'waiting_for_clarification': True,  # 계속 대기
                    'current_author': author_name
                }
            }

    def _analyze_query_intent(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """쿼리 의도를 분석하여 적절한 처리 방식 결정 (LLM 기반)."""
        if self.llm_client:
            return self._llm_analyze_intent(query, context)
        else:
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
        """기존 키워드 기반 의도 분석 (폴백용)."""
        query_lower = query.lower()
        
        # 작가 관련 키워드가 있는지 먼저 확인 (더 포괄적으로)
        author_keywords = [
            '작가', '소설가', '시인', '저자', '작품', '책', '소설',
            '누구', '알려줘', '정보', '말해줘', '설명', '소개',
            '에 대해', '이란', '라는', '인지', '인가', '예요', '이에요'
        ]
        has_author_keyword = any(word in query_lower for word in author_keywords)
        
        # 인명 패턴이 있는지도 확인 (한글 2-4글자 + 질문 패턴)
        import re
        name_question_patterns = [
            r'[가-힣]{2,4}(?:이|가)?\s*누구',  # "한강이 누구", "한강 누구"
            r'[가-힣]{2,4}(?:에|에게)?\s*대해',  # "한강에 대해"
            r'[가-힣]{2,4}(?:이|가)?\s*뭐',   # "한강이 뭐"
            r'[가-힣]{2,4}(?:을|를)?\s*알려',  # "한강을 알려"
            r'[가-힣]{2,4}(?:이|가)?\s*어떤',  # "한강이 어떤"
        ]
        
        has_name_question = any(re.search(pattern, query_lower) for pattern in name_question_patterns)
        
        # 작가 관련 키워드나 인명 질문 패턴이 없으면 처리 불가
        if not has_author_keyword and not has_name_question:
            return WikiQueryIntent.create_author_search(query, []).to_dict()
        
        # 복합 질문 우선 체크 (작가 + 세부정보)
        if any(word in query_lower for word in ['작가', '저자']) and \
           any(word in query_lower for word in ['대학', '출생', '나이', '언제', '어디']):
            return WikiQueryIntent.create_author_search(query, []).to_dict()
        
        # 단순 작품 -> 작가 질문 패턴  
        if any(word in query_lower for word in ['작가', '저자', '지은이', '쓴이', '쓴']) and \
           not any(word in query_lower for word in ['누구', '알려줘', '정보', '대학', '출생', '나이', '언제', '어디']):
            book_title = query_lower
            for word in ['작가', '누가', '저자', '지은이', '쓴이', '쓴', '정보', '누구야', '누구']:
                book_title = book_title.replace(word, '').strip()
            return WikiQueryIntent.create_book_to_author(query, book_title).to_dict()
        
        # 맥락 기반 질문 - 더 포괄적으로
        import re
        context_keywords = ['대학', '출생', '나이', '작품', '언제', '어디', '몇', '어떤', '고등학교', '중학교', '학교', '학력', '수상']
        context_patterns = [
            r'고등학교\s*어디',  # "고등학교 어디"
            r'대학\s*어디',     # "대학 어디" 
            r'어디\s*대학',     # "어디 대학"
            r'나이\s*몇',       # "나이 몇"
            r'언제\s*태어',     # "언제 태어"
            r'작품\s*뭐',       # "작품 뭐"
            r'수상\s*내역',     # "수상 내역"
            # 작가명이 없는 컨텍스트 질문만 포함
            r'^(?!.*[가-힣]{2,4}\s*)(?:고등학교|대학|나이|작품)',  # 작가명 없는 경우만
        ]
        
        # 작가명이 포함된 질문은 새로운 검색으로 처리
        author_in_query_patterns = [
            r'^[가-힣]{2,4}(?:은|는)?\s*어디',      # "이말년은 어디"
            r'^[가-힣]{2,4}\s+(?:고등학교|대학)',   # "이말년 고등학교"
        ]
        
        # 작가명이 포함된 질문인지 확인
        has_author_in_query = any(re.search(pattern, query_lower) for pattern in author_in_query_patterns)
        if has_author_in_query:
            return WikiQueryIntent.create_author_search(query, []).to_dict()
        
        # 패턴 매칭 또는 키워드 + 짧은 질문
        has_context_pattern = any(re.search(pattern, query_lower) for pattern in context_patterns)
        has_context_keyword = any(word in query_lower for word in context_keywords) and len(query.split()) <= 6
        
        if has_context_pattern or has_context_keyword:
            # 구체적인 정보 타입 결정
            info_type = InfoType.GENERAL
            if any(word in query_lower for word in ['대학', '대학교']):
                info_type = InfoType.UNIVERSITY
            elif any(word in query_lower for word in ['출생', '태어', '생일']):
                info_type = InfoType.BIRTH
            elif any(word in query_lower for word in ['학교', '고등학교', '중학교']):
                info_type = InfoType.SCHOOL
            elif any(word in query_lower for word in ['작품', '책', '소설']):
                info_type = InfoType.WORKS
            elif any(word in query_lower for word in ['수상', '상', '시상']):
                info_type = InfoType.AWARDS
                
            return WikiQueryIntent.create_context_question(query, info_type).to_dict()
        
        return WikiQueryIntent.create_author_search(query, []).to_dict()

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

    def _handle_book_to_author_query(self, book_title: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """작품명으로 작가를 찾는 쿼리 처리. 다양한 검색 패턴 시도."""
        
        # 다양한 검색 패턴으로 시도
        search_patterns = [
            book_title,                      # 원래 제목
            f"{book_title} (소설)",          # 소설 형태  
            f"{book_title} (책)",            # 책 형태
            f"{book_title} (문학)",          # 문학 형태
            f"{book_title} (작품)",          # 작품 형태
        ]
        
        # 띄어쓰기 변형 패턴도 추가 (한글의 경우)
        if len(book_title) > 2 and all(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in book_title if c.isalpha()):
            # 2글자씩 띄어쓰기 변형 추가
            spaced_title = ' '.join([book_title[i:i+2] for i in range(0, len(book_title), 2)])
            search_patterns.append(spaced_title)
            search_patterns.append(f"{spaced_title} (소설)")
            
            # 중간에 띄어쓰기 추가하는 변형
            if len(book_title) >= 4:
                mid_spaced = book_title[:2] + ' ' + book_title[2:]
                search_patterns.append(mid_spaced)
                search_patterns.append(f"{mid_spaced} (소설)")
        
        search_result = None
        successful_title = None
        
        for pattern in search_patterns:
            temp_result = self.tool.search_page(pattern)
            if temp_result['success']:
                # 작가 정보가 포함되어 있는지 확인
                has_author_info = self._contains_author_info(temp_result)
                if has_author_info:
                    search_result = temp_result
                    successful_title = pattern
                    break
        
        if search_result:
            # 검색 성공 - 작품 정보를 우선적으로 보여주기
            url = search_result.get('url', '')
            clickable_url = url.replace('(', '%28').replace(')', '%29')
            
            # 작가명 추출해서 메시지에 포함
            author_name = self._extract_author_from_work_page(search_result)
            
            # 작품 정보 포맷팅
            message = f"**{successful_title}**\n\n"
            
            if author_name:
                message += f"**작가**: {author_name}\n\n"
            
            message += f"**요약**: {search_result.get('summary', '')[:200]}...\n\n"
            message += f"**상세 정보**: {clickable_url}\n\n"
            message += "더 궁금한 것이 있으시면 언제든 물어보세요!"
            
            return {
                'action': 'show_result', 
                'message': message,
                'update_context': {
                    'current_author': author_name if author_name else book_title,
                    'last_search_result': search_result
                }
            }
        
        # 모든 패턴 실패시 폴백
        return {
            'action': 'ask_clarification',
            'message': "'{}'의 작가를 찾을 수 없습니다. 정확한 작품명을 알려주시겠어요?".format(book_title),
            'update_context': {
                'waiting_for_clarification': True,
                'current_author': None
            }
        }

    def _handle_context_question(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """맥락 기반 질문 처리: fallback info_type이 있으면 반드시 답변 생성"""
        # context에서 최근 검색 결과/작가명 활용
        search_result = context.get('last_search_result')
        author_name = context.get('current_author')
        if not search_result or not author_name:
            return {
                'action': 'error',
                'message': self.prompt.get_ambiguous_query_message(),
                'update_context': {}
            }
        # LLM으로 자연스러운 답변 생성
        llm_answer = self._generate_llm_answer(query, search_result, author_name)
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
        """검색 결과가 작가 정보인지 판단."""
        if not search_result.get('success', False):
            return False

        # 제목과 요약에서 작가 관련 키워드 검색
        content = (
            search_result.get('title', '') + ' ' + 
            search_result.get('summary', '') + ' ' + 
            search_result.get('content', '')
        ).lower()

        # 직접 작가 키워드
        direct_author_keywords = ['작가', '소설가', '시인', '저자', '만화가']
        if any(keyword in content for keyword in direct_author_keywords):
            return True
            
        # 작품 페이지에서 작가 정보 추출 (작품명으로 검색했을 때)
        work_indicators = ['웹툰', '소설', '만화', '시집', '연재', '출간', '발표']
        author_mentions = ['지은이', '쓴이', '작가', '저자', '글', '그린이']
        
        has_work = any(keyword in content for keyword in work_indicators)
        has_author_mention = any(keyword in content for keyword in author_mentions)
        
        return has_work and has_author_mention

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
        # 기존 분기 유지
        if re.search(r'(태어|출생)', query_lower) and re.search(r'(죽|사망)', query_lower):
            return 'birth_death'
        if any(word in query_lower for word in ['죽었', '사망', '사혼', '언제 죽', '몇년에 죽', '언제 죽', '죽은']):
            return 'death'
        if any(word in query_lower for word in ['출생', '태어', '나이']) or ('언제' in query_lower and not any(death_word in query_lower for death_word in ['죽', '사망'])):
            return 'birth'
        if any(word in query_lower for word in ['수상', '상', '받은']):
            return 'awards'
        return None

    def _extract_specific_answer(self, search_result: Dict[str, Any], info_type: str, author_name: str) -> str:
        """검색 결과에서 특정 정보를 추출하여 답변 생성."""
        content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
        title = search_result.get('title', author_name)
        
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
            birth_info = self._find_birth_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            # 디버깅
            
            if birth_info:
                return f"{title}은(는) {birth_info}에 태어났습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 출생 정보를 찾을 수 없습니다.\n\n**전체 정보**: {url}"
                
        elif info_type == 'death':
            # 사망 정보 추출
            death_info = self._find_death_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            # 디버깅
            
            if death_info:
                return f"{title}은(는) {death_info}에 사망했습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 사망 정보를 찾을 수 없습니다.\n\n**전체 정보**: {url}"
        
        elif info_type == 'birth_death':
            # 출생과 사망 정보 모두 추출
            birth_info = self._find_birth_info(content)
            death_info = self._find_death_info(content)
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
            works_info = self._find_works_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if works_info:
                return "{}의 주요 작품:\n{}\n\n**상세 정보**: {}".format(
                    title, works_info, url
                )
            else:
                return "{}의 작품 정보를 찾을 수 없습니다.\n\n**전체 정보**: {}".format(
                    title, url
                )
        
        elif info_type == 'awards':
            # 수상 정보 추출
            awards_info = self._find_awards_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if awards_info:
                return "{}의 주요 수상 내역:\n{}\n\n**상세 정보**: {}".format(
                    title, awards_info, url
                )
            else:
                return "{}의 수상 정보를 찾을 수 없습니다.\n\n**전체 정보**: {}".format(
                    title, url
                )
        
        elif info_type == 'father':
            # 아버지 정보 추출
            father_info = self._find_father_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if father_info:
                return f"{title}의 아버지 이름은 {father_info}입니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 아버지 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        elif info_type == 'mother':
            # 어머니 정보 추출
            mother_info = self._find_mother_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if mother_info:
                return f"{title}의 어머니 이름은 {mother_info}입니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 어머니 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        elif info_type == 'family':
            # 가족 정보 추출
            family_info = self._find_family_info(content)
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            if family_info and (family_info.get('father') or family_info.get('mother')):
                result_parts = []
                if family_info.get('father'):
                    result_parts.append(f"아버지: {family_info['father']}")
                if family_info.get('mother'):
                    result_parts.append(f"어머니: {family_info['mother']}")
                
                if result_parts:
                    return f"{title}의 가족 정보:\n" + "\n".join(result_parts) + f"\n\n**상세 정보**: {url}"
                else:
                    return f"{title}의 가족 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
            else:
                return f"{title}의 가족 정보를 찾을 수 없습니다.\n\n**상세 정보**: {url}"
        
        # 기본값: 전체 정보 반환
        return self.prompt.format_author_response(search_result)

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
            r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)[^\d]*?(?:사망|세상을 떠|타계|별세)',
            r'(\d{4}년)[^\d]*?(?:사망|세상을 떠|타계|별세)',
            r'(?:사망|세상을 떠|타계|별세)[^\d]*?(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',
            r'(?:사망|세상을 떠|타계|별세)[^\d]*?(\d{4}년)',
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
        
        # 3. 맥락 키워드 확인
        context_keywords = [
            '나이', '대학', '고등학교', '학교', '작품', '대표작품', 
            '수상', '언제', '어디', '몇살', '학력', '졸업'
        ]
        has_context_keyword = any(keyword in query for keyword in context_keywords)
        
        # 4. 우선순위 판단 로직
        should_use_context = (
            current_author and  # 현재 작가가 설정되어 있고
            not has_author_name and  # 질문에 새로운 작가명이 없고  
            has_context_keyword and  # 맥락 키워드가 있을 때
            has_recent_conversation  # 최근 대화가 있을 때
        )
        
        return {
            'should_use_context': should_use_context,
            'current_author': current_author,
            'has_author_name': has_author_name,
            'has_context_keyword': has_context_keyword,
            'reasoning': f"현재작가:{current_author}, 작가명포함:{has_author_name}, 맥락키워드:{has_context_keyword}"
        }
    
    def _contains_author_name(self, query: str) -> bool:
        """질문에 작가명(한글 2글자 이상, 띄어쓰기 포함, 영어 이름 등)이 포함되어 있는지 완화된 정규식으로 판별"""
        import re
        # 한글 2글자 이상(띄어쓰기 포함), 영어 이름(대소문자, 띄어쓰기 포함) 모두 허용
        # 예: '한강', '제인 오스틴', 'Agatha Christie', 'J. K. Rowling'
        return bool(re.search(r'([가-힣]{2,}(\s[가-힣]{2,})*|[A-Za-z]{2,}(\s[A-Za-z\.]{1,})*)', query))


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

    def _generate_llm_answer(self, query: str, search_result: Dict[str, Any], author_name: str) -> str:
        """LLM을 사용해서 자연스러운 답변 생성."""
        if not self.llm_client:
            # LLM 없으면 기본 포맷으로 폴백
            return self.prompt.format_author_response(search_result)
        
        try:
            content = search_result.get('content', '') + ' ' + search_result.get('summary', '')
            url = search_result.get('url', '').replace('(', '%28').replace(')', '%29')
            
            system_prompt = """당신은 위키피디아 정보를 바탕으로 사용자의 질문에 답변하는 AI입니다.

사용자의 질문 유형에 따라 적절한 범위의 정보를 제공하세요:

**1. 기본 소개 질문** ("OO 작가에 대해 알려줘", "OO 정보", "OO는 누구야?")
→ 위키피디아 첫 번째 문단(서머리)의 핵심 정보만 제공
→ 출생년도, 국적, 주요 업적, 대표작 위주
→ **중요: 부모, 가족 정보는 절대 포함하지 마세요**

**2. 구체적 정보 질문** ("부모님은?", "대표작은?", "언제 태어났어?")
→ 해당 질문에 직접 관련된 정보만 제공
→ 가족 정보를 명시적으로 물어봤을 때만 부모님 정보 제공
→ "A와 B 사이에서 태어났다", "소설가 X의 딸/아들" 패턴 인식

**답변 규칙:**
- 질문 유형에 따라 엄격하게 범위 제한
- 기본 소개에서는 부모/가족 정보 언급 금지
- 정보가 없으면 "찾을 수 없습니다"라고 솔직히 답변
- 자연스러운 한국어 사용
- 간결하고 명확하게 작성

**답변 예시:**
- 기본 소개: "홍성훈은 1945년 출생의 대한민국 아동문학가, 언론인, 연극인, 풍수지리가입니다."
- 가족 질문: "한강은 소설가 한승원의 딸입니다."
"""

            # 질문 유형 판단
            query_lower = query.lower()
            if any(word in query_lower for word in ['부모', '아버지', '어머니', '가족', '형제', '자매', '자녀', '딸', '아들', '친척']):
                question_type = "구체적 정보 질문 - 가족"
            elif any(word in query_lower for word in ['대표작', '작품', '소설', '책']):
                question_type = "구체적 정보 질문 - 작품"
            elif any(word in query_lower for word in ['출생', '태어', '언제', '나이']):
                question_type = "구체적 정보 질문 - 출생"
            elif any(word in query_lower for word in ['학력', '대학', '고등학교', '학교']):
                question_type = "구체적 정보 질문 - 학력"
            else:
                # 나머지는 모두 기본 소개 질문으로 처리
                # "홍성훈 정보", "한강 작가", "베르나르 베르베르는 누구야" 등
                question_type = "기본 소개 질문"

            user_prompt = f"""사용자 질문: {query}
작가명: {author_name}
질문 유형: {question_type}

위키피디아 정보:
{content[:2500]}

위의 정보를 바탕으로 질문 유형에 맞게 적절한 범위의 답변을 제공해주세요."""


            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            llm_answer = response.choices[0].message.content.strip()
            
            # URL이 없으면 추가
            if "**상세 정보**" not in llm_answer:
                llm_answer += f"\n\n**상세 정보**: {url}"
            
            return llm_answer
            
        except Exception as e:
            # LLM 실패시 폴백
            # 폴백: 기존 템플릿 방식
            return self.prompt.format_author_response(search_result)

    def _find_father_info(self, content: str) -> str:
        family_info = self._find_family_info(content)
        return family_info.get('father')

    def _find_mother_info(self, content: str) -> str:
        family_info = self._find_family_info(content)
        return family_info.get('mother')

    def _find_family_info(self, content: str) -> dict:
        import re

        result = {
            'father': None,
            'mother': None,
            'family': []
        }

        # 1. "A와 B 사이에서" 패턴 처리 (우선순위)
        birth_pattern = re.search(r'([가-힣A-Za-z\s]+)\s*와\s*(?:어머니\s*)?([가-힣A-Za-z\s]+)\s*사이에서\s*태어났다', content)
        if birth_pattern:
            father_candidate = birth_pattern.group(1).strip()
            mother_candidate = birth_pattern.group(2).strip()
            
            # 아버지 후보 검증 (30자 이하, 적절한 이름 형태)
            if len(father_candidate) <= 30 and not any(word in father_candidate for word in ['어머니', '사이에서', '태어났다']):
                result['father'] = father_candidate
                result['family'].append({'relation': 'father', 'name': father_candidate})
            
            # 어머니 후보 검증
            if len(mother_candidate) <= 30 and not any(word in mother_candidate for word in ['아버지', '사이에서', '태어났다']):
                result['mother'] = mother_candidate
                result['family'].append({'relation': 'mother', 'name': mother_candidate})

        # 2. "소설가 OO의 딸/아들" 패턴 처리
        if not result['father'] or not result['mother']:
            child_patterns = [
                r'(?:소설가|작가|시인)\s+([가-힣A-Za-z\s·\-]{2,10})\s*의\s+(딸|아들)',
                r'([가-힣A-Za-z\s·\-]{2,10})\s*의\s+(딸|아들)'
            ]
            
            for pattern in child_patterns:
                matches = re.findall(pattern, content)
                for parent_name, relation in matches:
                    parent_name = parent_name.strip()
                    parent_name = re.sub(r'^(소설가|작가|시인)\s*', '', parent_name).strip()
                    
                    if len(parent_name) >= 2 and len(parent_name) <= 10:
                        if not result['father']:
                            result['father'] = parent_name
                            result['family'].append({'relation': 'father', 'name': parent_name})
                        elif not result['mother'] and parent_name != result['father']:
                            result['mother'] = parent_name
                            result['family'].append({'relation': 'mother', 'name': parent_name})

        # 3. 명시적 "아버지" 키워드 패턴 (이미 찾지 못한 경우만)
        if not result['father']:
            match_father = re.search(r'아버지[\s:은는이가]*\s*([가-힣A-Za-z·\-]{2,10})(?=\s|$|,|\.|와|과)', content)
            if match_father:
                name = match_father.group(1).strip()
                # "생애" 같은 섹션 제목 제거
                if name not in ['생애', '개요', '경력', '작품', '수상']:
                    result['father'] = name
                    result['family'].append({'relation': 'father', 'name': name})

        # 4. 명시적 "어머니" 키워드 패턴 (이미 찾지 못한 경우만)
        if not result['mother']:
            match_mother = re.search(r'어머니[\s:은는이가]*\s*([가-힣A-Za-z·\-]{2,10})(?=\s|$|,|\.|와|과)', content)
            if match_mother:
                name = match_mother.group(1).strip()
                # "생애" 같은 섹션 제목 제거
                if name not in ['생애', '개요', '경력', '작품', '수상']:
                    result['mother'] = name
                    result['family'].append({'relation': 'mother', 'name': name})

        return result
