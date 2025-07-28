#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
위키피디아 검색 에이전트 - 검색 결과 모델
위키피디아 검색 결과를 표현하는 데이터 모델
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class WikiSearchResult:
    """위키피디아 검색 결과"""
    success: bool
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (기존 코드 호환성을 위해)"""
        result = {'success': self.success}
        
        if self.success:
            result.update({
                'title': self.title,
                'summary': self.summary,
                'content': self.content,
                'url': self.url
            })
        else:
            result['error'] = self.error
            
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WikiSearchResult':
        """딕셔너리에서 객체 생성 (기존 코드 호환성을 위해)"""
        return cls(
            success=data.get('success', False),
            title=data.get('title'),
            summary=data.get('summary'),
            content=data.get('content'),
            url=data.get('url'),
            error=data.get('error')
        )

    @classmethod
    def create_success(cls, title: str, summary: str, content: str, url: str) -> 'WikiSearchResult':
        """성공 결과 생성"""
        return cls(
            success=True,
            title=title,
            summary=summary,
            content=content,
            url=url
        )

    @classmethod
    def create_error(cls, error_message: str) -> 'WikiSearchResult':
        """에러 결과 생성"""
        return cls(
            success=False,
            error=error_message
        )

    def is_success(self) -> bool:
        """성공 여부 확인"""
        return self.success

    def has_content(self) -> bool:
        """컨텐츠 존재 여부 확인"""
        return self.success and bool(self.content)

    def get_content_length(self) -> int:
        """컨텐츠 길이 반환"""
        return len(self.content) if self.content else 0

    def get_summary_length(self) -> int:
        """요약 길이 반환"""
        return len(self.summary) if self.summary else 0