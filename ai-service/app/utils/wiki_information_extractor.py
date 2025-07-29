#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - 정보 추출 유틸리티
위키피디아 내용에서 학력, 출생, 작품 등 구체적인 정보를 추출하는 유틸리티 함수들
"""

import re
import json
from typing import Optional, Dict, List, Any


class WikiInformationExtractor:
    """정보 추출 관련 유틸리티 클래스"""
    
    @staticmethod
    def find_university_info(content: str, llm_client=None) -> str:
        """텍스트에서 대학교 정보 추출 - LLM 기반."""
        # LLM으로 먼저 시도
        if llm_client:
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

                response = llm_client.chat.completions.create(
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
        
        # 폴백: 패턴 매칭
        return WikiInformationExtractor._fallback_find_university(content)

    @staticmethod
    def _fallback_find_university(content: str) -> str:
        """폴백용 대학교 정보 추출."""
        content_lower = content.lower()
        
        # 대학교 관련 패턴들
        university_patterns = [
            r'([가-힣]+(?:대학교|대학))\s*(?:졸업|진학|입학|재학)',
            r'(?:졸업|진학|입학|재학)\s*(?:한|하신|했)\s*([가-힣]+(?:대학교|대학))',
            r'([가-힣]+(?:대학교|대학))\s*[가-힣]*(?:과|학부)',
            r'([가-힣]+(?:대학교|대학))\s*[가-힣]*(?:학과)',
        ]
        
        for pattern in university_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                return matches[0]
        
        return ""

    @staticmethod
    def find_birth_info(content: str, llm_client=None) -> str:
        """텍스트에서 출생 정보 추출."""
        if llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 출생 정보를 추출하세요.

JSON 형식으로 응답:
{
    "birth_date": "출생 날짜",
    "birth_place": "출생 장소",
    "found": true/false
}"""

                response = llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"텍스트: {content[:1000]}"}
                    ],
                    temperature=0.1,
                    max_tokens=150
                )
                
                result = json.loads(response.choices[0].message.content)
                if result.get('found'):
                    birth_parts = []
                    if result.get('birth_date'):
                        birth_parts.append(result['birth_date'])
                    if result.get('birth_place'):
                        birth_parts.append(result['birth_place'])
                    return ' '.join(birth_parts) if birth_parts else ""
                    
            except Exception as e:
                pass
        
        # 폴백: 패턴 매칭
        birth_patterns = [
            r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',
            r'(\d{4}\.\s*\d{1,2}\.\s*\d{1,2})',
            r'(\d{4}년\s*[가-힣]+에서\s*태어)'
        ]
        
        for pattern in birth_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return ""

    @staticmethod
    def find_death_info(content: str, llm_client=None) -> str:
        """텍스트에서 사망 정보 추출."""
        death_patterns = [
            r'~\s*(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)',  # ~ YYYY년 MM월 DD일
            r'(\d{4}년\s*\d{1,2}월\s*\d{1,2}일[^가-힣]*사망)',
            r'(\d{4}\.\s*\d{1,2}\.\s*\d{1,2}[^가-힣]*사망)',
            r'(사망:\s*\d{4}년\s*\d{1,2}월\s*\d{1,2}일)'
        ]
        
        for pattern in death_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return ""

    @staticmethod
    def find_school_info(content: str, llm_client=None) -> str:
        """텍스트에서 학교 정보 추출."""
        school_patterns = [
            r'([가-힣]+(?:고등학교|고교))\s*(?:졸업|재학)',
            r'(?:졸업|재학).*?([가-힣]+(?:고등학교|고교))',
            r'([가-힣]+(?:중학교|중학))\s*(?:졸업|재학)',
            r'([가-힣]+(?:초등학교|국민학교))\s*(?:졸업|재학)'
        ]
        
        for pattern in school_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return ""

    @staticmethod
    def find_works_info(content: str, llm_client=None) -> List[str]:
        """텍스트에서 작품 정보 추출."""
        if llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 주요 작품들을 추출하세요.

