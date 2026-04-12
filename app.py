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
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--bg-main);
        color: var(--text-primary);
    }

    h1, h2, h3, .outfit-font { font-family: 'Outfit', sans-serif; }

    /* Custom Header */
    .candidate-header {
        border-bottom: 1px solid var(--border);
        padding-bottom: 24px;
        margin-bottom: 32px;
    }
    .candidate-name { font-size: 28px; font-weight: 700; margin-bottom: 4px; color: var(--text-primary); }
    .candidate-title { font-size: 16px; color: var(--accent); font-weight: 500; margin-bottom: 16px; }
    .contact-links { font-size: 14px; color: var(--text-secondary); display: flex; gap: 12px; flex-wrap: wrap; }
    .contact-links a { color: var(--text-secondary); text-decoration: none; border-bottom: 1px solid transparent; }
    .contact-links a:hover { color: var(--accent); border-bottom: 1px solid var(--accent); }

    .app-description { font-size: 15px; line-height: 1.6; color: var(--text-secondary); margin-top: 20px; }
    .workflow-nav { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-top: 12px; letter-spacing: 0.5px; }

    /* Message Card styling */
    .message-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    .avatar { width: 44px; height: 44px; border-radius: 50%; background: #38444d; display: flex; align-items: center; justify-content: center; font-size: 18px; margin-right: 12px; }
    .user-name { font-weight: 700; font-size: 15px; }
    .user-handle { color: var(--text-secondary); font-size: 13px; }

    /* Instruction */
    .instruction-line { font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 8px; }

    /* Triage Section */
    .triage-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 16px; }
    .badge-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 10px; text-align: center; }
    .badge-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 2px; }
    .badge-value { font-weight: 700; font-size: 14px; }

    /* Status Colors */
    .val-critical, .val-high { color: var(--danger); }
    .val-medium { color: var(--warning); }
    .val-low, .val-positive, .val-billing { color: var(--success); }
    .val-bug { color: #7856ff; }

    /* Featured Response */
    .response-card {
        background: linear-gradient(145deg, #1e2732, #253341);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 16px;
        margin-top: 12px;
    }
    .response-label { color: var(--accent); font-weight: 700; font-size: 11px; margin-bottom: 4px; text-transform: uppercase; }
    .reasoning { font-size: 13px; font-style: italic; color: var(--text-secondary); margin-bottom: 12px; border-left: 2px solid var(--border); padding-left: 10px; }

    /* Section Headers */
    .section-header { font-size: 14px; font-weight: 700; color: var(--text-primary); margin: 24px 0 12px 0; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--border); padding-bottom: 4px; }

    /* Tone Check */
    .risk-ribbon { font-size: 10px; text-transform: uppercase; font-weight: 700; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }
    .risk-high { background: rgba(244, 33, 46, 0.2); color: var(--danger); }
    .risk-medium { background: rgba(255, 173, 31, 0.2); color: var(--warning); }
    .risk-low { background: rgba(0, 186, 124, 0.2); color: var(--success); }
    .issue-item { font-size: 12px; color: var(--text-secondary); margin: 2px 0; }
    .issue-item::before { content: "• "; color: var(--warning); }
    .improved-box { background: rgba(0, 186, 124, 0.05); border: 1px dashed var(--success); border-radius: 8px; padding: 10px; margin-top: 8px; }

    /* Escalation Box */
    .escalation-box { background: rgba(244, 33, 46, 0.05); border: 1px solid rgba(244, 33, 46, 0.2); border-radius: 12px; padding: 16px; margin-top: 12px; }
    .escalation-active { border-color: var(--danger); background: rgba(244, 33, 46, 0.1); }

    /* Escalation Payload */
    .payload-card { background: #000; border-radius: 8px; padding: 12px; font-family: 'Courier New', monospace; font-size: 12px; color: #00ff00; margin-top: 12px; }

    /* Override Streamlit elements */
    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; display: none; }
    .stTextInput input, .stTextArea textarea { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
class TriageAI:
    @staticmethod
    def analyze(text):
        text_l = text.lower()
        intent, sentiment, urgency, risk, channel, next_step, signal = "Question", "Neutral", "Low", "Low", "Public", "Reply Publicly", "UX confusion"
        reasoning = "Standard inquiry detected."
        suggested = "Hi! Thanks for reaching out. How can I help you with this?"
        pattern = "No clear pattern"

        # Pattern Detection
        if any(w in text_l for w in ["charge", "billing", "paid", "money"]): 
            pattern = "Recurring billing confusion"
        if any(w in text_l for w in ["deploy", "fail", "broken", "disappeared"]): 
            pattern = "Multiple deploy failures reported"

        # 1. Intent & Internal Signal
        if any(w in text_l for w in ["bug", "fail", "error", "broken", "fix"]): 
            intent, signal, next_step = "Bug", "Bug report", "Escalate Internally"
        elif any(w in text_l for w in ["charge", "billing", "money", "paid", "refund"]): 
            intent, signal, channel, next_step = "Billing", "Billing issue", "Private (DM)", "Move to DM"
        elif any(w in text_l for w in ["feature", "request", "add", "can you"]): 
            intent, signal = "Feature", "Feature request"
        elif len(text.strip()) < 10:
            signal = "Noise"

        # 2. Sentiment, Urgency, Risk
        if any(w in text_l for w in ["charged twice", "wtf", "now", "fix this", "??", "!!"]): 
            sentiment, urgency, risk = "Negative", "High", "High"
        elif any(w in text_l for w in ["lol", "thanks", "wow", "love"]): 
            sentiment = "Positive"

        # Specific Reasoning/Responses
        if intent == "Billing" and sentiment == "Negative":
            reasoning = "Detected duplicate charge complaint. Sensitive data requires private channel move."
            suggested = "I'm so sorry about the double charge! That sounds frustrating. Can you send us a DM with your email so I can fix this right away?"
        elif intent == "Bug" and urgency == "High":
            reasoning = "Critical functional failure reported. Immediate internal escalation recommended."
            suggested = "I'm really sorry to hear your projects disappeared—that shouldn't happen. DM us your account details and I’ll get our senior engineers on this now."
        elif "dark mode" in text_l:
            reasoning = "Product feedback regarding feature parity. Low urgency, high engagement opportunity."
            suggested = "I hear you! Dark mode is a top request. I'll make sure the product team knows it's still missing in 2026. Stay tuned! 🌑"
        elif "fail lol" in text_l:
            reasoning = "Snarky feedback reporting UX failure. Medium risk due to public visibility."
            suggested = "Ouch, definitely not the experience we want for you. Which deploy failed? I'd love to dig into this for you."

        # Escalation Logic
        esc_required = False
        esc_target = "Support (Zendesk)"
        if any(w in text_l for w in ["lawyer", "sue", "legal", "court"]):
            esc_required, esc_target = True, "Exec (Slack)"
        elif risk == "High":
            esc_required = True
            esc_target = "Engineering (Linear)" if intent == "Bug" else "Support (Zendesk)"
        
        return {
            "intent": intent, "sentiment": sentiment, "urgency": urgency, "risk": risk, 
            "channel": channel, "next_step": next_step, "reasoning": reasoning, 
            "suggested": suggested, "signal": signal, "pattern": pattern,
            "esc_required": esc_required, "esc_target": esc_target
        }

class ToneAI:
    @staticmethod
    def analyze(text):
        text_l = text.lower()
        risk, issues, improved = "Low", ["No major issues"], text
        if any(w in text_l for w in ["fault", "wrong", "you must", "read the docs"]):
            risk, issues = "High", ["Blames user", "Defensive tone"]
            improved = "I’m sorry you’re running into this. Let’s double-check the settings together."
        elif any(w in text_l for w in ["already told", "told you", "we said"]):
            risk, issues = "High", ["Defensive", "Condescending"]
            improved = "I apologize for any confusion! Let me try to clarify that status for you."
        elif any(w in text_l for w in ["idk", "don't know", "working on our end"]):
            risk, issues = "Medium", ["Dismissive", "Short tone"]
            improved = "It looks like our systems are green, but I want to make sure your case is solved."
        return {"risk": risk, "issues": issues, "improved": improved}

# --- APP UI ---

# 1. Candidate Header
st.markdown(f"""
<div class="candidate-header">
    <div class="candidate-name">Sefket Nouri</div>
    <div class="candidate-title">Replit Social Media Support Specialist candidate</div>
    <div class="contact-links">
        <a href="mailto:me@sefketnouri.com">Email</a> · 
        <a href="https://www.linkedin.com/in/sefketnouri/" target="_blank">LinkedIn</a> · 
        <a href="https://sefket24-social-inbox-triage.streamlit.app/">App</a> · 
        <a href="https://replit.com/@sefketnouri" target="_blank">Replit</a>
    </div>
    <div class="app-description">
        Social support is noisy. I built small tools to turn that into clear decisions across deployment, billing, and inbound triage.
    </div>
    <div class="workflow-nav">
        Workflow: Deployment Debugger → Support Gatekeeper → <span style="color:var(--accent); border-bottom: 2px solid var(--accent);">Social Inbox Triage</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Instruction & Message Card
st.markdown('<div class="instruction-line">“Paste a messy tweet, DM, or comment — see how it gets triaged instantly.”</div>', unsafe_allow_html=True)
st.markdown('<div class="message-card">', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 10])
with col_a: st.markdown('<div class="avatar">👤</div>', unsafe_allow_html=True)
with col_b: st.markdown('<div class="user-name">Unknown User</div><div class="user-handle">@customer</div>', unsafe_allow_html=True)
message = st_keyup("Input", value="your app just charged me twice?? what is this", key="msg_input", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# --- Analysis & Core Output ---
analysis = TriageAI.analyze(message)

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

# Reasoning & suggested response
st.markdown(f"""
<div class="response-card">
    <div class="response-label">AI REASONING</div>
    <div class="reasoning">"{analysis['reasoning']}"</div>
    <div class="response-label">SUGGESTED RESPONSE</div>
    <div style="font-size: 15px; color: #f7f9f9;">{analysis['suggested']}</div>
</div>
""", unsafe_allow_html=True)

# 7. Tone Check
st.markdown('<div class="section-header">Tone check</div>', unsafe_allow_html=True)

# Dynamic reset logic for Tone Check
if 'last_sug' not in st.session_state: st.session_state.last_sug = analysis['suggested']
if st.session_state.last_sug != analysis['suggested']:
    st.session_state.last_sug = analysis['suggested']
    st.session_state.tone_key = f"tone_{time.time()}"
if 'tone_key' not in st.session_state: st.session_state.tone_key = "tone_init"

draft = st_keyup("Edit draft", value=analysis['suggested'], key=st.session_state.tone_key, label_visibility="collapsed")
tone = ToneAI.analyze(draft)

# Tone Output
risk_c = f"risk-{tone['risk'].lower()}"
st.markdown(f'<div class="risk-ribbon {risk_c}">{tone["risk"]} Risk</div>', unsafe_allow_html=True)
c1, c2 = st.columns([1, 1])
with c1:
    for issue in tone['issues']: st.markdown(f'<div class="issue-item">{issue}</div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="improved-box"><div style="font-size: 11px; font-weight:700; color:var(--success);">IMPROVED</div><div style="font-size: 13px;">"{tone["improved"]}"</div></div>', unsafe_allow_html=True)

# 6. Internal Signal & 8. Pattern Detected
st.markdown('<div class="section-header">Internal signal</div>', unsafe_allow_html=True)
col_sig_a, col_sig_b = st.columns([1, 1])
with col_sig_a:
    st.markdown(f'<div class="badge-card" style="text-align:left;"><div class="badge-label">Classification</div><div class="badge-value">{analysis["signal"]}</div></div>', unsafe_allow_html=True)
with col_sig_b:
    st.markdown(f'<div style="margin-top:4px;"><span style="color:var(--text-secondary); font-size:12px; font-weight:700; text-transform:uppercase;">Pattern detected:</span><br><span style="font-size:14px; font-weight:600;">{analysis["pattern"]}</span></div>', unsafe_allow_html=True)

# 5. Escalation Workflow
st.markdown('<div class="section-header">Escalation</div>', unsafe_allow_html=True)
status_str = "Required" if analysis['esc_required'] else "Not required"
esc_class = "escalation-active" if analysis['esc_required'] else ""

st.markdown(f"""
<div class="escalation-box {esc_class}">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div class="badge-label">Status</div>
            <div class="badge-value" style="color: {'var(--danger)' if analysis['esc_required'] else 'var(--text-secondary)'}">{status_str}</div>
        </div>
        <div>
            <div class="badge-label">Target</div>
            <div class="badge-value">{analysis['esc_target']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if analysis['esc_required']:
    btn_label = f"Escalate to {'Exec Slack' if 'Exec' in analysis['esc_target'] else analysis['esc_target'].split('(')[1].split(')')[0]}"
    if st.button(btn_label):
        st.session_state.escalated = True
        st.session_state.esc_msg = message
    
    if st.session_state.get('escalated'):
        channel = "#exec-escalations" if "Exec" in analysis['esc_target'] else ("#linear-bugs" if "Engineering" in analysis['esc_target'] else "#support-tickets")
        st.success(f"Escalated to {channel}")
        st.markdown(f"""
        <div class="payload-card">
            [INTERNAL PAYLOAD]<br>
            Channel: {channel}<br>
            Priority: {'Urgent' if 'Exec' in analysis['esc_target'] else 'High'}<br>
            Reason: {analysis['reasoning']}<br><br>
            Summary: {analysis['intent']} detected with {analysis['sentiment']} sentiment. Immediate action: {analysis['next_step']}.<br><br>
            Original Message: "{message}"
        </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><center style='color: var(--text-secondary); font-size: 11px;'>Sefket Nouri • Social Support Demo v3.0 • Reactive Mode Active</center>", unsafe_allow_html=True)
