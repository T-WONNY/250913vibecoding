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
# 다중선택 응답 구분자(쉼표, 세미콜론, 슬래시, 수직바 등)
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
    """다중선택 응답을 1개 선택 단위로 분해"""
    return (
        s.dropna()
        .astype(str)
        .str.split(CHOICE_SEP, expand=True)
        .stack()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
    )

def make_top10_with_others(counts: pd.Series, top_n: int = 10) -> pd.Series:
    """상위 N + 기타로 묶어서 반환"""
    if len(counts) <= top_n:
        return counts
    top = counts.head(top_n)
    others = counts.iloc[top_n:].sum()
    return pd.concat([top, pd.Series({"기타": others})])

def bar_chart_from_counts(counts: pd.Series, title: str):
    df = counts.rename_axis("label").reset_index(name="count")
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="응답 수"),
            y=alt.Y("label:N", sort="-x", title=None),
            tooltip=["label:N", "count:Q"],
        )
        .properties(title=title, height=max(160, 18 * len(df)))
    )
    return chart

def hist_chart(nums: pd.Series, title: str):
    df = pd.DataFrame({"value": pd.to_numeric(nums, errors="coerce").dropna()})
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("value:Q", bin=alt.Bin(maxbins=20), title="값(구간)"),
            y=alt.Y("count():Q", title="빈도"),
            tooltip=[alt.Tooltip("count():Q", title="빈도")],
        )
        .properties(title=title, height=240)
    )
    return chart

def tokenize_ko(text: str):
    """한글 토큰화 (불용어 제외)"""
    return [t for t in TOK_RGX.findall(str(text)) if t not in STOPWORDS]

# ====== 사이드바 ======
with st.sidebar:
    st.header("⚙️ 옵션")
    auto_detect = st.checkbox("자동 타입 추론", value=True)
    show_pie = st.checkbox("파이 차트(참고용)도 함께 보기", value=False)
    min_token_len = st.slider("텍스트 토큰 최소 길이", 2, 4, 2, 1)
    top_k_tokens = st.slider("텍스트 상위 토큰 수", 10, 50, 30, 5)
    st.caption("※ 파이 차트는 참고용으로 제공되며, 범주가 많을 때는 막대 차트를 권장합니다.")

# ====== 파일 업로드 ======
file = st.file_uploader("📂 구글 설문 응답 CSV 업로드", type=["csv"])
if not file:
    st.info("CSV를 업로드하면 분석이 시작됩니다.")
    st.stop()

# CSV 읽기(한글 인코딩 대응)
read_ok = False
for enc in ("utf-8-sig", "cp949", "utf-8"):
    try:
        df = pd.read_csv(file, encoding=enc)
        read_ok = True
        break
    except Exception:
        continue
if not read_ok:
    st.error("CSV 인코딩을 감지하지 못했습니다. UTF-8 또는 CP949로 저장 후 다시 업로드해 주세요.")
    st.stop()

# 컬럼 정규화
df.columns = [normalize_col(c) for c in df.columns]

# ====== 타입 구성(세션 저장) ======
if "col_types" not in st.session_state:
    st.session_state.col_types = {}

col_types = st.session_state.col_types
for col in df.columns:
    if col not in col_types:
        col_types[col] = detect_type(df[col]) if auto_detect else "other"

# 타입 수동 수정 UI
with st.expander("🗂 문항 유형 확인/수정", expanded=False):
    left, right = st.columns(2)
    keys = list(df.columns)
    for i, col in enumerate(keys):
        cur = col_types.get(col, "other")
        with (left if i % 2 == 0 else right):
            col_types[col] = st.selectbox(
                f"{col}",
                list(COLUMN_TYPES.keys()),
                index=list(COLUMN_TYPES.keys()).index(cur) if cur in COLUMN_TYPES else 0,
                format_func=lambda k: f"{COLUMN_TYPES[k]}",
                key=f"type_{col}",
            )

# ====== 네비게이션 ======
tab_overview, tab_stats, tab_text = st.tabs(["📊 개요", "📈 통계", "📝 텍스트"])

