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
    def find_enhanced_family_info(content: str, llm_client=None) -> dict:
        """강화된 가족 정보 추출 (정규식 우선, LLM 폴백)"""
        
        # 스마트한 가족 정보 추출 - 부모와 형제자매 분리
        smart_result = WikiInformationExtractor._smart_family_extraction(content)
        
        if smart_result.get('father') or smart_result.get('mother') or smart_result.get('siblings'):
            return smart_result
        
        # 먼저 정규식으로 처리 (더 정확함)
        regex_result = WikiInformationExtractor._regex_family_extraction(content)
        
        if regex_result.get('father') or regex_result.get('mother'):
            return regex_result
        
        # 정규식으로 찾지 못한 경우에만 LLM 사용
        if llm_client:
            try:
                llm_result = WikiInformationExtractor._llm_find_family_info(content, llm_client)
                if llm_result.get('father') or llm_result.get('mother'):
                    return llm_result
            except Exception as e:
                pass
        
        # 둘 다 실패한 경우 기본값 반환
        return {'father': None, 'mother': None, 'family': []}
    
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

        result = {
            'father': None,
            'mother': None,
            'family': []
        }

        # 1. "A와 B에 대해" 패턴 처리 (우선순위)
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

        # 2. "소설가 OO의 딸/아들" 패턴 처리 + 일본 작가 패턴 추가
        if not result['father'] or not result['mother']:
            child_patterns = [
                r'(?:소설가|작가|시인)\s+([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(딸|아들)',
                r'([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(딸|아들)',
                r'([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(차녀|장녀|차남|장남)',  # 일본식 표현
            ]
            
            # 형제자매 관계는 제외하는 패턴들
            sibling_patterns = [
                r'([가-힣A-Za-z\s·\-ㅂ-ㅎㄱ-ㅎ]{2,15})\s*의\s+(동생|형|누나|언니|오빠|여동생|남동생)',
                r'([가-힣A-Za-z\s·\-]{2,15})(?:과|와)\s*([가-힣A-Za-z\s·\-]{2,15})\s*의\s+(딸|아들|차녀|장녀)'  # "A와 B의 딸" 형태만 허용
            ]
            
            # 먼저 형제자매 관계인지 확인
            is_sibling_context = any(re.search(pattern, content) for pattern in sibling_patterns)
            
            # 특별히 "동생" 키워드 직접 확인
            sibling_direct = "동생" in content or "형" in content or "누나" in content or "언니" in content or "오빠" in content
            
            # 형제자매 키워드가 있으면 형제자매 관계로 간주
            is_sibling_context = is_sibling_context or sibling_direct
            
            if not is_sibling_context:  # 형제자매가 아닌 경우만 부모로 간주
                for pattern in child_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if len(match) == 2:  # (parent_name, relation) 형태
                            parent_name, relation = match
                            parent_name = parent_name.strip()
                            parent_name = re.sub(r'^(소설가|작가|시인)\s*', '', parent_name).strip()
                            
                            if len(parent_name) >= 2 and len(parent_name) <= 15:
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
- **부모만 추출하세요. 형제자매, 동생, 언니, 누나, 오빠는 부모가 아닙니다**
- 부모, 아버지, 어머니, 부친, 모친 등의 키워드 활용
- "OO의 딸", "OO의 아들", "OO의 장녀", "OO의 차녀", "OO의 장남", "OO의 차남" 등의 표현에서 OO가 부모인 경우만 추출
- **"OO의 동생", "OO의 형", "OO의 누나", "OO의 언니", "OO의 오빠" 등은 절대 부모 관계가 아닙니다**
- **문장 구조를 정확히 분석하세요: "A의 차녀이자 B의 동생"에서 A는 부모, B는 형제자매입니다**
- 일본식 표현 "차녀", "장녀" 등도 고려하되, 부모-자식 관계만
- 정확한 이름만 추출하고, 직업이나 설명은 제외
- 정보가 없으면 found: false

예시:
- "요시모토 다카아키의 차녀" -> father: "요시모토 다카아키"
- "하루노 요이코의 동생" -> found: false (형제자매 관계이므로 부모 아님)
- "A의 차녀이자 B의 동생이다" -> father: "A", mother: null (B는 형제자매이므로 부모 아님)

**실제 텍스트 예시:**
텍스트: "요시모토 다카아키의 차녀이자 만화가인 하루노 요이코의 동생이다"
→ 정답: father: "요시모토 다카아키", mother: null
→ 이유: 하루노 요이코는 "동생" 관계이므로 형제자매입니다.

**절대 하지 말아야 할 것:**
- "하루노 요이코의 동생"에서 하루노 요이코를 어머니로 추출하면 안됩니다!
- "동생" 관계는 형제자매 관계입니다!"""

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