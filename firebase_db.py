# firebase_db.py — Firestore 저장/불러오기 (디버그 버전)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import base64
import json


def _get_db():
    try:
        app = firebase_admin.get_app()
    except ValueError:
        # try-except 없이 날것의 에러 그대로 노출
        b64 = st.secrets["firebase"]["json_base64"]
        key_dict = json.loads(base64.b64decode(b64).decode("utf-8"))
        cred = credentials.Certificate(key_dict)
        app = firebase_admin.initialize_app(cred)

    return firestore.client()


def save_portfolio(uid: str, portfolio: list) -> bool:
    try:
        db = _get_db()
        db.collection("users").document(uid).set(
            {"portfolio": portfolio, "updated_at": datetime.utcnow()},
            merge=True
        )
        st.sidebar.success("☁ 저장됨!")
        return True
    except Exception as e:
        st.sidebar.error(f"저장 실패: {e}")
        return False


def load_portfolio(uid: str) -> list:
    try:
        db = _get_db()
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict().get("portfolio", [])
        return []
    except Exception as e:
        st.sidebar.error(f"불러오기 실패: {e}")
        return []


def save_signal_history(uid: str, ticker: str, win_rate: float, price: float):
    try:
        db = _get_db()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        db.collection("users").document(uid)\
          .collection("signal_history").document(today)\
          .set({ticker: {"win_rate": win_rate, "price": price,
                         "recorded_at": datetime.utcnow()}},
               merge=True)
        return True
    except Exception as e:
        st.sidebar.error(f"히스토리 저장 실패: {e}")
        return False


def load_signal_history(uid: str) -> dict:
    try:
        db = _get_db()
        docs = db.collection("users").document(uid)\
                 .collection("signal_history")\
                 .order_by("__name__", direction=firestore.Query.DESCENDING)\
                 .limit(30).stream()
        history = {}
        for doc in docs:
            history[doc.id] = doc.to_dict()
        return history
    except Exception as e:
        st.sidebar.error(f"히스토리 불러오기 실패: {e}")
        return {}
