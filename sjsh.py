import streamlit as st
import pandas as pd
import plotly.express as px
import os

DATA_FILE = "course_applications.csv"

# -------------------------
# 초기 데이터 파일 생성
# -------------------------
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["학번", "이름", "학년", "과목", "학점", "학기", "교과군", "전공"]).to_csv(DATA_FILE, index=False)

# -------------------------
# 과목 데이터 정의
# -------------------------
courses_2nd = [
    ("수학", "진로", "고급 대수", 3, "2학기", "⭕"),
    ("수학", "진로", "고급 미적분", 3, "2학기", "⭕"),
    ("과학", "융합", "물리학 실험", 3, "2학기", "⭕"),
    ("과학", "융합", "화학 실험", 3, "2학기", "⭕"),
    ("과학", "융합", "생명과학 실험", 3, "2학기", "⭕"),
    ("과학", "융합", "지구과학 실험", 3, "2학기", "⭕"),
    ("기술가정/정보", "진로", "인공지능 일반", 3, "2학기", "⭕"),
    ("예술", "진로", "음악 감상과 비평", 3, "2학기", ""),
    ("예술", "일반", "미술", 3, "2학기", "")
]

courses_3rd = [
    # 1학기 과목
    ("국어", "일반", "독서와 작문", 4, "1학기", ""),
    ("영어", "일반", "영어 독해와 작문", 4, "1학기", ""),
    ("수학", "일반", "확률과 통계", 4, "1학기", ""),
    ("수학", "진로", "AP미적분학Ⅰ", 4, "1학기", "⭕"),
    ("과학", "진로", "AP일반물리Ⅰ", 4, "1학기", "⭕"),
    ("과학", "진로", "AP일반화학Ⅰ", 4, "1학기", "⭕"),
    ("과학", "진로", "AP일반생물학Ⅰ", 4, "1학기", "⭕"),
    ("과학", "진로", "천문학 세미나", 4, "1학기", "⭕"),
    ("기술가정/정보", "진로", "정보 과제 연구", 4, "1학기", "⭕"),
    ("사회", "융합", "사회문제 탐구", 4, "1학기", ""),
    ("제2외국어/한문", "일반", "중국어", 4, "1학기", ""),
    ("제2외국어/한문", "일반", "일본어", 4, "1학기", ""),

    # 2학기 과목
    ("국어", "진로", "문학과 영상", 3, "2학기", ""),
    ("영어", "진로", "심화 영어 독해와 작문", 3, "2학기", ""),
    ("수학", "진로", "기하", 4, "2학기", ""),
    ("수학", "진로", "이산 수학", 4, "2학기", "⭕"),
    ("과학", "진로", "AP일반물리Ⅱ", 4, "2학기", "⭕"),
    ("과학", "진로", "AP일반화학Ⅱ", 4, "2학기", "⭕"),
    ("과학", "진로", "인간생활과 생명과학", 4, "2학기", "⭕"),
    ("과학", "진로", "지구과학개론", 4, "2학기", "⭕"),
    ("기술가정/정보", "융합", "소프트웨어와 생활", 4, "2학기", ""),
    ("사회", "융합", "기후변화와 지속가능한 세계", 4, "2학기", ""),
    ("제2외국어/한문", "일반", "중국어", 4, "2학기", ""),
    ("제2외국어/한문", "일반", "일본어", 4, "2학기", "")
]