# ====== 1) 개요 ======
with tab_overview:
    st.subheader("📊 전체 개요")
    c1, c2, c3 = st.columns(3)
    c1.metric("응답 수", f"{len(df):,}")
    c2.metric("문항 수", f"{len(df.columns):,}")
    completion = (df.notna().sum().sum()) / (len(df) * len(df.columns)) * 100 if len(df) and len(df.columns) else 0
    c3.metric("완료율(전체 셀 기준)", f"{completion:.1f}%")

    st.markdown("#### 문항별 응답률")
    resp_rate = (df.notna().sum() / len(df) * 100).sort_values(ascending=True) if len(df) else pd.Series(dtype=float)
    if not resp_rate.empty:
        chart = bar_chart_from_counts(resp_rate, "문항별 응답률(%)").encode(x=alt.X("count:Q", title="응답률(%)"))
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("응답 데이터가 없습니다.")

# ====== 2) 통계(선택형/숫자/척도) ======
with tab_stats:
    st.subheader("📈 선택형·숫자형 통계")
    any_drawn = False
    for col, t in col_types.items():
        if col not in df.columns:
            continue
        if t not in {"single_choice", "multiple_choice", "linear_scale", "numeric"}:
            continue

        st.markdown(f"### 🏷 {col} · {COLUMN_TYPES.get(t, t)}")
        s = df[col].dropna().astype(str)

        # 다중선택 분해
        if t == "multiple_choice":
            s = split_multiple_choice(s)

        # 숫자/척도: 히스토그램 + 기초 통계
        if t in {"linear_scale", "numeric"}:
            nums = pd.to_numeric(s, errors="coerce").dropna()
            if nums.empty:
                st.info("유효한 숫자 데이터가 없습니다.")
                continue
            c1, c2, c3 = st.columns(3)
            c1.metric("평균", f"{nums.mean():.2f}")
            c2.metric("중앙값", f"{nums.median():.2f}")
            c3.metric("표준편차", f"{nums.std():.2f}")
            st.altair_chart(hist_chart(nums, "분포(히스토그램)"), use_container_width=True)
            any_drawn = True
        else:
            # 범주형: 상위 10 + 기타
            counts = s.value_counts()
            if counts.empty:
                st.info("응답이 없습니다.")
                continue
            counts_agg = make_top10_with_others(counts, top_n=10)
            st.altair_chart(bar_chart_from_counts(counts_agg, "상위 항목"), use_container_width=True)

            if show_pie:
                # Altair 파이(도넛) 차트
                df_pie = counts_agg.rename_axis("label").reset_index(name="count")
                pie = (
                    alt.Chart(df_pie)
                    .mark_arc(innerRadius=60)
                    .encode(theta="count:Q", color=alt.Color("label:N", legend=None), tooltip=["label:N", "count:Q"])
                    .properties(height=300)
                )
                legend = alt.Chart(df_pie).mark_rect().encode(y=alt.Y("label:N", sort="-x", title=None), color="label:N")
                st.altair_chart(pie | legend, use_container_width=True)
            any_drawn = True

    if not any_drawn:
        st.info("선택형/숫자형으로 분류된 문항이 없습니다. 상단의 ‘문항 유형 확인/수정’에서 유형을 조정해 보세요.")

# ====== 3) 텍스트 ======
with tab_text:
    st.subheader("📝 텍스트 분석(단답/장문)")
    drew_text = False
    for col, t in col_types.items():
        if col not in df.columns:
            continue
        if t not in {"text_short", "text_long"}:
            continue
        if t in SENSITIVE_TYPES:
            continue

        texts = [str(x).strip() for x in df[col].dropna() if str(x).strip()]
        if not texts:
            continue

        st.markdown(f"### 🔍 {col}")
        # 토큰화
        tokens = []
        for line in texts:
            for part in re.split(r"[,\s]+", line):
                for tok in TOK_RGX.findall(part):
                    if len(tok) >= min_token_len and tok not in STOPWORDS:
                        tokens.append(tok)

        if not tokens:
            st.info("유효한 토큰이 없습니다.")
            continue

        counts = Counter(tokens)
        top = pd.Series(dict(counts.most_common(top_k_tokens)))
        st.altair_chart(bar_chart_from_counts(top, f"상위 {len(top)} 토큰"), use_container_width=True)

        # 원문 일부 미리보기
        with st.expander("원문 일부 보기", expanded=False):
            for i, txt in enumerate(texts[:50], 1):
                st.write(f"{i}. {txt}")
        drew_text = True

    if not drew_text:
        st.info("텍스트형으로 분류된 문항이 없습니다. ‘문항 유형 확인/수정’에서 유형을 조정해 보세요.")
