import streamlit as st
from st_keyup import st_keyup
import time

# --- CONFIG ---
st.set_page_config(
    page_title="Social Inbox Triage",
    page_icon="📥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@300;400;600;700&display=swap');

    :root {
        --text-primary: #f7f9f9;
        --text-secondary: #8b98a5;
        --bg-main: #15202b;
        --bg-card: #1e2732;
        --accent: #1d9bf0;
        --success: #00ba7c;
        --warning: #ffad1f;
        --danger: #f4212e;
        --border: #38444d;
        --payload-bg: #f8f9fa;
        --payload-text: #1a1a1a;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-main);
        color: var(--text-primary);
    }

    h1, h2, h3, .outfit-font { font-family: 'Outfit', sans-serif; }

    /* Custom Header */
    .candidate-header { border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
    .candidate-name { font-size: 24px; font-weight: 700; color: var(--text-primary); }
    .candidate-title { font-size: 14px; color: var(--accent); font-weight: 500; margin-bottom: 8px; }
    .contact-links { font-size: 12px; color: var(--text-secondary); display: flex; gap: 8px; flex-wrap: wrap; }
    .contact-links a { color: var(--text-secondary); text-decoration: none; }
    .app-description { font-size: 14px; color: var(--text-secondary); margin-top: 12px; line-height: 1.4; }

    /* Message Card styling (Read-Only) */
    .tweet-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .tweet-header { display: flex; align-items: center; margin-bottom: 8px; }
    .avatar { width: 36px; height: 36px; border-radius: 50%; background: #38444d; display: flex; align-items: center; justify-content: center; font-size: 16px; margin-right: 10px; }
    .tweet-content { font-size: 15px; line-height: 1.4; color: var(--text-primary); white-space: pre-wrap; word-wrap: break-word; }

    /* Instruction */
    .instruction-line { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 4px; }

    /* Triage Section */
    .triage-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 16px; }
    .badge-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 8px; text-align: center; }
    .badge-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 2px; }
    .badge-value { font-weight: 700; font-size: 13px; }

    /* Status Colors */
    .val-critical, .val-high { color: var(--danger); }
    .val-medium { color: var(--warning); }
    .val-low, .val-positive { color: var(--success); }
    .val-bug { color: #7856ff; }

    /* Reasoning/Response */
    .result-card { background: linear-gradient(145deg, #1e2732, #253341); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 20px; }
    .label-accent { color: var(--accent); font-weight: 700; font-size: 11px; text-transform: uppercase; margin-bottom: 4px; }
    .reasoning-text { font-size: 13px; font-style: italic; color: var(--text-secondary); margin-bottom: 12px; border-left: 2px solid var(--border); padding-left: 10px; }

    /* Tone Check */
    .section-title { font-size: 14px; font-weight: 700; text-transform: uppercase; margin-top: 24px; border-bottom: 1px solid var(--border); padding-bottom: 4px; margin-bottom: 12px; }
    .risk-tag { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }

    /* Escalation UI Fix */
    .escalation-container { background: rgba(244, 33, 46, 0.05); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-top: 20px; }
    .escalation-container.active { border-color: var(--danger); }

    .slack-payload {
        background: var(--payload-bg);
        color: var(--payload-text);
        border: 1px solid #ced4da;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        line-height: 1.5;
        margin-top: 12px;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
    }
    .payload-title { font-weight: 700; font-size: 11px; color: #6c757d; text-transform: uppercase; margin-bottom: 8px; border-bottom: 1px solid #dee2e6; padding-bottom: 4px; }
    .payload-grid { display: grid; grid-template-columns: 80px 1fr; gap: 4px; margin-bottom: 12px; }
    .payload-label { font-weight: 600; color: #495057; }

    /* Hide Streamlit components */
    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; display: none; }
    .stTextInput input, .stTextArea textarea { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
class SupportIntelligence:
    @staticmethod
    def analyze(text):
        text_l = text.lower()
        intent, sentiment, urgency, risk, channel, next_step, signal = "Question", "Neutral", "Low", "Low", "Public", "Reply Publicly", "UX confusion"
        reasoning = "Standard inquiry detected."
        suggested = "Hi! Thanks for reaching out. How can I help you with this?"
        
        # High-Risk Triggers (Critical)
        if any(w in text_l for w in ["fuck", "shit", "damn", "wtf", "pissed"]):
            sentiment, risk, urgency = "Negative", "High", "High"
            next_step = "Move to DM"
        
        if any(w in text_l for w in ["sue", "lawyer", "legal", "court", "suing"]):
            risk, urgency, next_step = "High", "High", "Escalate"
            reasoning = "Legal threat detected. Critical risk handling protocol engaged."
        
        # Intent & Logic
        if any(w in text_l for w in ["charge", "billing", "money", "overbilled", "paid"]):
            intent, signal = "Billing", "Billing issue"
            urgency = "High" if urgency == "High" else "Medium"
            channel = "Private (DM)"
            if "fuck" in text_l or "suing" in text_l: next_step = "Escalate"
            else: next_step = "Move to DM"
            
        elif any(w in text_l for w in ["bug", "fail", "error", "broken", "fix"]):
            intent, signal, next_step = "Bug", "Bug report", "Escalate Internally"
            urgency = "Medium"
            
        # Sentiment Polish
        if any(w in text_l for w in ["lol", "thanks", "love", "great"]):
            sentiment = "Positive"

        # Specialized Responses
        if "bit" in text_l: # billing/legal/anger mix
            if "suing" in text_l or "fuck" in text_l:
                reasoning = "Combined legal/billing threat in public message. Immediate escalation required to protect brand voice."
                suggested = "I’m sorry you’re running into this frustration. I've escalated your billing concern to our senior team to resolve this immediately."
        
        elif "dark mode" in text_l:
            reasoning = "Feature request detected. Low urgency, positive engagement opportunity."
            suggested = "We hear you! Dark mode is on the roadmap for 2026. Stay tuned!"

        # Escalation Logic
        esc_required = (risk == "High" or next_step == "Escalate")
        esc_target = "Exec (Slack)" if ("sue" in text_l or "legal" in text_l or "fuck" in text_l) else "Engineering (Linear)"
        
        return {
            "intent": intent, "sentiment": sentiment, "urgency": urgency, "risk": risk, 
            "channel": channel, "next_step": next_step, "reasoning": reasoning, 
            "suggested": suggested, "signal": signal, "esc_required": esc_required, "esc_target": esc_target
        }

class ToneAI:
    @staticmethod
    def analyze(text):
        text_l = text.lower()
        risk, issues, improved = "Low", ["No major issues"], text
        if any(w in text_l for w in ["fault", "wrong", "read the docs"]):
            risk, issues = "High", ["Blames user", "Defensive tone"]
            improved = "I’m sorry you’re running into this. Let’s look at the settings together."
        elif any(w in text_l for w in ["already told"]):
            risk, issues = "High", ["Condescending"]
            improved = "Apologies if earlier info was unclear! Here’s the latest status."
        return {"risk": risk, "issues": issues, "improved": improved}

# --- APP UI ---

# Header
st.markdown(f"""
<div class="candidate-header">
    <div class="candidate-name">Sefket Nouri</div>
    <div class="candidate-title">Social Media Support Specialist candidate</div>
    <div class="contact-links">me@sefketnouri.com • LinkedIn • Portfolio</div>
</div>
""", unsafe_allow_html=True)

# 1. FIX: ONE INPUT FIELD
st.markdown('<div class="instruction-line">Paste a messy tweet, DM, or comment — triaged instantly.</div>', unsafe_allow_html=True)
message = st_keyup("Incoming message", value="fuck, Replit overbilled me - I'M SUING YOU ALL", key="main_input", label_visibility="collapsed")

# 2. FIX: READ-ONLY MESSAGE PREVIEW (TWEET CARD)
st.markdown(f"""
<div class="tweet-card">
    <div class="tweet-header">
        <div class="avatar">👤</div>
        <div>
            <div class="user-name">Unknown User</div>
            <div class="user-handle">@customer</div>
        </div>
    </div>
    <div class="tweet-content">{message if message else "Waiting for message..."}</div>
</div>
""", unsafe_allow_html=True)

# 3. FIX: TRIAGE LOGIC
analysis = SupportIntelligence.analyze(message)

# Triage Grid
st.markdown(f"""
<div class="triage-grid">
    <div class="badge-card"><div class="badge-label">Intent</div><div class="badge-value val-{analysis['intent'].lower()}">{analysis['intent']}</div></div>
    <div class="badge-card"><div class="badge-label">Sentiment</div><div class="badge-value val-{analysis['sentiment'].lower()}">{analysis['sentiment']}</div></div>
    <div class="badge-card"><div class="badge-label">Urgency</div><div class="badge-value val-{analysis['urgency'].lower()}">{analysis['urgency']}</div></div>
    <div class="badge-card"><div class="badge-label">Risk Level</div><div class="badge-value val-{analysis['risk'].lower()}">{analysis['risk']}</div></div>
    <div class="badge-card"><div class="badge-label">Channel</div><div class="badge-value">{analysis['channel']}</div></div>
    <div class="badge-card"><div class="badge-label">Next Step</div><div class="badge-value">{analysis['next_step']}</div></div>
</div>
""", unsafe_allow_html=True)

# Reasoning Section
st.markdown(f"""
<div class="result-card">
    <div class="label-accent">AI Reasoning</div>
    <div class="reasoning-text">"{analysis['reasoning']}"</div>
    <div class="label-accent">Suggested Response</div>
    <div style="font-size: 14px; color: var(--text-primary);">{analysis['suggested']}</div>
</div>
""", unsafe_allow_html=True)

# 7. Tone check Section
st.markdown('<div class="section-title">Tone check</div>', unsafe_allow_html=True)
if 'last_sug' not in st.session_state: st.session_state.last_sug = analysis['suggested']
if st.session_state.last_sug != analysis['suggested']:
    st.session_state.last_sug = analysis['suggested']
    st.session_state.tk = f"tk_{time.time()}"
if 'tk' not in st.session_state: st.session_state.tk = "tk_init"

draft = st_keyup("Edit reply", value=analysis['suggested'], key=st.session_state.tk, label_visibility="collapsed")
tone = ToneAI.analyze(draft)
t_risk_class = f"risk-{tone['risk'].lower()}"
st.markdown(f'<div class="risk-tag {t_risk_class}">{tone["risk"]} Tone Risk</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1,1])
with col1:
    for issue in tone['issues']: st.markdown(f'<div class="issue-item">{issue}</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="improved-box"><div style="font-size: 10px; font-weight:700; color:var(--success);">IMPROVED VERSION</div><div style="font-size: 12px;">"{tone["improved"]}"</div></div>', unsafe_allow_html=True)

# 4 & 5. FIX: ESCALATION UI & BEHAVIOR
if analysis['esc_required']:
    st.markdown('<div class="section-title">Escalation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="escalation-container active">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div><div class="badge-label">Status</div><div class="badge-value" style="color:var(--danger)">Required</div></div>
            <div><div class="badge-label">Target</div><div class="badge-value">{analysis['esc_target']}</div></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"Escalate to {analysis['esc_target'].split(' (')[0]} Slack"):
        st.session_state.esc_done = True
        st.session_state.esc_m = message

    if st.session_state.get('esc_done') and st.session_state.get('esc_m') == message:
        ch = "#exec-escalations" if "Exec" in analysis['esc_target'] else "#linear-bugs"
        st.success(f"Escalated to {ch}")
        # 4 & 6. FIX: CLEAN PAYLOAD WITH CONTRAST
        st.markdown(f"""
        <div class="slack-payload">
            <div class="payload-title">Slack Payload: {ch}</div>
            <div class="payload-grid">
                <div class="payload-label">Channel:</div><div>{ch}</div>
                <div class="payload-label">Priority:</div><div style="color: #dc3545; font-weight: 700;">Urgent</div>
                <div class="payload-label">Reason:</div><div>{analysis['reasoning']}</div>
            </div>
            <div class="payload-label" style="margin-bottom:4px;">Summary:</div>
            <div style="background: #fff; border: 1px solid #dee2e6; padding: 10px; border-radius: 6px; font-size: 13px;">
                User is threatening legal action over a billing complaint in a public message. High risk.
            </div>
            <div class="payload-label" style="margin-top:12px; margin-bottom:4px;">Original message:</div>
            <div style="font-style: italic; color: #6c757d; border-left: 2px solid #dee2e6; padding-left: 10px;">"{message}"</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><center style='color: var(--text-secondary); font-size: 11px;'>Sefket Nouri • Demo Refactoring • Reactive Mode Active</center>", unsafe_allow_html=True)
