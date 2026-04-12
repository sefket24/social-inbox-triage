import streamlit as st
from st_keyup import st_keyup
import time
import re

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
    .candidate-name { font-size: 22px; font-weight: 700; color: var(--text-primary); }
    .candidate-title { font-size: 13px; color: var(--accent); font-weight: 500; margin-bottom: 4px; }
    .contact-links { font-size: 11px; color: #ffffff; display: flex; gap: 12px; margin-top: 4px; }
    .contact-links a { 
        color: #ffffff; 
        text-decoration: none; 
        border-bottom: 1px solid rgba(255,255,255,0.3); 
        padding-bottom: 1px;
        transition: all 0.2s ease;
    }
    .contact-links a:hover { 
        color: var(--accent); 
        border-bottom-color: var(--accent);
        opacity: 0.9;
    }

    /* Message Card styling */
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
    .tweet-content { font-size: 15px; line-height: 1.4; color: var(--text-primary); }

    /* Triage Section */
    .triage-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 20px; }
    .badge-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 8px; text-align: center; height: 100%; }
    .badge-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 2px; }
    .badge-value { font-weight: 700; font-size: 13px; }

    /* Status Colors */
    .val-critical, .val-high { color: var(--danger); }
    .val-medium { color: var(--warning); }
    .val-low, .val-positive { color: var(--success); }
    .val-mixed { color: var(--warning); }
    .val-negative { color: var(--danger); }

    /* Reasoning/Response */
    .result-card { background: linear-gradient(145deg, #1e2732, #253341); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 24px; }
    .label-accent { color: var(--accent); font-weight: 700; font-size: 11px; text-transform: uppercase; margin-bottom: 4px; }
    .reasoning-text { font-size: 13px; font-style: italic; color: var(--text-secondary); border-left: 2px solid var(--border); padding-left: 10px; margin-bottom: 12px; }

    /* Escalation Section */
    .section-title { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--text-primary); margin-bottom: 12px; border-bottom: 1px solid var(--border); padding-bottom: 4px; }
    .escalation-box { background: rgba(244, 33, 46, 0.05); border: 1px solid var(--border); border-radius: 12px; padding: 16px; margin-bottom: 16px; }
    .escalation-box.active { border-color: var(--danger); background: rgba(244, 33, 46, 0.1); }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: var(--accent) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    /* Payload */
    .slack-payload { background: var(--payload-bg); color: var(--payload-text); border: 1px solid #ced4da; border-radius: 10px; padding: 16px; font-size: 12px; margin-top: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .payload-title { font-weight: 800; text-transform: uppercase; font-size: 10px; color: #6c757d; border-bottom: 1px solid #dee2e6; margin-bottom: 10px; padding-bottom: 4px; }
    .payload-row { display: grid; grid-template-columns: 80px 1fr; gap: 4px; margin-bottom: 4px; }
    .payload-label { font-weight: 700; color: #495057; }

    /* Hide Streamlit components */
    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; display: none; }
    .stTextInput input { background-color: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
class PriorityTriage:
    @staticmethod
    def analyze(text):
        text_l = text.lower()
        
        # 1. Feature Extraction
        is_legal = any(w in text_l for w in ["lawyer", "sue", "legal", "attorney", "suing", "court"])
        is_enterprise = any(w in text_l for w in ["enterprise", "business", "client", "customer account"])
        is_account = any(w in text_l for w in ["locked out", "can't log in", "account access"])
        has_profanity = any(w in text_l for w in ["fuck", "shit", "damn", "wtf"])
        
        is_outage = any(w in text_l for w in ["site is down", "website is down", "app is down", "service is down", "not loading"])
        is_financial = any(w in text_l for w in ["losing money", "costing me money", "revenue", "customers affected", "business impact"])
        
        # Urgency Detection
        urgency_score = 0
        urgency_phrases = ["urgent", "asap", "right now", "tight deadline", "need help", "fast", "!!"]
        for p in urgency_phrases:
            if p in text_l: urgency_score += 1
        
        caps_count = len(re.findall(r'\b[A-Z]{3,}\b', text))
        if caps_count >= 2: urgency_score += 1
        
        # --- RULE STACKING ---
        sentiment, urgency, risk, intent, channel = "Neutral", "Low", "Low", "Question", "Public"
        next_step, target, flow = "Reply Publicly", "Support (Zendesk)", "Support Ownership"
        
        # Intent
        if is_business := is_enterprise: intent = "Enterprise"
        elif is_outage: intent = "Outage"
        elif any(w in text_l for w in ["bug", "fail", "broken", "deploy"]): intent = "Bug"
        elif any(w in text_l for w in ["billing", "overbilled", "charge", "refund"]): intent = "Billing"
        elif is_account: intent = "Account Access"

        # Sentiment
        if has_profanity or any(w in text_l for w in ["not working", "locked out", "broken"]) or is_outage or is_financial:
            sentiment = "Negative"

        # Urgency & Risk
        if urgency_score >= 1 or is_account: urgency = "Medium"
        if urgency_score >= 2 or is_enterprise or is_outage: urgency = "High"
        if has_profanity or is_financial or is_legal or is_enterprise: risk = "High"
        elif is_outage: risk = "Medium"

        # ESCALATION FLOW (Two-Stage Model)
        esc_required = (risk == "High" or urgency == "High")
        
        # Default Flow: Support (Zendesk) -> Engineering (Linear)
        flow = "Support (Zendesk) → Engineering (Linear)"
        target = "Support (Zendesk)"
        
        if is_legal:
            target, next_step, flow = "Exec (Slack)", "Escalate Immediately", "Direct to Exec"
        elif is_outage and is_financial:
            target, next_step = "Engineering (Linear)", "Escalate + Respond (Urgent)"
            flow = "Fast-Track Support → Engineering"
        elif is_outage:
            target, next_step = "Support (Zendesk)", "Reply immediately (Offer DM) + escalate via Support"
        elif is_account:
            target, next_step = "Support (Zendesk)", "Reply Publicly (Offer DM)"
            flow = "Internal Verification Flow"

        # Final Validation Confidence
        is_high_confidence_bug = (is_outage and is_financial) or (intent == "Bug" and urgency == "High")

        # Specialized Reasoning
        reasoning = "Initial support ownership active. Validating issue before technical escalation."
        if is_legal: reasoning = "Legal risk detected. Bypassing validation; direct escalation to leadership."
        elif is_outage and is_financial: reasoning = "Major financial impact confirmed. Fast-tracking to Engineering for immediate resolution."
        elif is_outage: reasoning = "Potential outage reported. Support validating reproducibility before engineering handoff."
        elif is_account: reasoning = "Sensitive account access issue. Gathering details via DM first."

        suggested = "Hi! I'm sorry to hear that. Can you send us a DM with your email so we can verify the details and help right away?"
        if is_legal: suggested = "I hear your concern. I've escalated this specifically to our senior leadership team to address this with you."

        return {
            "intent": intent, "sentiment": sentiment, "urgency": urgency, "risk": risk,
            "next_step": next_step, "channel": channel, "target": target, "flow": flow,
            "reasoning": reasoning, "suggested": suggested, 
            "is_high_confidence_bug": is_high_confidence_bug, "is_legal": is_legal
        }

# --- APP UI ---
st.title("📥 Social Inbox Triage")
st.caption("Decision Support Engine • Two-Stage Escalation Active")

# Header
st.markdown(f"""
<div class="candidate-header">
    <div class="candidate-name">Sefket Nouri</div>
    <div class="candidate-title"><a href="https://replit.com/" target="_blank" style="color:var(--accent); text-decoration:none;">Replit</a> Social Media Support Specialist candidate</div>
    <div class="contact-links">
        <a href="mailto:me@sefketnouri.com">me@sefketnouri.com</a>
        <a href="https://www.linkedin.com/in/sefketnouri/" target="_blank">LinkedIn</a>
        <a href="https://replit.com/@sefketnouri" target="_blank">Replit</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Input
st.markdown('<div class="outfit-font" style="font-size:13px; font-weight:600; color:var(--text-secondary); margin-bottom:4px;">Paste messy social input below:</div>', unsafe_allow_html=True)
message = st_keyup("Input", value="my website is down!! I NEED help! I'm losing money", key="msg_input", label_visibility="collapsed")

# Read-only preview
st.markdown(f"""
<div class="tweet-card">
    <div class="tweet-header">
        <div class="avatar">👤</div>
        <div><div class="user-name">Unknown User</div><div class="user-handle">@customer</div></div>
    </div>
    <div class="tweet-content">{message if message else "Waiting for message..."}</div>
</div>
""", unsafe_allow_html=True)

# Analysis
analysis = PriorityTriage.analyze(message)

# Triage Grid
st.markdown(f"""
<div class="triage-grid">
    <div class="badge-card"><div class="badge-label">Intent</div><div class="badge-value">{analysis['intent']}</div></div>
    <div class="badge-card"><div class="badge-label">Sentiment</div><div class="badge-value val-{analysis['sentiment'].lower().replace('/','')}">{analysis['sentiment']}</div></div>
    <div class="badge-card"><div class="badge-label">Urgency</div><div class="badge-value val-{analysis['urgency'].lower()}">{analysis['urgency']}</div></div>
    <div class="badge-card"><div class="badge-label">Risk Level</div><div class="badge-value val-{analysis['risk'].lower()}">{analysis['risk']}</div></div>
    <div class="badge-card"><div class="badge-label">Escalation Flow</div><div class="badge-value" style="font-size:11px;">{analysis['flow']}</div></div>
    <div class="badge-card"><div class="badge-label">Next Step</div><div class="badge-value" style="font-size:11px;">{analysis['next_step']}</div></div>
</div>
""", unsafe_allow_html=True)

# Reasoning Sections
st.markdown(f"""
<div class="result-card">
    <div class="label-accent">AI Reasoning</div>
    <div class="reasoning-text">"{analysis['reasoning']}"</div>
    <div class="label-accent">Suggested Response</div>
    <div style="font-size: 14px; color: #f7f9f9; line-height:1.5;">{analysis['suggested']}</div>
</div>
""", unsafe_allow_html=True)

# Escalation Workflow
if ("Escalate" in analysis['next_step']) or (analysis['urgency'] == "High"):
    st.markdown('<div class="section-title">Escalation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="escalation-box active">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div><div class="badge-label">Status</div><div class="badge-value" style="color:var(--danger);">Required</div></div>
            <div><div class="badge-label">Current Owner</div><div class="badge-value">Support (Triage)</div></div>
            <div><div class="badge-label">Target</div><div class="badge-value">{analysis['target']}</div></div>
        </div>
    """, unsafe_allow_html=True)
    
    # 5. BUTTON LOGIC
    if analysis['is_legal']: btn_label = "Escalate to Exec Slack"
    elif analysis['is_high_confidence_bug']: btn_label = "Escalate to Engineering"
    else: btn_label = "Escalate to Support"
        
    if st.button(btn_label):
        st.session_state.esc_v2 = True
        st.session_state.m_v2 = message
    
    if st.session_state.get('esc_v2') and st.session_state.get('m_v2') == message:
        ch = "#exec-escalations" if "Exec" in analysis['target'] else ("#linear-bugs" if "Engineering" in analysis['target'] else "#support-tickets")
        st.success(f"Escalated to {ch}")
        
        # 6. PAYLOAD UPDATES
        st.markdown(f"""
        <div class="slack-payload">
            <div class="payload-title">Internal Payload: {ch}</div>
            <div class="payload-row"><div class="payload-label">Stage:</div><div>Initial Triage</div></div>
            <div class="payload-row"><div class="payload-label">Owner:</div><div>Support</div></div>
            <div class="payload-row"><div class="payload-label">Priority:</div><div style="color: #dc3545; font-weight: 800;">{analysis['urgency'].upper()}</div></div>
            <div class="payload-label" style="margin-top:10px; margin-bottom:4px;">Draft Summary:</div>
            <div style="background: white; border: 1px solid #dee2e6; padding: 10px; border-radius: 6px; color: #333; font-size:12px;">
                User reporting {analysis['intent'].lower()} affecting customers and revenue. Needs immediate validation.
            </div>
            <div class="payload-label" style="margin-top:12px; margin-bottom:4px;">Original Message:</div>
            <div style="font-style: italic; color: #6c757d; border-left: 3px solid #dee2e6; padding-left: 10px;">"{message}"</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><center style='color: var(--text-secondary); font-size: 11px;'>Sefket Nouri • Multi-Stage Triage Logic • Reactive Engine</center>", unsafe_allow_html=True)
