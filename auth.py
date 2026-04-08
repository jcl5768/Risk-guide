# auth.py — 로그인 / 회원가입 화면

import streamlit as st
import requests
import json


# ── Firebase REST API 키 (Secrets에서 가져옴) ────────────────────────────────
def _get_api_key() -> str:
    try:
        return st.secrets["firebase_web"]["api_key"]
    except Exception:
        return ""


# ── 이메일/비밀번호 로그인 ────────────────────────────────────────────────────
def _email_login(email: str, password: str) -> dict | None:
    api_key = _get_api_key()
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    try:
        res = requests.post(url, json={
            "email": email, "password": password, "returnSecureToken": True
        }, timeout=10)
        data = res.json()
        if "error" in data:
            return {"error": data["error"].get("message", "로그인 실패")}
        return data
    except Exception as e:
        return {"error": str(e)}


# ── 이메일/비밀번호 회원가입 ─────────────────────────────────────────────────
def _email_signup(email: str, password: str) -> dict | None:
    api_key = _get_api_key()
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    try:
        res = requests.post(url, json={
            "email": email, "password": password, "returnSecureToken": True
        }, timeout=10)
        data = res.json()
        if "error" in data:
            return {"error": data["error"].get("message", "회원가입 실패")}
        return data
    except Exception as e:
        return {"error": str(e)}


# ── 에러 메시지 한국어 변환 ───────────────────────────────────────────────────
def _korean_error(msg: str) -> str:
    table = {
        "EMAIL_NOT_FOUND":       "존재하지 않는 이메일이에요.",
        "INVALID_PASSWORD":      "비밀번호가 틀렸어요.",
        "INVALID_LOGIN_CREDENTIALS": "이메일 또는 비밀번호가 틀렸어요.",
        "EMAIL_EXISTS":          "이미 사용 중인 이메일이에요.",
        "WEAK_PASSWORD":         "비밀번호는 6자 이상이어야 해요.",
        "MISSING_PASSWORD":      "비밀번호를 입력해주세요.",
        "INVALID_EMAIL":         "이메일 형식이 올바르지 않아요.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "잠시 후 다시 시도해주세요.",
    }
    for k, v in table.items():
        if k in msg:
            return v
    return msg


# ── 로그인 화면 렌더링 ────────────────────────────────────────────────────────
def render_auth_page():
    st.markdown(
        '<div style="text-align:center;padding:32px 0 16px;">'
        '<div style="font-size:36px;">🔭</div>'
        '<div style="font-size:24px;font-weight:700;color:#1A1D23;margin-top:8px;">Signum</div>'
        '<div style="font-size:13px;color:#6B7280;margin-top:4px;">시장 신호 기반 포트폴리오 분석</div>'
        '</div>',
        unsafe_allow_html=True
    )

    tab_login, tab_signup = st.tabs(["🔑 로그인", "✏️ 회원가입"])

    # ── 로그인 탭 ─────────────────────────────────────────────────────
    with tab_login:
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        email    = st.text_input("이메일", placeholder="example@email.com", key="login_email")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력", key="login_pw")

        if st.button("로그인", use_container_width=True, type="primary", key="btn_login"):
            if not email or not password:
                st.error("이메일과 비밀번호를 입력해주세요.")
            else:
                with st.spinner("로그인 중..."):
                    result = _email_login(email.strip(), password)
                if result and "error" not in result:
                    st.session_state.user = {
                        "uid":   result["localId"],
                        "email": result["email"],
                        "token": result["idToken"],
                    }
                    st.success("로그인 성공!")
                    st.rerun()
                else:
                    err = result.get("error", "알 수 없는 오류") if result else "연결 실패"
                    st.error(_korean_error(err))

        st.markdown(
            '<div style="text-align:center;font-size:11px;color:#9CA3AF;margin-top:8px;">'
            'Google 로그인은 준비 중이에요</div>',
            unsafe_allow_html=True
        )

    # ── 회원가입 탭 ───────────────────────────────────────────────────
    with tab_signup:
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        su_email = st.text_input("이메일", placeholder="example@email.com", key="su_email")
        su_pw    = st.text_input("비밀번호", type="password", placeholder="6자 이상", key="su_pw")
        su_pw2   = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호 재입력", key="su_pw2")

        if st.button("회원가입", use_container_width=True, type="primary", key="btn_signup"):
            if not su_email or not su_pw or not su_pw2:
                st.error("모든 항목을 입력해주세요.")
            elif su_pw != su_pw2:
                st.error("비밀번호가 일치하지 않아요.")
            elif len(su_pw) < 6:
                st.error("비밀번호는 6자 이상이어야 해요.")
            else:
                with st.spinner("계정 생성 중..."):
                    result = _email_signup(su_email.strip(), su_pw)
                if result and "error" not in result:
                    st.session_state.user = {
                        "uid":   result["localId"],
                        "email": result["email"],
                        "token": result["idToken"],
                    }
                    st.success("가입 완료! 자동 로그인됐어요.")
                    st.rerun()
                else:
                    err = result.get("error", "알 수 없는 오류") if result else "연결 실패"
                    st.error(_korean_error(err))

    st.markdown(
        '<div style="text-align:center;font-size:10px;color:#D1D5DB;margin-top:24px;">'
        'Signum · 개인 포트폴리오 리스크 분석 도구</div>',
        unsafe_allow_html=True
    )
