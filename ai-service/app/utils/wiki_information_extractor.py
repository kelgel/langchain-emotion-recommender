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