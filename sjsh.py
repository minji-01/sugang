# filename: course_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="수강신청 시스템", page_icon="📘", layout="wide")

DATA_FILE = "course_applications.csv"

# -------------------------
# 초기 데이터 파일 생성
# -------------------------
BASE_COLUMNS = ["학번", "이름", "학년", "과목", "학점", "학기", "교과군", "과목유형", "전공", "제출시각"]
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=BASE_COLUMNS).to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# -------------------------
# 과목 데이터 정의
# -------------------------
courses_2nd = [
    ("수학", "진로", "고급 대수", 4, "2학기", "⭕"),
    ("수학", "진로", "고급 미적분", 4, "2학기", "⭕"),
    ("과학", "융합", "물리학 실험", 4, "2학기", "⭕"),
    ("과학", "융합", "화학 실험", 4, "2학기", "⭕"),
    ("과학", "융합", "생명과학 실험", 4, "2학기", "⭕"),
    ("과학", "융합", "지구과학 실험", 4, "2학기", "⭕"),
    ("기술가정/정보", "진로", "인공지능 일반", 3, "2학기", "⭕"),
    ("예술", "진로", "음악 감상과 비평", 3, "2학기", ""),
    ("예술", "일반", "미술", 3, "2학기", ""),
]

courses_3rd = [
    # 1학기
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
    # 2학기
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
    ("제2외국어/한문", "일반", "일본어", 4, "2학기", ""),
]

def as_df(course_list):
    return pd.DataFrame(course_list, columns=["교과군", "과목유형", "과목", "학점", "학기", "전공"])

df_2nd = as_df(courses_2nd).assign(학년="2학년")
df_3rd = as_df(courses_3rd).assign(학년="3학년")

# -------------------------
# 표 생성/스타일 함수
# -------------------------
def build_course_table(grade: str) -> pd.DataFrame:
    src = df_2nd if grade == "2학년" else df_3rd
    table = src.copy()
    table["구분"] = f"{grade} 선택"
    table["교과(군)"] = table["교과군"]
    table["전공과목 여부"] = table["전공"].replace({"⭕": "⭕", "": ""})
    # 개설되지 않은 학기 셀: 'X' 마킹 → 스타일에서 회색 처리
    table["1학기"] = table["학기"].apply(lambda x: "" if x == "1학기" else "X")
    table["2학기"] = table["학기"].apply(lambda x: "" if x == "2학기" else "X")

    view_cols = ["구분", "교과(군)", "과목유형", "과목", "학점", "전공과목 여부", "1학기", "2학기"]
    table = table[view_cols].sort_values(["교과(군)", "과목유형", "과목"]).reset_index(drop=True)
    return table

def style_semester(df: pd.DataFrame):
    def color_unavailable(val):
        return "background-color: #C7C7C7" if val == "X" else ""
    styler = (
        df.style
          .applymap(color_unavailable, subset=["1학기", "2학기"])
          .set_properties(subset=["전공과목 여부"], **{"text-align": "center"})
          .hide_index()
    )
    return styler

# -------------------------
# 검증 로직
# -------------------------
def validate_selection(selected_df: pd.DataFrame, grade: str):
    if selected_df.empty:
        return False, "최소 1과목 이상 선택해야 합니다."
    df = selected_df[selected_df["학년"] == grade].copy()
    if df.empty:
        return False, f"{grade} 과목을 최소 1과목 이상 선택해야 합니다."

    if grade == "3학년":
        # 사회 1과목 이상
        if df[df["교과군"] == "사회"].empty:
            return False, "3학년: 사회 교과에서 최소 1과목을 선택해야 합니다."
        # 정보/제2외국어 요건
        ai_selected = (df["과목"] == "인공지능 일반").any()
        info_foreign = df[df["교과군"].isin(["기술가정/정보", "제2외국어/한문"])]
        if ai_selected and len(info_foreign) < 1:
            return False, "3학년: '인공지능 일반' 선택 시 정보/제2외국어 최소 1과목 필요."
        if (not ai_selected) and len(info_foreign) < 2:
            return False, "3학년: 정보/제2외국어 과목에서 최소 2과목 필요."
        # 전공 8개 이상
        if (df["전공"] == "⭕").sum() < 8:
            return False, "3학년: 전공 과목은 최소 8개 선택해야 합니다."
        # 30학점 이상
        total_credits = df["학점"].sum()
        if total_credits < 30:
            return False, f"3학년: 최소 30학점을 선택해야 합니다. (현재 {total_credits}학점)"
    return True, "수강신청 조건을 만족합니다!"

# -------------------------
# 저장/로드
# -------------------------
def load_db():
    try:
        return pd.read_csv(DATA_FILE)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=BASE_COLUMNS)

def save_submission(student_id, name, grade, selected_df):
    db = load_db()
    mask = (db["학번"].astype(str) == str(student_id)) & (db["학년"] == grade)
    db = db[~mask].copy()  # 동일 학번·학년 덮어쓰기

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for _, r in selected_df.iterrows():
        if r["학년"] != grade:
            continue
        rows.append([student_id, name, grade, r["과목"], r["학점"], r["학기"],
                     r["교과군"], r["과목유형"], r["전공"], now])
    new_df = pd.DataFrame(rows, columns=BASE_COLUMNS)

    db = pd.concat([db, new_df], ignore_index=True)
    db.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# -------------------------
# 세션 상태(비밀번호)
# -------------------------
if "auth_student" not in st.session_state:
    st.session_state.auth_student = False