# -------------------------
# 검증 로직
# -------------------------
def validate_selection(selected_courses):
    if len(selected_courses) == 0:
        return False, "최소 1과목 이상 선택해야 합니다."
    
    df = pd.DataFrame(selected_courses, columns=["교과군", "과목유형", "과목", "학점", "학기", "전공"])
    total_credits = df["학점"].sum()

    # 1. 사회 필수
    social_courses = df[df["교과군"] == "사회"]
    if social_courses.empty:
        return False, "사회 교과에서 최소 1과목을 선택해야 합니다."

    # 2. 정보/제2외국어 필수
    ai_selected = any(df["과목"] == "인공지능 일반")
    info_foreign = df[df["교과군"].isin(["기술가정/정보", "제2외국어/한문"])]
    if ai_selected and len(info_foreign) < 1:
        return False, "인공지능 일반을 선택했으므로 정보/제2외국어 과목에서 최소 1과목 선택 필요"
    if not ai_selected and len(info_foreign) < 2:
        return False, "정보/제2외국어 과목에서 최소 2과목 선택 필요"

    # 3. 전공 과목 최소 8개
    major_courses = df[df["전공"] == "⭕"]
    if len(major_courses) < 8:
        return False, "전공 과목은 최소 8개 선택해야 합니다."

    if total_credits < 30:
        return False, "3학년에서 최소 30학점을 선택해야 합니다."

    return True, "수강신청 조건을 만족합니다!"

# -------------------------
# Streamlit UI
# -------------------------
st.title("📘 고등학교 수강신청 시스템")

menu = st.sidebar.radio("메뉴 선택", ["학생 수강신청", "관리자 모드"])

# -------------------------
# 학생 수강신청 모드
# -------------------------
if menu == "학생 수강신청":
    학번 = st.text_input("학번")
    이름 = st.text_input("이름")
    학년 = st.selectbox("학년", ["2학년", "3학년"])

    if 학번 and 이름:
        selected = []

        st.subheader("2학년 선택과목")
        for idx, c in enumerate(courses_2nd):
            if st.checkbox(f"{c[0]}-{c[1]}-{c[2]} ({c[3]}학점) {c[5]}", key=f"2_{idx}"):
                selected.append(c)

        st.subheader("3학년 선택과목")
        for idx, c in enumerate(courses_3rd):
            if st.checkbox(f"{c[0]}-{c[1]}-{c[2]} ({c[3]}학점) {c[5]}", key=f"3_{idx}"):
                selected.append(c)

        if st.button("수강신청 제출"):
            valid, msg = validate_selection(selected)
            if valid:
                try:
                    df = pd.read_csv(DATA_FILE)
                except pd.errors.EmptyDataError:
                    df = pd.DataFrame(columns=["학번", "이름", "학년", "과목", "학점", "학기", "교과군", "전공"])
                
                for c in selected:
                    new_row = [학번, 이름, 학년, c[2], c[3], c[4], c[0], c[5]]
                    df.loc[len(df)] = new_row
                df.to_csv(DATA_FILE, index=False)
                st.success("수강신청이 완료되었습니다!")
            else:
                st.error(msg)

# -------------------------
# 관리자 모드
# -------------------------
else:
    st.subheader("📊 관리자 페이지")

    try:
        df = pd.read_csv(DATA_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["학번", "이름", "학년", "과목", "학점", "학기", "교과군", "전공"])

    st.dataframe(df)

    st.subheader("과목별 신청 현황")
    semester = st.selectbox("학기 선택", ["전체", "1학기", "2학기"])
    if semester != "전체":
        df_filtered = df[df["학기"] == semester]
    else:
        df_filtered = df.copy()

    if not df_filtered.empty:
        summary = df_filtered.groupby(["과목", "학기"]).size().reset_index(name="신청 인원")
        st.dataframe(summary)
        fig = px.bar(summary, x="과목", y="신청 인원", color="학기", title="과목별 신청 인원")
        st.plotly_chart(fig)

    st.subheader("수강신청 내역 수정")
    edited_df = st.data_editor(df, num_rows="dynamic")
    if st.button("변경사항 저장"):
        edited_df.to_csv(DATA_FILE, index=False)
        st.success("변경사항이 저장되었습니다.")

    st.download_button("엑셀 파일 다운로드", df.to_csv(index=False).encode("utf-8-sig"),
                       "수강신청_내역.csv", "text/csv")
