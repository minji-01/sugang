# filename: course_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="수강신청 시스템", page_icon="📘", layout="wide")

DATA_FILE = "course_applications.csv"
BASE_COLUMNS = ["학번","이름","학년","과목","학점","학기","교과군","과목유형","전공","제출시각"]

if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=BASE_COLUMNS).to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# -------------------------
# 과목 데이터
# -------------------------
courses_2nd = [
    ("수학","진로","고급 대수",3,"2학기","⭕"),
    ("수학","진로","고급 미적분",3,"2학기","⭕"),
    ("과학","융합","물리학 실험",3,"2학기","⭕"),
    ("과학","융합","화학 실험",3,"2학기","⭕"),
    ("과학","융합","생명과학 실험",3,"2학기","⭕"),
    ("과학","융합","지구과학 실험",3,"2학기","⭕"),
    ("기술가정/정보","진로","인공지능 일반",3,"2학기","⭕"),
    ("예술","진로","음악 감상과 비평",3,"2학기",""),
    ("예술","일반","미술",3,"2학기",""),
]
courses_3rd = [
    ("국어","일반","독서와 작문",4,"1학기",""),
    ("영어","일반","영어 독해와 작문",4,"1학기",""),
    ("수학","일반","확률과 통계",4,"1학기",""),
    ("수학","진로","AP미적분학Ⅰ",4,"1학기","⭕"),
    ("과학","진로","AP일반물리Ⅰ",4,"1학기","⭕"),
    ("과학","진로","AP일반화학Ⅰ",4,"1학기","⭕"),
    ("과학","진로","AP일반생물학Ⅰ",4,"1학기","⭕"),
    ("과학","진로","천문학 세미나",4,"1학기","⭕"),
    ("기술가정/정보","진로","정보 과제 연구",4,"1학기","⭕"),
    ("사회","융합","사회문제 탐구",4,"1학기",""),
    ("제2외국어/한문","일반","중국어",4,"1학기",""),
    ("제2외국어/한문","일반","일본어",4,"1학기",""),
    ("국어","진로","문학과 영상",3,"2학기",""),
    ("영어","진로","심화 영어 독해와 작문",3,"2학기",""),
    ("수학","진로","기하",4,"2학기",""),
    ("수학","진로","이산 수학",4,"2학기","⭕"),
    ("과학","진로","AP일반물리Ⅱ",4,"2학기","⭕"),
    ("과학","진로","AP일반화학Ⅱ",4,"2학기","⭕"),
    ("과학","진로","인간생활과 생명과학",4,"2학기","⭕"),
    ("과학","진로","지구과학개론",4,"2학기","⭕"),
    ("기술가정/정보","융합","소프트웨어와 생활",4,"2학기",""),
    ("사회","융합","기후변화와 지속가능한 세계",4,"2학기",""),
    ("제2외국어/한문","일반","중국어",4,"2학기",""),
    ("제2외국어/한문","일반","일본어",4,"2학기",""),
]

def df_with_grade(lst, grade):
    df = pd.DataFrame(lst, columns=["교과군","과목유형","과목","학점","학기","전공"])
    df["학년"] = grade
    df["구분"] = f"{grade} 선택"
    df["교과(군)"] = df["교과군"]
    df["전공과목 여부"] = df["전공"].replace({"⭕":"⭕","":""})
    return df

df2_base = df_with_grade(courses_2nd, "2학년")
df3_base = df_with_grade(courses_3rd, "3학년")

# -------------------------
# 보기용(색만) 표
# -------------------------
def build_catalog():
    cat = pd.concat([df2_base, df3_base], ignore_index=True)
    cat = cat[["구분","교과(군)","과목유형","과목","학점","전공과목 여부","학기","학년"]].copy()
    # 2-1, 2-2, 3-1, 3-2 컬럼
    for c in ["2학년 1학기","2학년 2학기","3학년 1학기","3학년 2학기"]:
        cat[c] = ""
    cat = cat.sort_values(["구분","교과(군)","과목유형","과목"]).reset_index(drop=True)
    return cat

