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
    .stButton>button { width: 100%; background-color: var(--accent) !important; color: white !important; font-weight: 700 !important; border: none !important; border-radius: 8px !important; padding: 10px !important; }

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
        
        # 1. HARD OVERRIDE FOR LEGAL THREATS (FIRST CHECK)
        legal_keywords = ["lawyer", "sue", "legal", "attorney", "suing", "lawsuit"]
        is_legal = any(w in text_l for w in legal_keywords)
        
        if is_legal:
            return {
                "intent": "Legal / Complaint",
                "sentiment": "Negative",
                "urgency": "High",
                "risk": "High",
                "owner": "Exec (Slack)",
                "target": "Exec (Slack)",
                "next_step": "Escalate to Exec (Slack)",
                "flow": "Direct to Exec",
                "reasoning": "Legal risk override. Directing to executive leadership.",
                "suggested": "I hear your concern. I've escalated this specifically to our senior leadership team to address this with you.",
                "is_confirmed": False,
                "is_legal": True,
                "channel": "Public"
            }
        
        # 2. SIGNAL DETECTION (WEIGHTED)
        is_enterprise = "enterprise" in text_l
        is_outage = any(w in text_l for w in ["site is down", "website is down", "app is down", "service is down", "not loading"])
        is_billing = any(w in text_l for w in ["charged", "billing", "payment", "refund", "billed"])
        is_frustrated = any(w in text_l for w in ["no response", "still waiting", "what's going on", "not working", "disappeared"]) or "??" in text_l
        is_confused = any(w in text_l for w in ["idk", "what happened"]) or "??" in text_l
        is_feature = any(w in text_l for w in ["do you have", "is there a way to", "feature"])
        
        # Sarcasm check
        has_sarcasm = ("love this" in text_l or "great job" in text_l or "love getting" in text_l) and (is_billing or is_frustrated or "twice" in text_l)
        
        # Intensity
        has_multi_bang = "!!" in text
        has_caps = len(re.findall(r'\b[A-Z]{3,}\b', text)) >= 2
        
        # 3. BASE CLASSIFICATION
        sentiment, urgency, risk, intent = "Neutral", "Low", "Low", "Question"
        next_step, owner, flow = "Reply Publicly", "Support (Zendesk)", "Support → Engineering (if needed)"
        target = "Support (Zendesk)"
        channel = "Public"
        
        # Intent mapping
        if is_feature: intent = "Feature request"
        elif is_billing: intent = "Billing"
        elif is_outage: intent = "Outage"
        elif has_sarcasm: intent = "Complaint"
        elif is_enterprise: intent = "Enterprise"
        
        # Sentiment mapping
        if is_frustrated or is_confused or is_billing or is_outage:
            sentiment = "Negative"
        if has_sarcasm:
            sentiment = "Mixed / Negative"
            
        # Urgency & Risk mapping (Weighted)
        if is_frustrated or is_confused or is_billing: 
            urgency = "Medium"
        if is_billing:
            risk = "Medium"
        if is_enterprise:
            urgency = "High"
            risk = "High"
        if is_outage:
            urgency = "High"
            risk = "Medium"

        # Intensity boost
        if (has_multi_bang or has_caps) and urgency == "Low":
            urgency = "Medium"
        elif (has_multi_bang or has_caps) and urgency == "Medium":
            urgency = "High"

        # 4. NEXT STEP LOGIC (Based on Urgency)
        if urgency == "High":
            next_step = "Reply immediately (Offer DM)"
        elif urgency == "Medium":
            next_step = "Reply (Offer DM)"
        
        # 5. REASONING & SUGGESTED
        reasoning = "Signal-based triage weighing tone, urgency, and subject matter."
        
        # Suggested Response Selection (Human, concise, agent-like)
        if is_legal:
            suggested = "Understood — we’re taking this seriously. Our team will follow up directly."
        elif urgency == "High" or is_outage:
            suggested = "Got it — that sounds urgent. Can you DM details so we can check this right away?"
        elif is_billing:
            suggested = "Hey — that’s not expected. Can you DM your account email so we can take a look?"
        elif is_feature:
            suggested = "Good question — not available yet, but happy to pass this along to the team."
        elif any(w in text_l for w in ["memory", "port", "limit", "fail", "error"]):
            suggested = "That looks like a configuration issue. Try checking your resource limits and redeploying — let me know if it still fails."
        elif has_sarcasm or sentiment == "Negative":
            suggested = "Appreciate the feedback — can you share more about what didn’t work for you?"
        else:
            suggested = "Hey — that’s not expected. Can you share a bit more detail so we can help figure this out?"
        
        is_confirmed = False
        if is_outage:
            # Check for Engineering triggers
            is_system_bug = any(w in text_l for w in ["reproducible bug", "system-wide failure", "confirmed bug", "broken for everyone"])
            is_multi_user = any(w in text_l for w in ["multiple users", "all users", "many people"])
            if is_system_bug or is_multi_user:
                target, flow, is_confirmed = "Engineering (Linear)", "Confirmed Bug Path", True
                reasoning = "Verified system-wide failure detected. Escalating to Engineering."
            else:
                reasoning = "Potential outage reported. Support team currently validating reproducibility."
        
        if is_feature:
            reasoning = "Routine feature request. Logging for product review."

        return {
            "intent": intent, "sentiment": sentiment, "urgency": urgency, "risk": risk,
            "next_step": next_step, "channel": channel, "target": target, "flow": flow, "owner": owner,
            "reasoning": reasoning, "suggested": suggested, 
            "is_confirmed": is_confirmed, "is_legal": is_legal
        }

