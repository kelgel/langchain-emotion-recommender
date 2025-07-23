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
        """
        위키피디아 검색 워크플로우를 실행.
        
        이 메서드는 모든 비즈니스 로직과 엣지케이스를 처리합니다:
        - 작가인지 판단
        - 동명이인 처리 
        - 언제 대표작을 물어볼지 결정
        - 검색 실패시 처리
        - 재검색 로직
        """
        try:
            # 컨텍스트 상태 확인 및 분기
            if context.get('waiting_for_clarification', False):
                return self._handle_clarification_response(query, context)
            else:
                return self._handle_initial_query(query, context)
                
        except Exception as e:
            return {
                'action': 'error',
                'message': self.prompt.get_general_error_message(),
                'update_context': {}
            }

    def _handle_initial_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        최초 작가 검색 쿼리를 처리.
        
        엣지케이스 처리:
        - 빈 쿼리
        - 작가명 추출 실패
        - 검색 결과 없음
        - 동명이인 (작가가 아닌 결과)
        """
        # 1단계: 새로운 작가명 언급 확인 (우선순위 최고)
        if self._is_new_author_mentioned(query, context):
            # 새로운 작가가 언급되면 맥락을 무시하고 새 검색
            pass  # LLM 분석으로 진행
        else:
            # 2단계: 대화 맥락 우선 확인 (코드 레벨)
            context_check = self._check_context_priority(query, context)
            if context_check['should_use_context']:
                return self._handle_context_question(query, context)
        
        # 3단계: 질문 의도 분석 (LLM 기반)
        query_intent = self._analyze_query_intent(query, context)
        
        # 디버깅 정보를 사용자에게 표시 (임시)
        debug_info = f"[분석] '{query}' → {query_intent.get('type', 'unknown')}"
        if query_intent.get('keywords'):
            debug_info += f" | 키워드: {query_intent['keywords']}"
        
        if query_intent['type'] == 'book_to_author':
            # "개미 작가", "개미 저자" -> 작품명으로 작가 검색
            return self._handle_book_to_author_query(query_intent['book_title'], context)
        elif query_intent['type'] == 'context_question':
            # "대학이 어디야" -> 이전 검색 결과 활용
            return self._handle_context_question(query, context)
        elif query_intent['type'] not in ['new_search', 'author_search']:
            # 작가 검색이 아닌 경우 에러 반환
            return {
                'action': 'error',
                'message': '죄송합니다. 작가 정보 검색만 가능합니다. 작가에 대해 질문해주세요.',
                'update_context': {}
            }
        
        # 2단계: 일반 작가 검색 (LLM으로 키워드 추출된 경우 활용)
        if query_intent.get('keywords'):
            author_name = query_intent['keywords'][0]  # 첫 번째 키워드를 작가명으로 사용
        else:
            author_name = self._extract_author_name(query)
        if not author_name:
            return {
                'action': 'error',
                'message': self.prompt.get_ambiguous_query_message(),
                'update_context': {}
            }

        # 기본 검색 시도 (동명이인 대비 여러 패턴)
        search_patterns = [
            "{} (작가)".format(author_name),      # 먼저 명확한 패턴 시도
            "{} (소설가)".format(author_name),
            "{} (만화가)".format(author_name),
            author_name                          # 마지막에 기본 검색
        ]
        
        search_result = None
        for pattern in search_patterns:
            temp_result = self.tool.search_page(pattern)
            if temp_result['success'] and self._is_author_result(temp_result):
                search_result = temp_result
                break
        
        # 모든 패턴 실패시 마지막 시도
        if not search_result:
            search_result = self.tool.search_page(author_name)
        
        if not search_result['success']:
            # 엣지케이스: 검색 실패 → 대표작 요청
            return {
                'action': 'ask_clarification',
                'message': self.prompt.get_search_failure_message(author_name),
                'update_context': {
                    'waiting_for_clarification': True,
                    'current_author': author_name
                }
            }

        # 검색 성공 → 작가인지 검증
        if self._is_author_result(search_result):
            # LLM에서 특정 정보 요청이 있는지 먼저 확인
            llm_specific_info = query_intent.get('specific_info_request')
            # 기존 방식도 확인 (폴백)
            fallback_specific_info = self._extract_specific_info_request(query)
            
            specific_info = llm_specific_info or fallback_specific_info
            
            if specific_info:
                # 특정 정보 추출하여 답변
                answer = self._extract_specific_answer(search_result, specific_info, author_name)
                return {
                    'action': 'show_result',
                    'message': f"{debug_info}\n\n{answer}",
                    'update_context': {
                        'current_author': author_name,
                        'last_search_result': search_result
                    }
                }
            
            # 일반 작가 정보 반환
            return {
                'action': 'show_result',
                'message': f"{debug_info}\n\n{self.prompt.format_author_response(search_result)}",
                'update_context': {
                    'current_author': author_name,
                    'last_search_result': search_result
                }
            }
        else:
            # 엣지케이스: 동명이인 (작가가 아님) → 대표작 요청
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
            # 새로운 작가에 대한 질문 → 초기 쿼리로 재처리 (컨텍스트 완전 초기화)
            result = self._handle_initial_query(query, {})
            
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
            print(f"[DEBUG] LLM 의도 분석 시작: '{query}'")
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
            print(f"[DEBUG] LLM 분석 결과: {result}")
            
            # 결과를 기존 형식에 맞게 변환
            if result.get('intent_type') == 'book_to_author':
                return {
                    'type': 'book_to_author', 
                    'book_title': result.get('extracted_keywords', [query])[0]
                }
            elif result.get('intent_type') == 'context_question':
                return {
                    'type': 'context_question',
                    'question': query,
                    'specific_info': result.get('specific_info_request')
                }
            else:
                return {
                    'type': 'author_search',
                    'query': query,
                    'specific_info': result.get('specific_info_request'),
                    'keywords': result.get('extracted_keywords', [])
                }
                
        except Exception as e:
            # LLM 실패 원인 디버깅
            print(f"[DEBUG] LLM 의도 분석 실패: {str(e)}")
            print(f"[DEBUG] API 클라이언트 상태: {self.llm_client}")
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
            return {'type': 'unknown', 'query': query}
        
        # 복합 질문 우선 체크 (작가 + 세부정보)
        if any(word in query_lower for word in ['작가', '저자']) and \
           any(word in query_lower for word in ['대학', '출생', '나이', '언제', '어디']):
            return {'type': 'new_search', 'query': query}
        
        # 단순 작품 -> 작가 질문 패턴  
        if any(word in query_lower for word in ['작가', '저자', '지은이', '쓴이']) and \
           not any(word in query_lower for word in ['누구', '알려줘', '정보', '대학', '출생', '나이', '언제', '어디']):
            book_title = query_lower
            for word in ['작가', '누가', '저자', '지은이', '쓴이', '정보']:
                book_title = book_title.replace(word, '').strip()
            return {'type': 'book_to_author', 'book_title': book_title}
        
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
            return {'type': 'new_search', 'query': query}
        
        # 패턴 매칭 또는 키워드 + 짧은 질문
        has_context_pattern = any(re.search(pattern, query_lower) for pattern in context_patterns)
        has_context_keyword = any(word in query_lower for word in context_keywords) and len(query.split()) <= 6
        
        if has_context_pattern or has_context_keyword:
            return {'type': 'context_question', 'question': query}
        
        return {'type': 'new_search', 'query': query}

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
        """작품명으로 작가를 찾는 쿼리 처리."""
        # 작품명으로 직접 검색
        search_result = self.tool.search_page(book_title)
        
        if search_result['success'] and self._is_author_result(search_result):
            return {
                'action': 'show_result',
                'message': self.prompt.format_author_response(search_result),
                'update_context': {
                    'current_author': book_title,
                    'last_search_result': search_result
                }
            }
        
        # 실패시 일반 검색으로 폴백
        return {
            'action': 'ask_clarification',
            'message': "'{}'의 작가를 찾을 수 없습니다. 정확한 작품명을 알려주시겠어요?".format(book_title),
            'update_context': {
                'waiting_for_clarification': True,
                'current_author': None
            }
        }

    def _handle_context_question(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """이전 검색 결과를 활용한 맥락 질문 처리."""
        last_result = context.get('last_search_result')
        
        if not last_result:
            # 컨텍스트가 없지만 질문에 작가명이 포함된 경우 자동 검색
            author_name = self._extract_author_from_context_question(query)
            if author_name:
                # 해당 작가를 먼저 검색
                search_result = self._search_author_automatically(author_name)
                if search_result and search_result.get('success'):
                    # 검색 성공 후 질문 처리
                    specific_answer = self._extract_context_specific_answer(query, search_result)
                    if specific_answer:
                        return {
                            'action': 'show_result',
                            'message': specific_answer,
                            'update_context': {
                                'current_author': author_name,
                                'last_search_result': search_result
                            }
                        }
            
            return {
                'action': 'error', 
                'message': '먼저 작가를 검색해주세요. 예: "한강 작가 알려줘"',
                'update_context': {}
            }
        
        # 질문 유형에 따른 구체적 답변 생성
        specific_answer = self._extract_context_specific_answer(query, last_result)
        
        # 디버깅: 왜 구체적 답변을 찾지 못했는지 확인
        if not specific_answer:
            print(f"[DEBUG] 구체적 답변 찾기 실패: '{query}'")
            print(f"[DEBUG] 검색 결과 일부: {last_result.get('content', '')[:200]}...")
        
        if specific_answer:
            return {
                'action': 'show_result',
                'message': specific_answer,
                'update_context': context
            }
        else:
            # 구체적 답변을 찾지 못한 경우 전체 정보 반환
            answer = "이전에 검색한 {}의 정보를 다시 보여드리겠습니다.".format(
                last_result.get('title', '작가')
            )
            return {
                'action': 'show_result',
                'message': answer + "\n\n" + self.prompt.format_author_response(last_result),
                'update_context': context
            }

    def _extract_author_name(self, query: str) -> str:
        """쿼리에서 작가명을 추출 - 개선된 방식."""
        import re
        
        # 먼저 LLM으로 시도
        if self.llm_client:
            try:
                system_prompt = """사용자 질문에서 작가명만 추출하세요.

