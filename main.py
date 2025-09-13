# app.py
import streamlit as st
import random
from datetime import datetime

st.set_page_config(
    page_title="MBTI 공부법 매칭 🎓",
    page_icon="🎓",
    layout="wide",
)

# ---------- 스타일(이모지/애니메이션/그라데이션) ----------
GRADIENTS = [
    "linear-gradient(120deg, #f6d365 0%, #fda085 100%)",
    "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)",
    "linear-gradient(120deg, #d4fc79 0%, #96e6a1 100%)",
    "linear-gradient(120deg, #f093fb 0%, #f5576c 100%)",
    "linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%)",
]

bg = random.choice(GRADIENTS)
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {bg};
        background-attachment: fixed;
    }}
    .emoji-bounce {{
        display:inline-block; animation: bounce 1.3s infinite;
    }}
    @keyframes bounce {{
        0%, 100% {{ transform: translateY(0) rotate(0deg); }}
        50% {{ transform: translateY(-6px) rotate(2deg); }}
    }}
    .glow {{
        text-shadow: 0 0 6px rgba(255,255,255,0.8);
    }}
    .card {{
        background: rgba(255, 255, 255, 0.85);
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 12px 28px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }}
    .tag {{
        display:inline-block; padding: 4px 10px; border-radius: 999px;
        background:#0000000d; margin-right:6px; margin-bottom:6px; font-size:0.9rem
    }}
    .pill {{
        display:inline-flex; align-items:center; gap:.5rem; padding:.45rem .7rem;
        border-radius:999px; background:#ffffff; border:1px solid #00000015; margin:3px;
    }}
    .tiny {{
        opacity:.8; font-size:.92rem;
    }}
    .big-emoji {{ font-size: 1.6rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- 헤더 ----------
left, right = st.columns([0.75, 0.25])
with left:
    st.markdown(
        "<h1 class='glow'>MBTI 공부법 매칭 🎓✨</h1>"
        "<div class='tiny'>성격에 딱 맞는 공부 루틴을 추천해드려요!</div>",
        unsafe_allow_html=True,
    )
with right:
    if st.button("기분전환 🎈", use_container_width=True):
        # 랜덤 효과
        random.choice([st.balloons, st.snow])()

# ---------- 데이터 ----------
MBTI_LIST = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

TIPS = {
    "INTJ": {
        "title":"전략가 🧠📈",
        "traits": ["체계적", "목표지향", "장기전략 선호"],
        "core": [
            "🎯 SMART 목표(주/월)로 역진행 계획(backcasting) 세우기",
            "📚 심화자료-핵심요약-테스트 3단 점프 학습",
            "⏱ 50분 집중 + 10분 산책 ‘딥워크 블록’"
        ],
        "avoid": ["과한 완벽주의로 시작 지연 ⛔", "혼자만 파고들다 피드백 놓치기"],
        "tools": ["Notion/Obsidian", "Anki", "Forest/Focus To-Do"],
        "env": "조용한 1인 공간 + 약한 화이트노이즈 🎧",
        "buddy": "ENFP/ENFJ와 주간 리뷰 미팅 🤝",
        "mini": ["08:00-08:15 목적 재확인",
                 "08:15-09:05 개념+정리",
                 "09:15-10:05 문제풀이",
                 "밤: 15분 복습+내일 프리뷰"]
    },
    "INTP": {
        "title":"사색가 🧪🌀",
        "traits": ["탐구형", "논리중시", "깊이 파고듦"],
        "core": [
            "❓스스로 질문 리스트 만들고 ‘왜/어떻게’ 파고들기",
            "📓 개념 연결 맵(Concept Map) 작성",
            "🧩 예제→반례→일반화 순서로 개념 견고화"
        ],
        "avoid": ["이론만 파고 실전 회피 ⛔", "완료 없이 무한 리팩토링"],
        "tools": ["Obsidian(링크드 노트)", "Excalidraw", "Khan/CS50"],
        "env": "혼자 몰입 가능한 카페 구석/서재 ☕",
        "buddy": "ESTJ와 주간 체크로 마감 책임감 ↑",
        "mini": ["AM 딥다이브 90분", "PM 문제풀이 60분", "밤 20분 요약"]
    },
    "ENTJ": {
        "title":"지휘관 🚀🗂️",
        "traits": ["리더십", "효율추구", "결단력"],
        "core": [
            "📆 주간 로드맵 + KPI(시간/문제수/점수)",
            "🧪 주 2회 모의테스트 → 지표로 전략 수정",
            "👥 스터디 리드(설명하며 배우기)"
        ],
        "avoid": ["속도만 중시해 개념 구멍 ⛔", "과도한 일정으로 번아웃"],
        "tools": ["Google Calendar", "Todoist", "Notion DB"],
        "env": "밝고 깔끔한 데스크 + 대형 모니터",
        "buddy": "ISFJ와 디테일 보완 콤보 🤝",
        "mini": ["아침 30분 계획", "오전 2블록 집중", "오후 리뷰&수정"]
    },
    "ENTP": {
        "title":"발명가 ⚡🧩",
        "traits": ["아이디어 풍부", "변화 선호", "토론 애호"],
        "core": [
            "🧠 ‘가짜 강의(Feynman)’로 개념 설명해보기",
            "🔄 과목을 교차(Interleave)해 지루함 방지",
            "🎙 스스로 토론/녹음 → 논리 점검"
        ],
        "avoid": ["새로운 것만 쫓아 기본 빵꾸 ⛔", "계획 없이 즉흥 학습"],
        "tools": ["Miro/Whimsical", "Voice Memos", "Quizlet"],
        "env": "카페/라운지 등 약간의 자극 환경",
        "buddy": "ISTJ와 체크리스트 운영",
        "mini": ["25-5 포모도로 × 6세트", "저녁 10분 하이라이트 정리"]
    },
    "INFJ": {
        "title":"옹호자 🌿🔮",
        "traits": ["의미중시", "깊이 성찰", "조용한 열정"],
        "core": [
            "💌 ‘왜 배우는가’ 가치카드 작성 후 책상에 붙이기",
            "📖 사례/비유로 개념 의미화",
            "🌙 취침 전 15분 리플렉션 저널"
        ],
        "avoid": ["감정소모로 페이스 다운 ⛔", "과한 이상화로 실행 지연"],
        "tools": ["Day One/Notion Journal", "GoodNotes", "Calm"],
        "env": "따뜻한 조명/식물/차 한 잔 공간 🍵",
        "buddy": "ENTP와 활력 보충 토론",
        "mini": ["아침 감사 3줄", "오전 집중 60분", "밤 성찰 15분"]
    },
    "INFP": {
        "title":"중재자 🎨🌈",
        "traits": ["창의", "감성", "자율성"],
        "core": [
            "🎯 ‘아주 작은 할 일’로 시작 문턱 낮추기",
            "📓 스토리텔링 요약노트(그림/색상)",
            "🎵 음악 타이머로 몰입 리듬 만들기"
        ],
        "avoid": ["기분 따라 변동 큰 루틴 ⛔", "마감 불명확"],
        "tools": ["Notion Kanban", "Flocus/Flow Timer", "Procreate/GoodNotes"],
        "env": "감성 소품+헤드폰 🎧",
        "buddy": "ESTJ와 데드라인 계약",
        "mini": ["10분 스타터 → 40분 집중", "산책 10분", "리뷰 10분"]
    },
    "ENFJ": {
        "title":"선도자 🤝🌟",
        "traits": ["사람중심", "격려", "조직화"],
        "core": [
            "👥 서로 가르치는 페어티칭",
            "🗓 체크인 미팅으로 동기 유지",
            "📣 공개 선언(친구/SNS)로 약속 효과"
        ],
        "avoid": ["남 챙기다 본인 공부 밀림 ⛔", "계획 과다 약속"],
        "tools": ["Google Sheets(학습대시보드)", "Habitica", "Zoom/Jitsi"],
        "env": "밝은 공동학습실/도서관",
        "buddy": "INTP/ISTJ로 깊이/디테일 보완",
        "mini": ["AM 그룹 45분", "PM 개인 60분", "밤 10분 피드백"]
    },
    "ENFP": {
        "title":"활동가 🎉🚴",
        "traits": ["열정", "다재다능", "새로움 추구"],
        "core": [
            "🎯 2~3개 핵심 목표만 ‘하루 집중 리스트’",
            "🔀 주제 스위칭(30~40분 단위)으로 신선도 유지",
            "🏁 ‘시작의식(Starting Ritual)’ 만들기"
        ],
        "avoid": ["시작 안 하거나 금방 딴길 ⛔", "툴만 꾸미고 공부 X"],
        "tools": ["Toggl Track", "Minimal Pomodoro", "Anki"],
        "env": "활기 있는 카페/스터디 카페",
        "buddy": "ISTJ와 체크리듬 맞추기",
        "mini": ["40-10 × 3회", "보상: 5분 춤/스트레칭 🕺"]
    },
    "ISTJ": {
        "title":"현실주의자 📋🧭",
        "traits": ["성실", "절차중시", "정밀함"],
        "core": [
            "📑 과목별 체크리스트로 확실한 완료감",
            "📆 같은 시간/자리에서 루틴 고정",
            "🧪 주간 점검표(틀린 문제 패턴 기록)"
        ],
        "avoid": ["계획에 매여 유연성 부족 ⛔", "암기 위주로 이해 소홀"],
        "tools": ["Excel/Sheets", "GoodNotes 템플릿", "Focus To-Do"],
        "env": "정돈된 데스크/책장",
        "buddy": "ENFP와 동기 부스터",
        "mini": ["21:00-23:00 고정 블록", "금: 주간 점검 20분"]
    },
    "ISFJ": {
        "title":"수호자 🧺🌼",
        "traits": ["배려", "성실", "세심함"],
        "core": [
            "📦 단원별 ‘지식 바스켓’(핵심정리+오답)",
            "🔁 소리 내어 설명하며 암기 강화",
            "🧘 짧은 스트레칭/루틴으로 안정감"
        ],
        "avoid": ["요청 거절 못해 시간 분산 ⛔", "혼자 고민만 하다 막힘"],
        "tools": ["Notion DB(오답노트)", "Voice Memos", "Stretching App"],
        "env": "조용한 집/도서관",
        "buddy": "ENTJ와 목표점검",
        "mini": ["30-5 × 4세트", "밤 15분 낭독 복습"]
    },
    "ESTJ": {
        "title":"경영자 🧱📊",
        "traits": ["실행력", "조직력", "규율"],
        "core": [
            "📈 Gantt/캘린더로 전과목 운영",
            "🧩 실전문제-오답-유형화 사이클",
            "👑 아침 루틴(책상 리셋+계획+첫 세트)"
        ],
        "avoid": ["속도 우선으로 개념 빈틈 ⛔", "윗선 지시식만 고집"],
        "tools": ["Gantt(TeamGantt)", "TickTick", "Past papers"],
        "env": "밝고 시계 보이는 자리",
        "buddy": "INFP와 창의/휴식 밸런스",
        "mini": ["아침 20분 플래닝", "50-10 × 4세트"]
    },
    "ESFJ": {
        "title":"집정관 🍰📣",
        "traits": ["협력", "실용", "조화"],
        "core": [
            "👥 스터디 운영(서로 설명/퀴즈)",
            "📌 시각적 플래너/스티커 강화",
            "📞 체크-인 파트너로 꾸준함 유지"
        ],
        "avoid": ["과한 대인활동으로 시간 소모 ⛔", "타인 기준에 맞추다 목표 흐림"],
        "tools": ["Papercal/Planner", "Quizlet", "Google Meet"],
        "env": "밝은 조명 + 큰 테이블",
        "buddy": "INTJ로 전략 보완",
        "mini": ["AM 2세트 집중", "PM 그룹퀴즈 30분"]
    },
    "ISTP": {
        "title":"장인 🛠️🏎️",
        "traits": ["문제해결", "실습선호", "침착"],
        "core": [
            "🔧 개념→즉시 실습(문제/프로젝트) 연결",
            "⏱ 타이머로 짧고 빠른 세트",
            "📓 실수노트(원인/해결/예방) 유지"
        ],
        "avoid": ["흥미 없으면 바로 이탈 ⛔", "장기 계획 소홀"],
        "tools": ["Timer/Minimal Pomodoro", "Git/Colab", "Anki Cloze"],
        "env": "메이커 감성, 넓은 책상",
        "buddy": "ENFJ로 일정 견인",
        "mini": ["25-5 × 6세트", "끝에 10분 회고"]
    },
    "ISFP": {
        "title":"모험가 🧚‍♀️📷",
        "traits": ["감각", "유연", "감성"],
        "core": [
            "🎨 색/이미지/도형으로 노트 꾸미기",
            "🎧 음악과 함께 리듬 학습",
            "🌿 짧은 야외 산책으로 재충전"
        ],
        "avoid": ["기분 따라 흐르는 일정 ⛔", "피드백 회피"],
        "tools": ["GoodNotes/Notability", "Lo-Fi Radio", "Habit tracker"],
        "env": "따뜻한 조명+식물+향",
            "buddy": "ENTJ와 목표 명료화",
        "mini": ["30-5 × 4세트", "밤 10분 하이라이트 스케치"]
    },
    "ESTP": {
        "title":"사업가 🏁📣",
        "traits": ["액션", "현장감", "경쟁심"],
        "core": [
            "🎯 시간제한 스프린트 풀이(게임화)",
            "🏆 친구와 점수 배틀/랭킹",
            "🎬 실전/사례 먼저 보고 개념 정리"
        ],
        "avoid": ["장기복습 누락 ⛔", "즉흥으로 방향 잦은 변경"],
        "tools": ["Quizizz/Kahoot", "Toggl Sprint", "Past papers"],
        "env": "활기찬 공간(적당한 소음 OK)",
        "buddy": "INFJ로 깊이/의미 보강",
        "mini": ["20-5 × 6세트", "주 2회 누적복습 30분"]
    },
    "ESFP": {
        "title":"연예인 🎤🌟",
        "traits": ["사교적", "즉흥", "감각적"],
        "core": [
            "📸 발표/녹화로 ‘보여주는 공부’",
            "👯 파트너와 퀴즈/롤플레잉",
            "🎁 보상 설계(세트 완료→간식/산책)"
        ],
        "avoid": ["즐거움만 추구해 심화 회피 ⛔", "일정 불규칙"],
        "tools": ["Flip/YouTube Shorts", "Quizlet Live", "Streaks"],
        "env": "밝고 열려있는 공간",
        "buddy": "INTJ/ISTJ로 구조 보강",
        "mini": ["25-5 × 5세트", "저녁 15분 발표연습"]
    },
}

# ---------- 사이드바 ----------
with st.sidebar:
    st.markdown("## 🧭 어떻게 쓰나요?")
    st.markdown("- MBTI 선택 → ‘맞춤 카드’ 확인\n- 공유 링크로 MBTI 미리 선택 가능")
    mbti = st.selectbox("MBTI 유형을 골라주세요", MBTI_LIST, index=MBTI_LIST.index("ENFP"))
    fancy = st.toggle("✨ 화려한 모드(이모지 강화/애니메이션)", value=True)
    st.divider()
    st.markdown("#### 🔗 공유 링크")
    st.caption("아래 버튼을 누르면 현재 선택한 MBTI가 URL 파라미터에 담겨 공유돼요.")
    if st.button("링크 업데이트"):
        st.experimental_set_query_params(mbti=mbti)
        st.toast("링크가 주소창에 반영되었어요! 📎", icon="🔗")

# 쿼리파라미터로 MBTI 세팅
params = st.experimental_get_query_params()
if "mbti" in params and params["mbti"]:
    q = params["mbti"][0].upper()
    if q in MBTI_LIST and q != mbti:
        mbti = q
        st.session_state["_mbti_from_query"] = True
        st.toast(f"공유 링크로 {mbti}가 선택되었어요! ✨", icon="✅")

# ---------- 본문 ----------
card = TIPS.get(mbti, None)

if fancy and random.random() < 0.33:
    st.balloons()
elif fancy and datetime.now().month in [12,1,2] and random.random() < 0.2:
    st.snow()

top_l, top_r = st.columns([0.65, 0.35])
with top_l:
    st.markdown(
        f"<div class='card'>"
        f"<h2 class='glow'>[{mbti}] {card['title']} <span class='emoji-bounce'>📚✨</span></h2>"
        f"<div class='tiny'><span class='tag'>성향</span> "
        + " ".join(f"<span class='pill'><span class='big-emoji'>🔹</span>{t}</span>" for t in card["traits"])
        + "</div></div>",
        unsafe_allow_html=True,
    )

with top_r:
    st.metric(label="오늘의 집중 세트", value=f"{random.randint(3,6)} 세트", delta=f"+{random.randint(1,3)} 권장")
    st.metric(label="권장 휴식", value=f"{random.choice([5,10,15])}분", delta="세트 사이 휴식")
    st.caption("작게 자주 쉬면 더 오래 달릴 수 있어요 💪")

st.markdown("### 🧠 핵심 공부법")
with st.container():
    cols = st.columns(3)
    for i, tip in enumerate(card["core"]):
        with cols[i % 3]:
            st.markdown(f"<div class='card'><h4>Tip {i+1} 💡</h4><p>{tip}</p></div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("### 🧰 추천 도구 & 🏕️ 환경")
    st.markdown(
        f"<div class='card'><b>도구</b> — " + "、".join(card["tools"]) +
        f"<br><b>환경</b> — {card['env']}</div>",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown("### 🙅 피하면 좋아요")
    st.markdown(
        f"<div class='card'>" + " · ".join(card["avoid"]) + "</div>",
        unsafe_allow_html=True,
    )

st.markdown("### 🤜🤛 스터디 궁합")
st.markdown(
    f"<div class='card'>{card['buddy']}</div>",
    unsafe_allow_html=True,
)

with st.expander("⏱️ 미니 타임테이블 보기"):
    st.markdown(
        "<div class='card'>" +
        "<br>".join(f"• {slot}" for slot in card["mini"]) +
        "</div>",
        unsafe_allow_html=True,
    )

# ---------- 다운로드(메모/플랜) ----------
def make_md(m):
    c = TIPS[m]
    out = [
        f"# {m} 공부 플랜",
        f"**타입 이름:** {c['title']}",
        f"**성향:** {', '.join(c['traits'])}",
        "## 핵심 공부법",
        *[f"- {t}" for t in c["core"]],
        "## 피하면 좋은 습관",
        *[f"- {a}" for a in c["avoid"]],
        "## 추천 도구",
        f"- " + ", ".join(c["tools"]),
        "## 학습 환경",
        f"- {c['env']}",
        "## 스터디 궁합",
        f"- {c['buddy']}",
        "## 미니 타임테이블",
        *[f"- {s}" for s in c["mini"]],
    ]
    return "\n".join(out)

dl_col1, dl_col2 = st.columns([0.6, 0.4])
with dl_col1:
    st.markdown("### 📝 내 기기 저장")
with dl_col2:
    st.download_button(
        label="Markdown으로 저장 ⬇️",
        data=make_md(mbti),
        file_name=f"{mbti}_study_plan.md",
        mime="text/markdown",
        use_container_width=True
    )

# ---------- 재미 요소: 랜덤 칭찬 & 진행 위젯 ----------
st.markdown("### 🌟 오늘의 칭찬 한 스푼")
praise = random.choice([
    "작게라도 시작한 당신, 이미 절반은 했다! 🏁",
    "집중 20분 = 미래의 자신에게 보낸 선물 🎁",
    "완벽보다 완료! Done is better than perfect. ✅",
    "오늘의 꾸준함이 내일의 실력을 만든다 📈",
    "배운 것을 한 번 더 설명하면 두 배가 된다 🎤",
])
st.success(praise)

with st.container():
    st.markdown("### 🎯 오늘의 목표 진행")
    goal = st.slider("오늘 목표 세트 수(25~50분 기준)", 1, 10, value=random.randint(3,6))
    done = st.number_input("완료한 세트 수", min_value=0, max_value=10, value=0, step=1)
    prog = min(max(done/goal, 0), 1)
    st.progress(prog)
    if prog >= 1:
        st.toast("목표 달성! 대단해요! 🥳", icon="🎉")
        if fancy:
            st.balloons()

# 푸터
st.caption("💡 팁: 사이드바에서 링크 업데이트 → MBTI가 포함된 URL로 공유할 수 있어요.")