# --- APP UI ---
st.title("📥 Social Inbox Triage")
st.caption("Support-First decision Engine • Multi-Stage validation Active")

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
message = st_keyup("Incoming message", value="my website is down!! I'm losing money", key="msg_input")

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
    <div class="badge-card"><div class="badge-label">Current Owner</div><div class="badge-value" style="font-size:11px;">{analysis['owner']}</div></div>
    <div class="badge-card"><div class="badge-label">Next Step</div><div class="badge-value" style="font-size:11px;">{analysis['next_step']}</div></div>
</div>
""", unsafe_allow_html=True)

# Reasoning
st.markdown(f"""
<div class="result-card">
    <div class="label-accent">AI Reasoning</div>
    <div class="reasoning-text">"{analysis['reasoning']}"</div>
    <div class="label-accent">Suggested Response</div>
    <div style="font-size: 14px; color: #f7f9f9; line-height:1.5;">{analysis['suggested']}</div>
</div>
""", unsafe_allow_html=True)

# Escalation Workflow
if (analysis['risk'].upper() == "HIGH") or (analysis['urgency'].upper() == "HIGH"):
    st.markdown('<div class="section-title">Escalation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="escalation-box active">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div><div class="badge-label">Status</div><div class="badge-value" style="color:var(--danger);">Required</div></div>
            <div><div class="badge-label">Flow</div><div class="badge-value" style="font-size:11px;">{analysis['flow']}</div></div>
            <div><div class="badge-label">Target</div><div class="badge-value">{analysis['target']}</div></div>
        </div>
    """, unsafe_allow_html=True)
    
    # 5. BUTTON DYNAMIC LOGIC
    if analysis['is_legal']: btn_label = "Escalate to Exec Slack"
    elif analysis['is_confirmed']: btn_label = "Escalate to Engineering"
    else: btn_label = "Escalate to Support"
        
    if st.button(btn_label):
        st.session_state.esc_v3 = True
        st.session_state.m_v3 = message
    
    if st.session_state.get('esc_v3') and st.session_state.get('m_v3') == message:
        ch = "#exec-escalations" if "Exec" in analysis['target'] else ("#linear-bugs" if "Engineering" in analysis['target'] else "#support-tickets")
        st.success(f"Escalated to {ch}")
        st.markdown(f"""
        <div class="slack-payload">
            <div class="payload-title">Internal Payload: {ch}</div>
            <div class="payload-row"><div class="payload-label">Priority:</div><div style="color: #dc3545; font-weight: 800;">{analysis['urgency'].upper()}</div></div>
            <div class="payload-row"><div class="payload-label">Owner:</div><div>{analysis['owner']}</div></div>
            <div class="payload-label" style="margin-top:10px; margin-bottom:4px;">Draft Summary:</div>
            <div style="background: white; border: 1px solid #dee2e6; padding: 10px; border-radius: 6px; color: #333; font-size:12px;">
                {analysis['intent']} detected. Stage: Initial triage. Action: Validate impact before technical escalation.
            </div>
            <div class="payload-label" style="margin-top:12px; margin-bottom:4px;">Original Message:</div>
            <div style="font-style: italic; color: #6c757d; border-left: 3px solid #dee2e6; padding-left: 10px;">"{message}"</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><center style='color: var(--text-secondary); font-size: 11px;'>Sefket Nouri • Support-First Validation Flow • Reactive Mode</center>", unsafe_allow_html=True)
