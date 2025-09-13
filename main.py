import streamlit as st
import pandas as pd
import altair as alt

# CSV 불러오기
df = pd.read_csv("countriesMBTI_16types.csv")

st.title("🌍 국가별 MBTI 유형 비율 Top 10")
st.write("업로드한 CSV 데이터를 바탕으로, 선택한 MBTI 유형의 비율이 가장 높은 국가 10개를 확인할 수 있습니다.")

# MBTI 유형 선택
mbti_types = [col for col in df.columns if col != "Country"]
selected_type = st.selectbox("MBTI 유형을 선택하세요:", mbti_types)

# 선택된 유형 기준 Top 10 국가 추출
top10 = df[["Country", selected_type]].sort_values(by=selected_type, ascending=False).head(10)

# Altair 그래프
chart = (
    alt.Chart(top10)
    .mark_bar()
    .encode(
        x=alt.X(selected_type, title="비율", scale=alt.Scale(domain=[0, top10[selected_type].max()*1.1])),
        y=alt.Y("Country", sort="-x", title="국가"),
        tooltip=["Country", selected_type]
    )
    .interactive()
    .properties(
        width=600,
        height=400,
        title=f"{selected_type} 유형 비율 Top 10 국가"
    )
)

st.altair_chart(chart, use_container_width=True)

# 데이터도 같이 표시
st.subheader("📊 데이터 미리보기")
st.dataframe(top10)