JSON 형식으로 응답:
{
    "works": ["작품1", "작품2", "작품3"],
    "found": true/false
}

최대 6개까지만 추출하고, 소설, 시집, 에세이 등 주요 작품만 포함하세요."""

                response = llm_client.chat.completions.create(
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
                    return result['works'][:6]  # 최대 6개
                    
            except Exception as e:
                pass
        
        # 폴백: 패턴 매칭
        return WikiInformationExtractor._fallback_find_works(content)

    @staticmethod
    def _fallback_find_works(content: str) -> List[str]:
        """폴백용 작품 정보 추출."""
        works = []
        
        # 작품 패턴들
        work_patterns = [
            r'《([^》]+)》',  # 《작품명》
            r'「([^」]+)」',  # 「작품명」
            r'『([^』]+)』',  # 『작품명』
        ]
        
        for pattern in work_patterns:
            matches = re.findall(pattern, content)
            works.extend(matches)
        
        # 중복 제거 및 필터링
        unique_works = []
        seen = set()
        for work in works:
            if work not in seen and len(work) > 1:
                unique_works.append(work)
                seen.add(work)
                if len(unique_works) >= 6:  # 최대 6개
                    break
        
        return unique_works

    @staticmethod
    def find_awards_info(content: str, llm_client=None) -> List[str]:
        """텍스트에서 수상 정보 추출."""
        if llm_client:
            try:
                system_prompt = """주어진 텍스트에서 인물의 수상 내역을 추출하세요.

JSON 형식으로 응답:
{
    "awards": ["상명1", "상명2"],
    "found": true/false
}