def style_catalog(df: pd.DataFrame):
    Y1, Y2, R1, R2, G = "#FFE08C", "#FFD24D", "#F5A3A3", "#E88080", "#E6E6E6"
    def colorize(row):
        if row["구분"].startswith("2학년"):
            c = [Y1 if row["학기"]=="1학기" else G,
                 Y2 if row["학기"]=="2학기" else G,
                 G, G]
        else:
            c = [G, G,
                 R1 if row["학기"]=="1학기" else G,
                 R2 if row["학기"]=="2학기" else G]
        return [""]*6 + [f"background-color: {c[0]}", f"background-color: {c[1]}",
                         f"background-color: {c[2]}", f"background-color: {c[3]}"]
    cols = ["구분","교과(군)","과목유형","과목","학점","전공과목 여부",
            "2학년 1학기","2학년 2학기","3학년 1학기","3학년 2학기"]
    dfv = df[cols].copy()
    styler = (dfv.style
                .apply(lambda r: colorize(r), axis=1,
                       subset=["2학년 1학기","2학년 2학기","3학년 1학기","3학년 2학기"])
                .set_properties(subset=["전공과목 여부"], **{"text-align":"center"}))
    if hasattr(styler,"hide_index"): styler = styler.hide_index()
    return styler

# -------------------------
# 선택용 표(해당 학년만 체크 가능)
# -------------------------
def make_selectable(df_base: pd.DataFrame):
    df = df_base.copy()
    df["선택"] = False
    # 학기 정보(텍스트만, 체크/아이콘 없음)
    df["2학년 1학기"] = df.apply(lambda r: "개설" if (r["학년"]=="2학년" and r["학기"]=="1학기") else "", axis=1)
    df["2학년 2학기"] = df.apply(lambda r: "개설" if (r["학년"]=="2학년" and r["학기"]=="2학기") else "", axis=1)
    df["3학년 1학기"] = df.apply(lambda r: "개설" if (r["학년"]=="3학년" and r["학기"]=="1학기") else "", axis=1)
    df["3학년 2학기"] = df.apply(lambda r: "개설" if (r["학년"]=="3학년" and r["학기"]=="2학기") else "", axis=1)
    view_cols = ["선택","구분","교과(군)","과목유형","과목","학점","전공과목 여부",
                 "2학년 1학기","2학년 2학기","3학년 1학기","3학년 2학기",
                 "학기","교과군","전공","학년"]
    return df[view_cols].sort_values(["교과(군)","과목유형","과목"]).reset_index(drop=True)

df2_select = make_selectable(df2_base)
df3_select = make_selectable(df3_base)

# -------------------------
# 검증(3학년 규정)
# -------------------------
def validate_selection(selected_df: pd.DataFrame, grade: str):
    if selected_df.empty:
        return False, "최소 1과목 이상 선택해야 합니다."
    df = selected_df[selected_df["학년"] == grade]
    if df.empty:
        return False, f"{grade} 과목을 최소 1과목 이상 선택해야 합니다."
    if grade == "3학년":
        if df[df["교과군"]=="사회"].empty:
            return False, "3학년: 사회 교과에서 최소 1과목을 선택해야 합니다."
        ai_selected = (df["과목"]=="인공지능 일반").any()
        info_foreign = df[df["교과군"].isin(["기술가정/정보","제2외국어/한문"])]
        if ai_selected and len(info_foreign) < 1:
            return False, "3학년: '인공지능 일반' 선택 시 정보/제2외국어 최소 1과목 필요."
        if (not ai_selected) and len(info_foreign) < 2:
            return False, "3학년: 정보/제2외국어 과목에서 최소 2과목 필요."
        if (df["전공"]=="⭕").sum() < 8:
            return False, "3학년: 전공 과목은 최소 8개 선택해야 합니다."
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
    mask = (db["학번"].astype(str)==str(student_id)) & (db["학년"]==grade)
    db = db[~mask].copy()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for _, r in selected_df.iterrows():
        if r["학년"] != grade:
            continue
        rows.append([student_id, name, grade, r["과목"], int(r["학점"]), r["학기"],
                     r["교과군"], r["과목유형"], r["전공"], now])
    new_df = pd.DataFrame(rows, columns=BASE_COLUMNS)
    db = pd.concat([db, new_df], ignore_index=True)
    db.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# -------------------------
