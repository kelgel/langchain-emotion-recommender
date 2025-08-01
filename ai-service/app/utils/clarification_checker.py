"""
clarification_checker.py
clarification_checker intent에 따른 필수 정보 누락 판단(정보가 부족한지 판단) - True 또는 False
"""

def needs_clarification(intent: str, info: dict) -> bool:
    """
    사용자의 intent에 따라 필요한 정보가 충분히 포함되어 있는지 판단하여,
    Clarification 단계가  필요한지 여부를 반환합니다.
    """

    # 1. 도서 추천 (recommendation)
    # 감정+장르 or 작가 or 키워드 중 하나라도 있으면 추천 가능
    if intent == "recommendation":
        genre = info.get("genre")
        emotion = info.get("emotion")
        author = info.get("author")
        keywords = info.get("keywords")

        # ✅ 추천 조건: 네 가지 중 하나라도 있으면 충분
        if any([genre, emotion, author, keywords]):
            return False  # 조건 충분 → clarification 필요 없음

        return True  # 네 가지 모두 없음 → clarification 필요
    # if intent ==  "recommendation":
    #     if intent == "recommendation":
    #         genre = info.get("genre")
    #         emotion = info.get("emotion")
    #
    #     # ✅ 감정과 장르 모두 없으면 → 둘 다 물어봐야 함
    #     if not genre and not emotion:
    #         return True
    #
    #     # ✅ 감정 없고 장르만 있을 경우 → Clarification 생략 (바로 추천 가능)
    #     if genre and not emotion:
    #         return False  # 여기 중요!
    #
    #     # ✅ 둘 다 있으면 당연히 문제 없음
    #     return False

    # 2. 도서/작가 정보 요청(info)
    # 책 제목 or 작가 이름 둘 중 하나라도 있어야함
    elif intent == "info": 
        return not(info.get("title") or info.get("author"))

    # 3. 주문 확인 (order_check)
    # 주문 번호 or 책 제목 중 하나라도 있어야 함
    elif intent =="order_check":
        return not(info.get("order_id") or info.get("title"))

    # 4. 재고 확인 (stock_check)
    # 책 제목이 반드시 있어야 함
    elif intent == "stock_check":
        return not info.get("title")

    # 5. 의도 자체가 모호 (clarification)
    elif intent == "clarification":
        return True

    # 알 수 없는 intent -> clarification
    return True