JSON 형식으로 응답:
{
    "author_name": "추출된 작가명",
    "confidence": 0.0-1.0
}

예시:
"한강이 누구야" -> {"author_name": "한강", "confidence": 0.9}
"무라카미 하루키 작가 알려줘" -> {"author_name": "무라카미 하루키", "confidence": 0.95}
"개미 쓴 작가 누구야" -> {"author_name": null, "confidence": 0.1}"""

                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1,
                    max_tokens=100
                )
                
                result = json.loads(response.choices[0].message.content)
                if result.get('author_name') and result.get('confidence', 0) > 0.7:
                    return result['author_name']
                    
            except Exception as e:
                pass  # 폴백으로 진행
        
        # 폴백: 기존 방식
        return self._fallback_extract_author_name(query)
    
    def _fallback_extract_author_name(self, query: str) -> str:
        """폴백용 작가명 추출."""
        import re
        
        # 1단계: "X가/이 누구야" 패턴 우선 처리 - 조사를 명확히 분리
        who_patterns = [
            r'^([가-힣]{2,4})가\s*누구',     # "한강가 누구" - "가" 조사
            r'^([가-힣]{2,4})이\s*누구',     # "한강이 누구" - "이" 조사  
            r'^([가-힣]{2,4})\s+누구',       # "한강 누구" - 조사 없음
        ]
        
        for pattern in who_patterns:
            match = re.match(pattern, query.strip())
            if match:
                return match.group(1)
        
        # 2단계: 외국 이름 우선 추출 (띄어쓰기 포함)
        foreign_patterns = [
            r'^([A-Za-z]+\s+[A-Za-z]+)',  # "무라카미 하루키"
            r'^([가-힣]+\s+[가-힣]+)',    # "무라카미 하루키" (한글 표기)
        ]
        
        for pattern in foreign_patterns:
            match = re.match(pattern, query.strip())
            if match:
                return match.group(1).strip()
        
        # 3단계: 한글 이름 (2-4글자) - 질문 단어가 없는 경우만
        if not any(word in query for word in ['누구', '뭐', '어떤', '언제', '어디', '알려줘']):
            korean_match = re.match(r'^([가-힣]{2,4})', query.strip())
            if korean_match:
                return korean_match.group(1)
        
        # 4단계: 키워드 제거 방식 (폴백)
        safe_keywords = [
            '어디', '언제', '몇', '어떤', '누구', '나이',
            '대학', '대학교', '학교', '고등학교', '중학교', '초등학교',
            '출신', '졸업', '나옴', '나왔', '다녔', '공부했',
            '작가', '소설가', '시인', '저자', '정보', '알려줘', '말해줘',
            '?', '!', '.', '은', '는', '이', '가', '야'
        ]
        
        cleaned = query.strip()
        for keyword in safe_keywords:
            cleaned = cleaned.replace(keyword, ' ')
        
        cleaned = ' '.join(cleaned.split()).strip()
        return cleaned if cleaned else None

    def _parse_clarification_response(self, query: str) -> Dict[str, str]:
        """clarification 응답에서 작품명과 작가명을 파싱."""
        import re
        
        # "작품명 쓴 작가명" 패턴들 - 더 포괄적으로
        patterns = [
            r'^(.+?)\s+쓴\s+([가-힣]{2,4})\s*말이야',        # "채식주의자 쓴 한강 말이야"
            r'^(.+?)\s+쓴\s+([가-힣\s]+)\s*말이야',          # "개미 쓴 베르나르 베르베르 말이야"  
            r'^(.+?)\s+쓴\s+([가-힣]{2,4})',                # "채식주의자 쓴 한강"
            r'^(.+?)\s+쓴\s+([가-힣\s]+)',                  # "개미 쓴 베르나르 베르베르"
            r'^(.+?)\s+(?:작가|저자)\s+([가-힣]{2,4})',      # "채식주의자 작가 한강"
            r'^(.+?)(?:라는|이라는)\s+(?:작품|소설|책)\s+쓴\s+([가-힣\s]+)',  # "개미라는 작품 쓴 베르나르 베르베르"
            r'^(.+?)(?:라는|이라는)?\s*(?:책|소설|작품)?\s*썼다고?\s*했는데',  # "혼모노라는 책 썼다고 했는데"
            r'^(.+?)\s*썼다고?\s*했는데',                    # "혼모노 썼다고 했는데"
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.match(pattern, query.strip())
            if match:
                book_title = match.group(1).strip()
                
                # 마지막 두 패턴("썼다고 했는데")은 작가명이 없음
                if i >= 6:  # "썼다고 했는데" 패턴들
                    author_name = None
                else:
                    author_name = match.group(2).strip() if len(match.groups()) > 1 else None
                
                # 작품명에서 따옴표나 불필요한 문자 제거
                book_title = book_title.replace('"', '').replace("'", '')
                
                return {
                    'book_title': book_title,
                    'author_name': author_name
                }
        
        # 패턴 매칭 실패시 전체를 작품명으로 처리
        return {
            'book_title': query.strip(),
            'author_name': None
        }

    def _extract_author_from_context_question(self, query: str) -> str:
        """컨텍스트 질문에서 작가명 추출."""
        import re
        
        # "한강 고등학교", "한강 대학" 등의 패턴
        patterns = [
            r'^([가-힣]{2,4})\s+(?:고등학교|대학|학교|학력)',
            r'^([가-힣]{2,4})\s+(?:나이|출생|작품|수상)',  
            r'^([가-힣\s]+)\s+(?:고등학교|대학|학교|학력)',  # 긴 이름 대응
            r'^([가-힣]{2,4})(?:은|는)?\s*어디\s*(?:학교|대학|고등학교)',  # "이말년은 어디 학교"
            r'^([가-힣]{2,4})\s*어디\s*(?:학교|대학|고등학교)',  # "이말년 어디 학교"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, query.strip())
            if match:
                return match.group(1).strip()
        
        return None

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
        """쿼리에서 특정 정보 요청을 추출."""
        query_lower = query.lower()
        
        # 명시적으로 고등학교/중학교/초등학교를 언급한 경우만 school
        if any(word in query_lower for word in ['고등학교', '중학교', '초등학교']):
            return 'school'
        # 일반적인 "학교", "출신", "대학" 모두 최종학력(대학교)로 간주
        elif any(word in query_lower for word in ['대학', '대학교', '학교', '출신']):
            return 'university'
        elif any(word in query_lower for word in ['출생', '태어', '나이', '언제']):
            return 'birth'
        elif any(word in query_lower for word in ['작품', '소설', '책']):
            return 'works'
        elif any(word in query_lower for word in ['수상', '상', '받은']):
            return 'awards'
        
        return None

    def _contains_author_name(self, query: str) -> bool:
        """쿼리에 작가명이 포함되어 있는지 확인."""
        # 한글 이름 패턴 (2-4글자)
        import re
        korean_name_pattern = r'[가-힣]{2,4}'
        
        # 외국 이름 패턴 (영문)
        foreign_name_pattern = r'[A-Za-z]{3,}'
        
        korean_matches = re.findall(korean_name_pattern, query)
        foreign_matches = re.findall(foreign_name_pattern, query)
        
        # 일반적인 단어들은 제외
        common_words = ['대학', '어디', '나왔', '출신', '졸업', '언제', '태어', '작품', '소설', '어떤']
        
        # 한글 이름 후보가 있고, 일반 단어가 아닌 경우
        for name in korean_matches:
            if name not in common_words:
                return True
                
        # 외국 이름 후보가 있는 경우
        if foreign_matches:
            return True
            
        return False

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
            print(f"[DEBUG] birth 정보 추출: '{birth_info}'")
            print(f"[DEBUG] 분석 텍스트 일부: {content[:300]}...")
            
            if birth_info:
                return "{}은(는) {}에 태어났습니다.\n\n**상세 정보**: {}".format(
                    title, birth_info, url
                )
            else:
                return "{}의 출생 정보를 찾을 수 없습니다.\n\n**전체 정보**: {}".format(
                    title, url
                )
        
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
                print(f"[DEBUG] LLM birth 추출 결과: {result}")
                
                if result.get('found'):
                    birth_date = result.get('birth_date', '')
                    age_info = result.get('age_info', '')
                    
                    if birth_date and age_info:
                        return f"{birth_date} ({age_info})"
                    elif birth_date:
                        return birth_date
                    elif age_info:
                        return age_info
                        
            except Exception as e:
                print(f"[DEBUG] LLM birth 추출 실패: {e}")
        
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
                    # 디버깅: LLM이 왜 못 찾았는지 확인
                    print(f"[DEBUG] LLM 고등학교 추출 실패: {result}")
                    print(f"[DEBUG] 분석한 텍스트 일부: {content[:500]}...")
                    
            except Exception as e:
                print(f"[DEBUG] LLM 고등학교 추출 오류: {e}")
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
        """질문에 작가명이 포함되어 있는지 확인."""
        import re
        
        # 작품명→작가명 패턴 확인 (우선순위)
        book_to_author_patterns = [
            r'(.+)\s+(작가|저자)(?:가|는|을|를)?\s*(누구|뭐)',  # "토지 작가가 누구야"
            r'(.+)\s+(쓴|지은)\s*(사람|작가|저자)',  # "토지 쓴 사람"
        ]
        
        for pattern in book_to_author_patterns:
            match = re.search(pattern, query)
            if match:
                return False  # 이는 작품명이므로 작가명이 아님
        
        # 명시적 작가명 언급 패턴
        explicit_author_patterns = [
            r'(김영하|한강|무라카미\s*하루키|박민규|정유정)',  # 알려진 작가명
            r'[가-힣]{2,3}\s+[가-힣]{2,3}',  # 한국식 성명 (김영하, 이문열 등)
        ]
        
        # 작가명이 명시적으로 언급된 경우만 True
        for pattern in explicit_author_patterns:
            if re.search(pattern, query):
                # 작가 관련 질문인지 확인
                if any(word in query for word in ['작가', '저자', '작품', '대표작', '누구', '알려줘', '대해', '몇살', '나이', '대학', '학교']):
                    return True
        
        return False

    def _is_new_author_mentioned(self, query: str, context: Dict[str, Any]) -> bool:
        """새로운 작가가 언급되었는지 확인."""
        import re
        
        current_author = context.get('current_author') or ''
        if current_author:
            current_author = current_author.strip()
        
        # 명시적 작가명 패턴 (띄어쓰기 유연하게)
        author_patterns = [
            r'(김영하|한강|무라카미\s*하루키|박민규|정유정|이문열|조석|박완서)(?:\s*작가)?',  # 알려진 작가명 + 선택적 "작가"
            r'([가-힣]{2,4})(?:\s*작가)',  # "작가"가 붙은 이름
            r'[가-힣]{2,3}\s+[가-힣]{2,3}',  # 한국식 성명 패턴
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                mentioned_author = match.strip()
                # 현재 대화 중인 작가와 다른 작가가 언급된 경우
                if mentioned_author and mentioned_author != current_author:
                    # 작가 관련 질문인지 확인
                    author_keywords = ['작가', '저자', '작품', '대표작', '누구', '알려줘', '대해', '몇살', '나이', '대학', '학교', '수상', '상', '경력', '이력', '정보']
                    if any(word in query for word in author_keywords):
                        return True
        
        return False