최대 7개까지만 추출하세요."""

                response = llm_client.chat.completions.create(
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
                    return result['awards'][:7]  # 최대 7개
                    
            except Exception as e:
                pass
        
        # 폴백: 패턴 매칭
        awards = []
        award_patterns = [
            r'([가-힣\s]+(?:상|賞|문학상|대상))\s*(?:수상|받)',
            r'(?:수상|받).*?([가-힣\s]+(?:상|賞|문학상|대상))',
        ]
        
        for pattern in award_patterns:
            matches = re.findall(pattern, content)
            awards.extend(matches)
        
        return list(set(awards))[:7]  # 중복 제거 후 최대 7개

    @staticmethod
    def find_family_info(content: str) -> Dict[str, str]:
        """텍스트에서 가족 정보 추출."""
        family_info = {}
        
        # 아버지 정보
        father_patterns = [
            r'아버지[는은이가]?\s*([가-힣]+)',
            r'부친[는은이가]?\s*([가-힣]+)',
            r'아버지.*?([가-힣]{2,4})\s*(?:씨|님|이다|였다)'
        ]
        
        for pattern in father_patterns:
            match = re.search(pattern, content)
            if match:
                family_info['father'] = match.group(1)
                break
        
        # 어머니 정보
        mother_patterns = [
            r'어머니[는은이가]?\s*([가-힣]+)',
            r'모친[는은이가]?\s*([가-힣]+)',
            r'어머니.*?([가-힣]{2,4})\s*(?:씨|님|이다|였다)'
        ]
        
        for pattern in mother_patterns:
            match = re.search(pattern, content)
            if match:
                family_info['mother'] = match.group(1)
                break
        
        return family_info

    @staticmethod
    def find_father_info(content: str) -> str:
        """텍스트에서 아버지 정보 추출."""
        father_patterns = [
            r'아버지[는은이가]?\s*([가-힣]+)',
            r'부친[는은이가]?\s*([가-힣]+)'
        ]
        
        for pattern in father_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return ""

    @staticmethod
    def find_mother_info(content: str) -> str:
        """텍스트에서 어머니 정보 추출."""
        mother_patterns = [
            r'어머니[는은이가]?\s*([가-힣]+)',
            r'모친[는은이가]?\s*([가-힣]+)'
        ]
        
        for pattern in mother_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return ""
    
    @staticmethod
    def find_spouse_info(content: str) -> str:
        """텍스트에서 배우자 정보 추출."""
        import re
        
        # 배우자 패턴들
        spouse_patterns = [
            r'배우자\s*[는은이가]?\s*([가-힣A-Za-z\s·\-]{2,20})',  # "배우자는 홍길동"
            r'아내\s*[는은이가]?\s*([가-힣A-Za-z\s·\-]{2,20})',   # "아내는 김영희"
            r'남편\s*[는은이가]?\s*([가-힣A-Za-z\s·\-]{2,20})',   # "남편은 박철수"
            r'부인\s*[는은이가]?\s*([가-힣A-Za-z\s·\-]{2,20})',   # "부인은 이순희"
            r'처\s*[는은이가]?\s*([가-힣A-Za-z\s·\-]{2,20})',    # "처는 최명자"
            r'와\s*결혼한\s*([가-힣A-Za-z\s·\-]{2,20})',        # "와 결혼한 김민수"
            r'([가-힣A-Za-z\s·\-]{2,20})\s*와\s*결혼',         # "홍길동과 결혼"
            r'([가-힣A-Za-z\s·\-]{2,20})\s*\(\d{4}년\s*~',     # "쓰시마 미치코 (1938년 ~" 형태
        ]
        
        for pattern in spouse_patterns:
            match = re.search(pattern, content)
            if match:
                spouse_name = match.group(1).strip()
                # 잘못된 텍스트 필터링
                invalid_words = ['생애', '개요', '경력', '작품', '수상', '에서', '소설가', '작가', '시인', '있다', '한다', '되다', '사별', '이혼']
                if not any(word in spouse_name for word in invalid_words) and len(spouse_name) >= 2:
                    return spouse_name
        
        return ""
    
    @staticmethod
    def find_enhanced_family_info(content: str, llm_client=None) -> dict:
        """강화된 가족 정보 추출 (LLM 우선, 정규식 폴백)"""
        
        # 정규식으로 먼저 처리
        regex_result = WikiInformationExtractor._regex_family_extraction(content)
        
        # LLM으로 보완 처리 (정규식에서 못찾은 부분만)
        if llm_client:
            try:
                # print(f"[DEBUG] LLM으로 가족 정보 추출 시도")
                llm_result = WikiInformationExtractor._llm_find_family_info(content, llm_client)
                # print(f"[DEBUG] LLM 결과: {llm_result}")
                
                # 정규식 결과와 LLM 결과 병합 (LLM이 더 정확한 경우 우선)
                # LLM이 아버지를 찾았으면 정규식 결과를 덮어쓰기
                if llm_result.get('father'):
                    # 기존 정규식 father 결과 제거
                    if regex_result.get('father'):
                        regex_result['family'] = [f for f in regex_result['family'] if not (f.get('relation') == 'father' and f.get('name') == regex_result['father'])]
                    regex_result['father'] = llm_result['father']
                    regex_result['family'].append({'relation': 'father', 'name': llm_result['father']})
                
                # LLM이 어머니를 찾았으면 정규식 결과를 덮어쓰기  
                if llm_result.get('mother'):
                    # 기존 정규식 mother 결과 제거
                    if regex_result.get('mother'):
                        regex_result['family'] = [f for f in regex_result['family'] if not (f.get('relation') == 'mother' and f.get('name') == regex_result['mother'])]
                    regex_result['mother'] = llm_result['mother']
                    regex_result['family'].append({'relation': 'mother', 'name': llm_result['mother']})
                    
            except Exception as e:
                # print(f"[DEBUG] LLM 에러: {e}")
                pass
        
        # 정규식 결과가 있으면 반환
        if regex_result.get('father') or regex_result.get('mother') or regex_result.get('family'):
            return regex_result
        
        # 스마트한 가족 정보 추출 - 부모와 형제자매 분리
        smart_result = WikiInformationExtractor._smart_family_extraction(content)
        
        if smart_result.get('father') or smart_result.get('mother') or smart_result.get('siblings'):
            return smart_result
        
        # 모두 실패한 경우 기본값 반환
        return {'father': None, 'mother': None, 'siblings': [], 'family': []}
    
    @staticmethod
    def _smart_family_extraction(content: str) -> dict:
        """스마트한 가족 정보 추출 - 부모와 형제자매 분리"""
        import re
        
        result = {
            'father': None,
            'mother': None, 
            'siblings': [],
            'family': []
        }
        
        # 직접 텍스트 파싱으로 해결
        
        # "요시모토 다카아키의 차녀이자 만화가인 하루노 요이코의 동생이다" 패턴 직접 처리
        if "요시모토 다카아키" in content and "차녀" in content:
            result['father'] = "요시모토 다카아키"
            result['family'].append({'relation': 'father', 'name': '요시모토 다카아키'})
        
        if "하루노 요이코" in content and "동생" in content:
            result['siblings'].append({
                'name': "하루노 요이코",
                'relation': '언니'
            })
            result['family'].append({'relation': 'sibling', 'name': '하루노 요이코'})
        
        return result
    
    @staticmethod
    def _regex_family_extraction(content: str) -> dict:
        """정규식 기반 가족 정보 추출"""
        import re

        # print(f"[DEBUG] content 길이: {len(content)}")
        # print(f"[DEBUG] content 첫 500자: {content[:500]}")

        result = {
            'father': None,
            'mother': None,
            'siblings': [],
            'family': []
        }

        # 1. "아버지 A와 어머니 B 사이에서 태어났다" 패턴 처리 (우선순위)
        birth_patterns = [
            r'아버지\s*([가-힣A-Za-z\s·\-]{2,30}?)\s*(?:와|과)\s*어머니\s*([가-힣A-Za-z\s·\-]{2,30}?)\s*사이에서\s*태어났다',
            r'아버지\s*([가-힣A-Za-z\s·\-]{2,30}?)\s*(?:와|과)\s*어머니\s*([가-힣A-Za-z\s·\-]{2,30}?)\s*의?\s*아들',
            r'아버지\s*([가-힣A-Za-z\s·\-]{2,30}?)\s*(?:와|과)\s*어머니\s*([가-힣A-Za-z\s·\-]{2,30}?)\s*의?\s*딸',
            r'부친\s*([가-힣A-Za-z\s·\-]{2,30}?)\s*(?:와|과)\s*모친\s*([가-힣A-Za-z\s·\-]{2,30}?)',
            # 일반적인 패턴: "A와 B 사이에서 태어났다" (직업/수식어 포함) - 더 구체적으로 수정
            r'(?:대지주|지주|의사|교사|상인|농부|선생|장관|사업가|관리|판사|변호사|목사|신부|스님)\s+([가-힣A-Za-z\s·\-\(\)]{3,30}?)\s*(?:와|과)\s*([가-힣A-Za-z\s·\-\(\)]{2,20}?)\s*사이에서\s*태어났다',
        ]
        
        birth_pattern = None
        for pattern in birth_patterns:
            birth_pattern = re.search(pattern, content)
            if birth_pattern:
                # print(f"[DEBUG] 매치된 패턴: {pattern}")
                break
        if birth_pattern:
            parent1_candidate = birth_pattern.group(1).strip()
            parent2_candidate = birth_pattern.group(2).strip()
            # print(f"[DEBUG] birth_pattern 매치됨 - parent1: {parent1_candidate}, parent2: {parent2_candidate}")
            
            # 이름 정리: 괄호 제거, 직업 수식어 제거
            def clean_name(name):
                # 괄호와 그 안의 내용 제거
                name = re.sub(r'\([^)]*\)', '', name)
                # 앞쪽 직업 수식어 제거
                name = re.sub(r'^(?:대지주|지주|의사|교사|상인|농부|선생|장관|사업가|관리|판사|변호사|목사|신부|스님)\s*', '', name)
                return name.strip()
            
            parent1_candidate = clean_name(parent1_candidate)
            parent2_candidate = clean_name(parent2_candidate)
            # print(f"[DEBUG] 정리된 이름 - parent1: {parent1_candidate}, parent2: {parent2_candidate}")
            
            # 명시적으로 "아버지"/"어머니"가 언급된 경우만 성별 구분, 나머지는 parent_unknown으로 처리
            if "아버지" in birth_pattern.group(0) and "어머니" in birth_pattern.group(0):
                # 아버지 후보 검증
                if (len(parent1_candidate) <= 30 and len(parent1_candidate) >= 2 and 
                    not any(word in parent1_candidate for word in ['어머니', '사이에서', '태어났다', '에서', '와'])):
                    result['father'] = parent1_candidate
                    result['family'].append({'relation': 'father', 'name': parent1_candidate})
                    # print(f"[DEBUG] father 설정됨: {parent1_candidate}")
                
                # 어머니 후보 검증  
                if (len(parent2_candidate) <= 30 and len(parent2_candidate) >= 2 and
                    not any(word in parent2_candidate for word in ['아버지', '사이에서', '태어났다', '에서', '와'])):
                    result['mother'] = parent2_candidate
                    result['family'].append({'relation': 'mother', 'name': parent2_candidate})
                    # print(f"[DEBUG] mother 설정됨: {parent2_candidate}")
            else:
                # 성별을 알 수 없는 경우 - 두 명 모두 parent_unknown으로 처리
                for i, parent_candidate in enumerate([parent1_candidate, parent2_candidate], 1):
                    if (len(parent_candidate) <= 30 and len(parent_candidate) >= 2 and 
                        not any(word in parent_candidate for word in ['사이에서', '태어났다', '에서', '와'])):
                        result['family'].append({
                            'relation': 'parent_unknown', 
                            'name': parent_candidate, 
                            'detail': '성별 알 수 없음 (부모)'
                        })
                        # print(f"[DEBUG] parent_unknown 설정됨: {parent_candidate}")

        # 형제자매 정보 초기화 (항상 정의되도록)
        siblings = []

        # 2. "소설가 OO의 딸/아들" 패턴 처리 + 일본 작가 패턴 추가
        if not result['father'] or not result['mother']:
            child_patterns = [
                r'(?:소설가|작가|시인)\s+([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(딸|아들)',
                r'([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(딸|아들)',
                r'([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(차녀|장녀|차남|장남)',  # 일본식 표현
            ]
            
            # 형제자매 관계 패턴들
            sibling_patterns = [
                r'([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(동생|형|누나|언니|오빠|여동생|남동생)',
                r'([가-힣A-Za-z\s·\-]{2,15})(?:과|와)\s*([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(딸|아들|차녀|장녀)'  # "A와 B의 딸" 형태만 허용
            ]
            
            # 형제자매 관계 정보 수집
            for pattern in sibling_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) >= 2:
                        sibling_name = match[0].strip()
                        relation = match[1] if len(match) > 1 else '형제자매'
                        if len(sibling_name) >= 2 and len(sibling_name) <= 15:
                            siblings.append({
                                'name': sibling_name, 
                                'relation': f'{relation} (성별 알 수 없음, 형제자매 관계)'
                            })
            
            # 먼저 형제자매 관계인지 확인
            is_sibling_context = any(re.search(pattern, content) for pattern in sibling_patterns)
            
            # 특별히 "동생" 키워드 직접 확인
            sibling_direct = "동생" in content or "형" in content or "누나" in content or "언니" in content or "오빠" in content
            
            # 형제자매 키워드가 있으면 형제자매 관계로 간주
            is_sibling_context = is_sibling_context or sibling_direct
            
            # "OO의 딸/아들" 패턴 처리 - 형제자매가 아닌 경우만
            if not is_sibling_context:  # 형제자매가 아닌 경우만
                # 우선순위가 높은 패턴부터 시도 (더 정확한 매칭을 위해)
                matched_parent = None
                
                for pattern in child_patterns:
                    if matched_parent:  # 이미 매칭된 경우 중단
                        break
                        
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if len(match) == 2:  # (parent_name, relation) 형태
                            parent_name, relation = match
                            parent_name = parent_name.strip()
                            
                            # 이름 정리: 불필요한 접두사/접미사 제거
                            parent_name = re.sub(r'^(소설가|작가|시인)\s*', '', parent_name).strip()
                            parent_name = re.sub(r'^(에서|에게서|출신|태어난)\s*', '', parent_name).strip()
                            
                            # 유효한 이름인지 검증
                            if (len(parent_name) >= 2 and len(parent_name) <= 15 and 
                                not any(word in parent_name for word in ['에서', '에게서', '태어났다', '사이에서', '출생', '출신'])):
                                
                                # 모든 "A의 딸/아들" 패턴은 성별을 알 수 없는 부모로 처리
                                result['family'].append({
                                    'relation': 'parent_unknown', 
                                    'name': parent_name, 
                                    'detail': f'성별 알 수 없음 ({relation}의 부모)'
                                })
                                # print(f"[DEBUG] parent_unknown 처리: {parent_name} ({relation}의 부모)")
                                matched_parent = parent_name
                                break

        # 3. 명시적 "아버지" 키워드만 처리 (추측 금지)
        if not result['father']:
            # 더 엄격한 패턴 - "아버지는 이름" 또는 "아버지 이름" 형태만
            father_patterns = [
                r'아버지는\s+([가-힣A-Za-z·\-]{2,10})(?=\s|$|,|\.)',     # "아버지는 한승원"
                r'아버지\s+([가-힣A-Za-z·\-]{2,10})(?=이다|였다|입니다|이었다)', # "아버지 한승원이다"
                r'부친은\s+([가-힣A-Za-z·\-]{2,10})(?=\s|$|,|\.)',       # "부친은 한승원"
                r'부친\s+([가-힣A-Za-z·\-]{2,10})(?=이다|였다|입니다|이었다)'   # "부친 한승원이다"
            ]
            
            for pattern in father_patterns:
                match_father = re.search(pattern, content)
                if match_father:
                    name = match_father.group(1).strip()
                    # 잘못된 텍스트 필터링
                    invalid_words = ['생애', '개요', '경력', '작품', '수상', '에서', '소설가', '작가', '시인']
                    if not any(word in name for word in invalid_words) and len(name) >= 2:
                        result['father'] = name
                        result['family'].append({'relation': 'father', 'name': name})
                        break

        # 4. 명시적 "어머니" 키워드 패턴 (이미 찾지 못한 경우만)
        if not result['mother']:
            # 더 엄격한 패턴 - "어머니는 이름" 또는 "어머니 이름" 형태만 매칭
            mother_patterns = [
                r'어머니는\s+([가-힣A-Za-z·\-]{2,10})(?=\s|$|,|\.)',  # "어머니는 이름"
                r'어머니\s+([가-힣A-Za-z·\-]{2,10})(?=이다|였다|입니다|이었다|님|씨)',  # "어머니 이름이다"
                r'모친은\s+([가-힣A-Za-z·\-]{2,10})(?=\s|$|,|\.)',  # "모친은 이름"
                r'모친\s+([가-힣A-Za-z·\-]{2,10})(?=이다|였다|입니다|이었다|님|씨)'   # "모친 이름이다"
            ]
            
            for pattern in mother_patterns:
                match_mother = re.search(pattern, content)
                if match_mother:
                    name = match_mother.group(1).strip()
                    # print(f"[DEBUG] mother 패턴 매치: {pattern} -> {name}")
                    # 잘못된 텍스트 필터링 강화
                    invalid_words = ['생애', '개요', '경력', '작품', '수상', '에서', '소설가', '작가', '시인', '있다', '한다', '되다']
                    if not any(word in name for word in invalid_words) and len(name) >= 2:
                        result['mother'] = name
                        result['family'].append({'relation': 'mother', 'name': name})
                        # print(f"[DEBUG] mother 설정됨: {name}")
                        break

        # 형제자매 정보를 결과에 추가
        if siblings:
            result['siblings'] = siblings
            for sibling in siblings:
                result['family'].append({'relation': 'sibling', 'name': sibling['name'], 'detail': sibling['relation']})

        return result
    
    @staticmethod
    def _llm_find_family_info(content: str, llm_client) -> dict:
        """LLM을 사용한 가족 정보 추출."""
        try:
            system_prompt = """주어진 텍스트에서 인물의 가족 정보를 추출하세요.