if "auth_admin" not in st.session_state:
    st.session_state.auth_admin = False

# -------------------------
# UI
# -------------------------
st.title("📘 고등학교 수강신청 시스템")
menu = st.sidebar.radio("메뉴 선택", ["학생 수강신청", "관리자 모드"])

# -------------------------
# 학생 수강신청
# -------------------------
if menu == "학생 수강신청":
    # 비밀번호 게이트 (학생)
    if not st.session_state.auth_student:
        st.info("우리 학교 학생 전용 페이지입니다. 비밀번호를 입력해 주세요.")
        pw = st.text_input("수강신청 비밀번호", type="password", placeholder="비밀번호: sjsh2025")
        if st.button("확인"):
            if pw == "sjsh2025":
                st.session_state.auth_student = True
                st.success("인증되었습니다.")
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        st.stop()

    # 전체 과목표(2/3학년 동시 표시)
    st.markdown("### 전체 과목표")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### 2학년")
        st.table(style_semester(build_course_table("2학년")))
    with colB:
        st.markdown("#### 3학년")
        st.table(style_semester(build_course_table("3학년")))
    st.markdown("---")

    # 선택 폼
    with st.form("apply_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            학번 = st.text_input("학번")
        with col2:
            이름 = st.text_input("이름")
        with col3:
            학년 = st.selectbox("학년", ["2학년", "3학년"])

        st.markdown(f"#### {학년} 과목표 (선택 기준)")
        st.table(style_semester(build_course_table(학년)))

        st.markdown("#### 과목 선택")
        course_source = (df_2nd if 학년 == "2학년" else df_3rd) \
            .sort_values(["교과군", "과목유형", "과목", "학기"]).reset_index(drop=True)

        selected_mask = []
        for idx, r in course_source.iterrows():
            label = f"{r['교과군']} - {r['과목유형']} - {r['과목']} ({r['학점']}학점, {r['학기']}) {'[전공]' if r['전공']=='⭕' else ''}"
            checked = st.checkbox(label, key=f"{학년}_{idx}")
            selected_mask.append(checked)
        selected_df = course_source[selected_mask].copy().assign(학년=학년)

        submitted = st.form_submit_button("수강신청 제출")
        if submitted:
            if not 학번 or not 이름:
                st.error("학번과 이름을 모두 입력해 주세요.")
            else:
                valid, msg = validate_selection(selected_df, 학년)
                if valid:
                    try:
                        save_submission(학번, 이름, 학년, selected_df)
                        st.success("수강신청이 완료되었습니다!")
                        st.info(msg)
                    except Exception as e:
                        st.error(f"저장 중 오류가 발생했습니다: {e}")
                else:
                    st.error(msg)

# -------------------------
# 관리자 모드
# -------------------------
else:
    # 비밀번호 게이트 (관리자)
    if not st.session_state.auth_admin:
        st.info("관리자 전용 페이지입니다. 비밀번호를 입력해 주세요.")
        pw = st.text_input("관리자 비밀번호", type="password", placeholder="비밀번호: admin9704")
        if st.button("확인", key="admin_auth"):
            if pw == "admin9704":
                st.session_state.auth_admin = True
                st.success("관리자 인증되었습니다.")
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        st.stop()

    st.subheader("📊 관리자 페이지")
    db = load_db()
    st.caption("※ 동일 학생/동일 학년 재제출 시 기존 기록을 자동 덮어씁니다.")
    st.dataframe(db, use_container_width=True, height=350)

    st.markdown("### 과목별 신청 현황")
    if db.empty:
        st.info("아직 신청 내역이 없습니다.")
    else:
        colA, colB, colC = st.columns([1, 1, 2])
        with colA:
            grade_filter = st.selectbox("학년", ["전체", "2학년", "3학년"])
        with colB:
            semester = st.selectbox("학기", ["전체", "1학기", "2학기"])
        with colC:
            show_major_only = st.toggle("전공 과목만 보기", value=False)

        df_filtered = db.copy()
        if grade_filter != "전체":
            df_filtered = df_filtered[df_filtered["학년"] == grade_filter]
        if semester != "전체":
            df_filtered = df_filtered[df_filtered["학기"] == semester]
        if show_major_only:
            df_filtered = df_filtered[df_filtered["전공"] == "⭕"]

        if df_filtered.empty:
            st.warning("조건에 해당하는 신청 내역이 없습니다.")
        else:
            summary = (
                df_filtered
                .groupby(["학년", "학기", "교과군", "과목"], as_index=False)
                .size()
                .rename(columns={"size": "신청 인원"})
            )
            st.dataframe(summary, use_container_width=True, height=300)

            fig = px.bar(
                summary,
                x="과목",
                y="신청 인원",
                color="학기",
                barmode="group",
                facet_col="학년",
                title="과목별 신청 인원",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 수강신청 내역 수정")
    edited_df = st.data_editor(db, num_rows="dynamic", use_container_width=True, height=350)
    if st.button("변경사항 저장"):
        try:
            edited_df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
            st.success("변경사항이 저장되었습니다.")
        except Exception as e:
            st.error(f"저장 실패: {e}")

    st.download_button(
        "엑셀(CSV) 파일 다운로드",
        (db if not db.empty else pd.DataFrame(columns=BASE_COLUMNS)).to_csv(index=False).encode("utf-8-sig"),
        "수강신청_내역.csv",
        "text/csv"
    )
