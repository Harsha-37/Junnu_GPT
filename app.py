# app.py
import os
import time
from dotenv import load_dotenv
import streamlit as st

# ---------- Page config (must be first st.*)
st.set_page_config(page_title="JunnuGPT", page_icon="💗", layout="wide")

# ---------- Secrets / Env (set this BEFORE importing chat_junnu)
# Cloud: OPENAI_API_KEY must be in Settings → Secrets
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Local dev: also load .env if present (doesn't overwrite what's already set)
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.strip() == "":
    st.error("OPENAI_API_KEY missing. Add it in Settings → Secrets (cloud) or .env (local).")
    st.stop()

# ⬇️ Only now import the module that reads os.getenv at import-time
from chat_junnu import init_messages, chat_once


# ---------- CSS (modern look + pretty input)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial; }
.main .block-container { padding-top: 1.25rem; padding-bottom: 9rem; max-width: 860px; }
/* Hide Streamlit's "Press Enter to submit form" hint */
[data-testid="stForm"] [data-testid="stTextInput"] [aria-live="polite"]{display:none !important;}
/* Fallback for older builds */
[data-testid="stTextInput"] [role="status"]{display:none !important;}


/* Soft bg */
body {
  background:
    radial-gradient(1200px 600px at 10% -10%, #fff6fa 0%, transparent 60%),
    radial-gradient(1200px 600px at 90% -20%, #f4fff9 0%, transparent 60%),
    radial-gradient(900px 500px at -10% 90%, #f7faff 0%, transparent 60%),
    #ffffff;
}

/* Header */
.h-wrap { display:flex; gap:16px; align-items:center; }
.h-icon { font-size:1.8rem; }
.h-title{font-size:2.2rem;font-weight:800;margin:0;letter-spacing:.1px;display:flex;align-items:baseline;gap:10px}
.ver{font-size:.9rem;font-weight:700;color:#b07;opacity:.75}
.h-sub{color:#7b7b7b;margin-top:2px}
.header-accent{height:6px;background:linear-gradient(90deg,#ffdee8,#ffe7f1,#fff0f7,#e8fff3,#def9ec);border-radius:999px;margin:10px 0 18px;}

/* Messages */
.chat { margin-top:.25rem; }
.msg { border-radius:16px; padding:12px 14px; margin:10px 0; line-height:1.6; position:relative; }
.user  { background:#eef2ff; border:1px solid #e3e9ff; box-shadow:0 2px 12px rgba(78,93,180,.06); border-top-left-radius:6px; }
.assistant { background:#eafaf0; border:1px solid #dff4e8; box-shadow:0 2px 12px rgba(48,171,115,.06); border-top-right-radius:6px; }
.role { font-weight:700; opacity:.85; margin-bottom:6px; display:flex; align-items:center; gap:8px; }
.role .avatar { width:28px; height:28px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; }
.avatar-user { background:#dfe6ff; }
.avatar-assistant { background:#d9f6e6; }
.small { font-size:0.86rem; color:#777; margin-top:6px }

/* Sticky composer */
.composer {
  position:fixed; bottom:0; left:0; right:0;
  padding:14px 20px 22px 20px;
  background:linear-gradient(180deg, rgba(255,255,255,0), #ffffff 45%);
  border-top:1px solid #eee;
}
.composer-inner{
  max-width:860px; margin:0 auto;
  display:flex; gap:10px;
  padding:10px; border-radius:18px;
  background:rgba(255,255,255,.85);
  backdrop-filter: blur(10px);
  border:1px solid rgba(230,230,230,.9);
  box-shadow:0 10px 30px rgba(0,0,0,.05);
}

/* Pretty input (ChatGPT style) via wrapper */
.txt-input input{
  height:48px !important;
  border-radius:12px !important;
  border:1px solid #ddd !important;
  padding:0 14px !important;
  background-color:#fff !important;
  color:#333 !important;
  font-size:0.95rem !important;
  box-shadow:inset 0 1px 3px rgba(0,0,0,0.05);
  transition:all .2s ease-in-out;
}
.txt-input input::placeholder{ color:#aaa !important; font-style:italic !important; }
.txt-input input:focus{
  border-color:#ffb6c1 !important;
  box-shadow:0 0 0 3px rgba(255,182,193,0.25) !important;
  outline:none !important;
}

/* Stronger override using Streamlit test-id (works on older versions) */
[data-testid="stTextInput"] input {
  background:#fff !important;
  border:1px solid #ddd !important;
  border-radius:12px !important;
  height:48px !important;
  padding:0 14px !important;
  font-size:0.95rem !important;
  color:#333 !important;
  box-shadow:inset 0 1px 3px rgba(0,0,0,0.05) !important;
}
[data-testid="stTextInput"] input:focus{
  border-color:#ffb6c1 !important;
  box-shadow:0 0 0 3px rgba(255,182,193,0.25) !important;
  outline:none !important;
}
[data-testid="stTextInput"] input::placeholder{
  color:#aaa !important; font-style:italic !important;
}
/* kill red invalid border */
input:invalid { box-shadow:none !important; border-color:#ddd !important; }

/* Send button */
.send-btn button{
  height:48px; border-radius:12px; font-weight:700;
  background:#ffb6c1 !important; border:none !important; color:#fff !important;
  transition:background .2s ease;
}
.send-btn button:hover{ background:#ff9db3 !important; }

/* Scrollbar */
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-thumb{background:#e8e8e8;border-radius:999px}
</style>
""", unsafe_allow_html=True)

# ---------- Header
st.markdown(
    "<div class='h-wrap'><div class='h-icon'>💗</div>"
    "<div><div class='h-title'>JunnuGPT <span class='ver'>v9.1.21</span></div>"
    "<div class='h-sub'>Inside jokes, little teases, open warmth, velvet sarcasm, easy smiles — unsaid care.</div>"
    "</div></div>",
    unsafe_allow_html=True
)
st.markdown("<div class='header-accent'></div>", unsafe_allow_html=True)
# ---------- Seed helper: only 2 demo exchanges
def _seed_two_examples():
    # keep only the system persona from your original init
    base = [m for m in init_messages() if m.get("role") == "system"]

    demo = [
        {"role": "user", "content": "Birthday dare: naku oka secret level hint ivvu. If I find it, I get a virtual hug? 😉"},
        {"role": "assistant", "content": "Deal. Clue: **v9.1.21** — chuddu, adi header daggara unde. 💗"},
        {"role": "user", "content": "Moon check-in: still orbiting around U. Na next year kosam oka blessing cheppu."},
        {"role": "assistant", "content": "May your small braves add up to big magic. Nuvvu light avvali—tapakunda! ✨"},
    ]
    return base + demo

# ---------- Session
if "messages" not in st.session_state:
    st.session_state.messages = _seed_two_examples()


if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False
if "last_latency_ms" not in st.session_state:
    st.session_state.last_latency_ms = None


# ---------- Render messages
st.markdown("<div class='chat'>", unsafe_allow_html=True)
for msg in st.session_state.messages:
    role = msg.get("role")
    if role == "system":
        continue
    if role == "user":
        st.markdown(
            f"<div class='msg user'>"
            f"<div class='role'><span class='avatar avatar-user'>🧍‍♂️</span>You</div>"
            f"{msg['content']}</div>",
            unsafe_allow_html=True
        )
    elif role == "assistant":
        st.markdown(
            f"<div class='msg assistant'>"
            f"<div class='role'><span class='avatar avatar-assistant'>💖</span>Junnu</div>"
            f"{msg['content']}</div>",
            unsafe_allow_html=True
        )
st.markdown("</div>", unsafe_allow_html=True)

# Typing / latency
if st.session_state.is_thinking:
    st.markdown("<div class='small'>Junnu is typing…</div>", unsafe_allow_html=True)
elif st.session_state.last_latency_ms is not None:
    st.markdown(f"<div class='small'>Last reply: {st.session_state.last_latency_ms:.0f} ms</div>", unsafe_allow_html=True)

# ---------- Composer (Enter-to-send + Send button)
st.markdown("<div class='composer'><div class='composer-inner'>", unsafe_allow_html=True)
with st.form("composer_form", clear_on_submit=True):
    c1, c2 = st.columns([7, 1.2])
    with c1:
        st.markdown("<div class='txt-input'>", unsafe_allow_html=True)
        st.text_input("", key="composer_input", placeholder="Message Junnu…")  # Enter submits
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='send-btn'>", unsafe_allow_html=True)
        sent = st.form_submit_button("➤ Send")   # keep simple for older Streamlit
        st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)

# ---------- Submit handler
if sent:
    user_text = st.session_state.get("composer_input", "").strip()
    if user_text:
        st.session_state.is_thinking = True
        t0 = time.time()
        with st.spinner(""):
            try:
                reply, st.session_state.messages = chat_once(
                    st.session_state.messages,
                    user_text,
                    model="gpt-4o"
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
            finally:
                st.session_state.is_thinking = False
                st.session_state.last_latency_ms = (time.time() - t0) * 1000.0
        st.rerun()

# ---------- Sidebar
with st.sidebar:
    st.markdown("### Controls")
    if st.button("🔁 Reset chat"):
       st.session_state.messages = _seed_two_examples()
       st.session_state.last_latency_ms = None
       st.rerun()

    st.caption("Press **Enter** to send · or click **➤ Send** on the right.\nSoft palette + tiny acrostics keep the vibe personal.")