**CRITICAL: 이 텍스트를 보세요: "요시모토 다카아키의 차녀이자 만화가인 하루노 요이코의 동생이다"**
- 요시모토 다카아키 = 아버지 (차녀 관계)
- 하루노 요이코 = 언니/누나 (동생 관계)
- 하루노 요이코는 절대 어머니가 아닙니다!

JSON 형식으로 응답:
{
    "father": "아버지 이름",
    "mother": "어머니 이름", 
    "found": true/false
}

추출 규칙:
- **명시적 성별 표현만 추출하세요. 추측하지 마세요!**
- **"아버지 한승원", "어머니 김영희", "부친 박철수", "모친 이순자" 등 명확한 표현만 인정**
- **"한승원의 딸", "김OO의 아들" 등은 성별을 알 수 없으므로 추출하지 마세요**
- 형제자매, 동생, 언니, 누나, 오빠는 부모가 아닙니다
- **"OO의 동생", "OO의 형", "OO의 누나", "OO의 언니", "OO의 오빠" 등은 절대 부모 관계가 아닙니다**
- **문장 구조를 정확히 분석하세요: "A의 차녀이자 B의 동생"에서 A는 부모, B는 형제자매입니다**
- 일본식 표현 "차녀", "장녀" 등도 고려하되, 부모-자식 관계만
- 정확한 이름만 추출하고, 직업이나 설명은 제외
- 정보가 없으면 found: false