# 세션 상태
# -------------------------
if "auth_student" not in st.session_state: st.session_state.auth_student = False
if "auth_admin" not in st.session_state:   st.session_state.auth_admin   = False
if "student_meta" not in st.session_state: st.session_state.student_meta = {"학번":"","이름":"","학년":""}

st.title("📘 고등학교 수강신청 시스템")
menu = st.sidebar.radio("메뉴 선택", ["학생 수강신청", "관리자 모드"])

# =========================
# ① 학생: 암호 입력 → ② 학번·이름·학년 → ③ 체크 → ④ 확인
# =========================
if menu == "학생 수강신청":
    # ① 암호
    if not st.session_state.auth_student:
        st.info("우리 학교 학생 전용 페이지입니다. 비밀번호를 입력해 주세요.")
        pw = st.text_input("수강신청 비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        if st.button("확인", key="btn_student_auth"):
            if pw == "sjsh2025":
                st.session_state.auth_student = True
                st.success("인증되었습니다.")
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        st.stop()

    # ② 학번·이름·학년
    st.markdown("### 학생 정보 입력")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:  st.session_state.student_meta["학번"] = st.text_input("학번", value=st.session_state.student_meta["학번"])
    with col2:  st.session_state.student_meta["이름"] = st.text_input("이름", value=st.session_state.student_meta["이름"])
    with col3:  st.session_state.student_meta["학년"] = st.selectbox("학년", ["2학년","3학년"],
                                                  index=0 if st.session_state.student_meta["학년"]!="3학년" else 1)
    student_grade = st.session_state.student_meta["학년"]
    st.markdown("---")

    # ③ 과목 표에서 체크 (선택 학년=편집 표, 다른 학년=보기용 표) — 세로 배치
    st.markdown("### 과목 개설 현황 (보기용)")
    st.table(style_catalog(build_catalog()))

    st.markdown(f"### {student_grade} 수강 과목 선택")
    # 편집 가능한 표(선택 학년만)
    if student_grade == "2학년":
        edited = st.data_editor(
            make_selectable(df2_base), hide_index=True, use_container_width=True, key="edit_selected_grade",
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", help="수강할 과목을 체크"),
                "학점": st.column_config.NumberColumn("학점", step=1, disabled=True),
                "전공과목 여부": st.column_config.TextColumn("전공과목 여부", disabled=True),
                "2학년 1학기": st.column_config.TextColumn("2학년 1학기", disabled=True),
                "2학년 2학기": st.column_config.TextColumn("2학년 2학기", disabled=True),
                "3학년 1학기": st.column_config.TextColumn("3학년 1학기", disabled=True),
                "3학년 2학기": st.column_config.TextColumn("3학년 2학기", disabled=True),
                "구분": st.column_config.TextColumn("구분", disabled=True),
                "교과(군)": st.column_config.TextColumn("교과(군)", disabled=True),
                "과목유형": st.column_config.TextColumn("과목유형", disabled=True),
                "과목": st.column_config.TextColumn("과목", disabled=True),
                "학기": st.column_config.TextColumn("학기", disabled=True),
                "교과군": st.column_config.TextColumn("교과군", disabled=True),
                "전공": st.column_config.TextColumn("전공", disabled=True),
                "학년": st.column_config.TextColumn("학년", disabled=True),
            },
        )
        other_view = style_catalog(build_catalog()[lambda d: d["구분"].str.startswith("3학년")])
        st.markdown("#### 3학년 과목(보기용)")
        st.table(other_view)
    else:
        edited = st.data_editor(
            make_selectable(df3_base), hide_index=True, use_container_width=True, key="edit_selected_grade",
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", help="수강할 과목을 체크"),
                "학점": st.column_config.NumberColumn("학점", step=1, disabled=True),
                "전공과목 여부": st.column_config.TextColumn("전공과목 여부", disabled=True),
                "2학년 1학기": st.column_config.TextColumn("2학년 1학기", disabled=True),
                "2학년 2학기": st.column_config.TextColumn("2학년 2학기", disabled=True),
                "3학년 1학기": st.column_config.TextColumn("3학년 1학기", disabled=True),
                "3학년 2학기": st.column_config.TextColumn("3학년 2학기", disabled=True),
                "구분": st.column_config.TextColumn("구분", disabled=True),
                "교과(군)": st.column_config.TextColumn("교과(군)", disabled=True),
                "과목유형": st.column_config.TextColumn("과목유형", disabled=True),
                "과목": st.column_config.TextColumn("과목", disabled=True),
                "학기": st.column_config.TextColumn("학기", disabled=True),
                "교과군": st.column_config.TextColumn("교과군", disabled=True),
                "전공": st.column_config.TextColumn("전공", disabled=True),
                "학년": st.column_config.TextColumn("학년", disabled=True),
            },
        )
        other_view = style_catalog(build_catalog()[lambda d: d["구분"].str.startswith("2학년")])
        st.markdown("#### 2학년 과목(보기용)")
        st.table(other_view)

    # ④ 제출 & 확인
    with st.form("apply_form"):
        submit = st.form_submit_button("수강신청 제출")
        if submit:
            sid = st.session_state.student_meta["학번"].strip()
            name = st.session_state.student_meta["이름"].strip()
            grade = st.session_state.student_meta["학년"]
            if not sid or not name:
                st.error("학번과 이름을 모두 입력해 주세요.")
            else:
                picks = pd.DataFrame(edited)
                selected = picks[(picks["선택"]==True) & (picks["학년"]==grade)].copy()
                if not selected.empty:
                    selected = selected.rename(columns={"교과(군)":"교과군"})
                valid, msg = validate_selection(selected, grade)
                if valid:
                    try:
                        save_submission(sid, name, grade, selected)
                        st.success("수강신청이 완료되었습니다!")
                        st.info(msg)
                        # 확인표
                        confirm = selected[["교과군","과목유형","과목","학점","학기","전공"]]\
                                  .sort_values(["교과군","과목유형","과목"]).reset_index(drop=True)
                        st.markdown("### ✅ 제출 과목 확인")
                        st.dataframe(confirm, use_container_width=True)
                        st.write(f"**총 학점:** {int(confirm['학점'].sum())}학점")
                    except Exception as e:
                        st.error(f"저장 중 오류가 발생했습니다: {e}")
                else:
                    st.error(msg)

