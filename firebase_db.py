# firebase_db.py — Firestore 저장/불러오기

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import base64
import json


# ── Firebase 초기화 (한 번만) ─────────────────────────────────────────────────
def _init_firebase():
    if firebase_admin._apps:
        return True
    try:
        b64 = st.secrets["firebase"]["json_base64"]
        key_dict = json.loads(base64.b64decode(b64).decode("utf-8"))
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
        return True
    except KeyError:
        return False
    except Exception:
        return False


def get_db():
    if not _init_firebase():
        return None
    try:
        return firestore.client()
    except Exception:
        return None


# ── 포트폴리오 저장 ───────────────────────────────────────────────────────────
def save_portfolio(uid: str, portfolio: list) -> bool:
    db = get_db()
    if db is None:
        return False
    try:
        db.collection("users").document(uid).set(
            {"portfolio": portfolio, "updated_at": datetime.utcnow()},
            merge=True
        )
        return True
    except Exception as e:
        st.error(f"포트폴리오 저장 실패: {e}")
        return False


# ── 포트폴리오 불러오기 ───────────────────────────────────────────────────────
def load_portfolio(uid: str) -> list:
    db = get_db()
    if db is None:
        return []
    try:
        doc = db.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict().get("portfolio", [])
        return []
    except Exception as e:
        st.error(f"포트폴리오 불러오기 실패: {e}")
        return []


# ── 신호 히스토리 저장 ────────────────────────────────────────────────────────
def save_signal_history(uid: str, ticker: str, win_rate: float, price: float):
    db = get_db()
    if db is None:
        return False
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        db.collection("users").document(uid)\
          .collection("signal_history").document(today)\
          .set({ticker: {"win_rate": win_rate, "price": price,
                         "recorded_at": datetime.utcnow()}},
               merge=True)
        return True
    except Exception as e:
        st.error(f"신호 히스토리 저장 실패: {e}")
        return False


# ── 신호 히스토리 불러오기 (최근 30일) ───────────────────────────────────────
def load_signal_history(uid: str) -> dict:
    db = get_db()
    if db is None:
        return {}
    try:
        docs = db.collection("users").document(uid)\
                 .collection("signal_history")\
                 .order_by("__name__", direction=firestore.Query.DESCENDING)\
                 .limit(30).stream()
        history = {}
        for doc in docs:
            history[doc.id] = doc.to_dict()
        return history
    except Exception as e:
        st.error(f"히스토리 불러오기 실패: {e}")
        return {}