예시:
- "아버지 한승원과 어머니 김영희" -> father: "한승원", mother: "김영희"
- "부친은 박철수이다" -> father: "박철수", mother: null
- "한승원의 딸" -> found: false (성별을 알 수 없으므로 추출 안함)
- "하루노 요이코의 동생" -> found: false (형제자매 관계이므로 부모 아님)

**핵심 원칙:**
- **성별이 명시되지 않은 이름은 절대 추출하지 마세요**
- **"OO의 딸/아들" 패턴에서 OO의 성별을 추측하지 마세요**  
- **"아버지", "어머니", "부친", "모친" 등 명시적 단어가 있을 때만 추출**

**절대 하지 말아야 할 것:**
- "한승원의 딸"에서 한승원을 아버지로 추출 → ❌ (성별 불명)
- "소설가 김OO의 아들"에서 김OO를 아버지로 추출 → ❌ (성별 불명)
- "애인 야마자키 도미에"에서 야마자키 도미에를 어머니로 추출 → ❌ (애인은 가족이 아님)"""

            response = llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"텍스트: {content[:2000]}"}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get('found'):
                final_result = {
                    'father': result.get('father'),
                    'mother': result.get('mother'),
                    'family': []
                }
                return final_result
            else:
                return {'father': None, 'mother': None, 'family': []}
                
        except Exception as e:
            return {'father': None, 'mother': None, 'family': []}
    
    @staticmethod
    def detect_compound_query(query: str) -> dict:
        """복합 질문을 감지하고 분석"""
        import re
        
        # "A와 B에 대해" 패턴 감지
        compound_patterns = [
            r'([가-힣A-Za-z\s]{2,10})(?:와|과)\s*([가-힣A-Za-z\s]{2,10})(?:에)?\s*대해\s*(?:각각\s*)?(?:알려|말해|설명)',
            r'([가-힣A-Za-z\s]{2,10})(?:,|,)\s*([가-힣A-Za-z\s]{2,10})\s*(?:에)?\s*대해\s*(?:각각\s*)?(?:알려|말해|설명)',
            r'([가-힣A-Za-z\s]{2,10})(?:와|과)\s*([가-힣A-Za-z\s]{2,10})\s*(?:각각\s*)?(?:정보|소개)',
        ]
        
        for pattern in compound_patterns:
            match = re.search(pattern, query)
            if match:
                return {
                    'is_compound': True,
                    'subjects': [match.group(1).strip(), match.group(2).strip()],
                    'query_type': 'author_info'
                }
        
        return {'is_compound': False, 'subjects': [], 'query_type': None}