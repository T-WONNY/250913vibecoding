# app.py
# ─────────────────────────────────────────────────────────
# 구글 설문조사 CSV 자동 분석기 (Streamlit + pandas + Altair)
# 외부 라이브러리 불필요: pandas/altair는 Streamlit에 포함
# ─────────────────────────────────────────────────────────
import re
import unicodedata
from collections import Counter

import altair as alt
import pandas as pd
import streamlit as st

# ====== 기본 세팅 ======
st.set_page_config(page_title="구글 설문 CSV 자동 분석", page_icon="🧠", layout="wide")
st.title("🧠 구글 설문 CSV 자동 분석기")
st.caption("CSV를 업로드하면 문항 유형을 자동 추론하고, 선택형/숫자형/텍스트형을 손쉽게 시각화합니다.")

# ====== 상수 ======
COLUMN_TYPES = {
    "timestamp": "타임스탬프",
    "email": "이메일",
    "phone": "전화",
    "name": "이름",
    "student_id": "학번",
    "numeric": "숫자",
    "single_choice": "단일선택",
    "multiple_choice": "다중선택",
    "linear_scale": "척도",
    "text_short": "단답",
    "text_long": "장문",
    "url": "URL",
    "other": "기타",
}
SENSITIVE_TYPES = {"email", "phone", "student_id", "url", "name"}
# 다중선택 응답 구분자(국내 CSV는 보통 쉼표, 세미콜론, 슬래시, 수직바 등)
CHOICE_SEP = r"[;,／\|/]"

# 텍스트 토큰화(한글 2자 이상만)
TOK_RGX = re.compile(r"[가-힣]{2,}")
STOPWORDS = {"은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "또", "더", "등", "및"}

# ====== 유틸 ======
def normalize_col(col: str) -> str:
    """괄호 설명 제거, 공백 정리, NFKC 정규화"""
    col = unicodedata.normalize("NFKC", str(col))
    col = re.sub(r"\s*\(.*?\)\s*$", "", col)  # 끝의 (설명) 제거
    col = re.sub(r"\s+", " ", col)
    return col.strip()

def detect_type(series: pd.Series) -> str:
    """열 값으로부터 문항 유형 대략 추정"""
    s = series.dropna().astype(str)
    if s.empty:
        return "other"
    # 숫자만(또는 거의 숫자)
    if pd.to_numeric(s, errors="coerce").notna().mean() > 0.95:
        return "numeric"
    # 다중선택(구분자 포함 비율이 일정 이상)
    if (s.str.contains(CHOICE_SEP)).mean() > 0.2:
        return "multiple_choice"
    # 카테고리(고유값 수가 상대적으로 적음)
    if s.nunique() < max(20, len(s) * 0.5):
        return "single_choice"
    # 길이로 단답/장문 가늠
    mlen = s.str.len().dropna().median()
    if mlen and mlen < 50:
        return "text_short"
    return "text_long"

def split_multiple_choice(s: pd.Series) -> pd.Series:
    """다중선택 응답을 1개 선택 단위