# =========================
# 관리자 모드
# =========================
else:
    if not st.session_state.auth_admin:
        st.info("관리자 전용 페이지입니다. 비밀번호를 입력해 주세요.")
        pw = st.text_input("관리자 비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        if st.button("확인", key="btn_admin_auth"):
            if pw == "admin9704":
                st.session_state.auth_admin = True
                st.success("관리자 인증되었습니다.")
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        st.stop()

    st.subheader("📊 관리자 페이지")

    db = load_db()
    st.caption("※ 동일 학생/동일 학년 재제출 시 기존 기록을 자동 덮어씁니다.")
    st.dataframe(db, use_container_width=True, height=300)

    # 과목별 수강자 수 표 (요청 사항)
    st.markdown("### 과목별 수강자 수")
    if db.empty:
        st.info("아직 신청 내역이 없습니다.")
    else:
        counts = (
            db.groupby(["학년","학기","교과군","과목","전공"], as_index=False)
              .size()
              .rename(columns={"size":"신청 인원"})
              .sort_values(["학년","학기","교과군","과목"])
        )
        st.dataframe(counts, use_container_width=True, height=320)

        # 보조 시각화(선택): 막대그래프
        fig = px.bar(counts, x="과목", y="신청 인원", color="학기",
                     facet_col="학년", barmode="group", title="과목별 신청 인원")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 수강신청 내역 수정")
    edited_db = st.data_editor(db, num_rows="dynamic", use_container_width=True, height=300)
    if st.button("변경사항 저장"):
        try:
            edited_db.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
            st.success("변경사항이 저장되었습니다.")
        except Exception as e:
            st.error(f"저장 실패: {e}")

    st.download_button(
        "엑셀(CSV) 파일 다운로드",
        (db if not db.empty else pd.DataFrame(columns=BASE_COLUMNS)).to_csv(index=False).encode("utf-8-sig"),
        "수강신청_내역.csv", "text/csv"
    )
