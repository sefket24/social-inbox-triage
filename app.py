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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

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
        font-family: 'Outfit', sans-serif;
        background-color: var(--bg-main);
        color: var(--text-primary);
    }

    /* Message Card styling */
    .message-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        animation: fadeIn 0.4s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #38444d;
        margin-right: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    .user-name {
        font-weight: 700;
        font-size: 16px;
    }

    .user-handle {
        color: var(--text-secondary);
        font-size: 14px;
    }

    /* Triage Section */
    .triage-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-bottom: 16px;
    }

    .badge-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }

    .badge-label {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-secondary);
        margin-bottom: 2px;
    }

    .badge-value {
        font-weight: 700;
        font-size: 16px;
    }

    /* Status Colors */
    .val-critical, .val-high { color: var(--danger); }
    .val-medium { color: var(--warning); }
    .val-low, .val-positive, .val-billing { color: var(--success); }
    .val-bug { color: #7856ff; }

    /* Featured Response */
    .response-card {
        background: linear-gradient(145deg, #1e2732, #253341);
        border: 1px solid var(--accent);
        border-radius: 12px;
        padding: 16px;
        margin-top: 12px;
        margin-bottom: 24px;
    }

    .response-label {
        color: var(--accent);
        font-weight: 700;
        font-size: 12px;
        margin-bottom: 4px;
        text-transform: uppercase;
    }

    .reasoning {
        font-size: 13px;
        font-style: italic;
        color: var(--text-secondary);
        margin-bottom: 12px;
        line-height: 1.3;
        border-left: 2px solid var(--accent);
        padding-left: 10px;
    }

    /* Tone Check Section */
    .tone-section {
        border-top: 1px solid var(--border);
        padding-top: 24px;
        margin-top: 24px;
    }

    .risk-ribbon {
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 2px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 12px;
    }
    .risk-high { background: rgba(244, 33, 46, 0.2); color: var(--danger); }
    .risk-medium { background: rgba(255, 173, 31, 0.2); color: var(--warning); }
    .risk-low { background: rgba(0, 186, 124, 0.2); color: var(--success); }

    .issue-item {
        font-size: 13px;
        color: var(--text-secondary);
        margin: 4px 0;
    }
    .issue-item::before { content: "• "; color: var(--warning); }

    .improved-box {
        background: rgba(0, 186, 124, 0.05);
        border: 1px dashed var(--success);
        border-radius: 8px;
        padding: 12px;
        margin-top: 12px;
    }

    /* Override Streamlit input */
    .stTextInput input {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        font-size: 15px !important;
    }

    .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(29, 155, 240, 0.2) !important;
    }

    /* Mobile adjustments */
    @media (max-width: 600px) {
        .triage-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    /* Hide Streamlit elements */
    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; display: none; }
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
class TriageAI:
    @staticmethod
    def analyze(text):
        text = text.lower()
        intent, sentiment, urgency, risk, channel, action = "Question", "Neutral", "Low", "Low", "Public", "Reply Publicly"
        reasoning = "Standard inquiry detected."
        suggested = "Hi! Thanks for reaching out. How can I help you with this?"

        if any(w in text for w in ["bug", "fail", "error", "broken", "fix"]): 
            intent, action = "Bug", "Escalate Internally"
        elif any(w in text for w in ["charge", "billing", "money", "paid", "refund"]): 
            intent, channel, action = "Billing", "Private (DM)", "Move to DM"
        elif any(w in text for w in ["feature", "request", "add", "can you"]): 
            intent = "Feature"
        
        if any(w in text for w in ["charged twice", "wtf", "now", "fix this", "??", "!!"]): 
            sentiment, urgency, risk = "Negative", "High", "High"
        elif any(w in text for w in ["lol", "thanks", "wow", "love"]): 
            sentiment = "Positive"

        if intent == "Billing" and sentiment == "Negative":
            reasoning = "Detected duplicate charge complaint. Sensitive data requires private channel move."
            suggested = "I'm so sorry about the double charge! That sounds frustrating. Can you send us a DM with your email so I can fix this right away?"
        elif intent == "Bug" and urgency == "High":
            reasoning = "Critical functional failure reported. Immediate internal escalation recommended."
            suggested = "I'm really sorry to hear your projects disappeared—that shouldn't happen. DM us your account details and I’ll get our senior engineers on this now."
        elif "dark mode" in text:
            reasoning = "Product feedback regarding feature parity. Low urgency, high engagement opportunity."
            suggested = "I hear you! Dark mode is a top request. I'll make sure the product team knows it's still missing in 2026. Stay tuned! 🌑"
        elif "fail lol" in text:
            reasoning = "Snarky feedback reporting UX failure. Medium risk due to public visibility."
            suggested = "Ouch, definitely not the experience we want for you. Which deploy failed? I'd love to dig into this for you."

        return {"intent": intent, "sentiment": sentiment, "urgency": urgency, "risk": risk, "channel": channel, "action": action, "reasoning": reasoning, "suggested_response": suggested}

class ToneAI:
    @staticmethod
    def analyze(text):
        text_lower = text.lower()
        risk, issues, improved = "Low", ["No major issues"], text
        
        if any(w in text_lower for w in ["fault", "wrong", "you must", "read the docs"]):
            risk, issues = "High", ["Blames user", "Defensive tone"]
            improved = "I’m sorry you’re running into this. Let’s double-check the settings together."
        elif any(w in text_lower for w in ["already told", "told you", "we said"]):
            risk, issues = "High", ["Defensive", "Condescending"]
            improved = "I apologize for any confusion! Let me try to clarify that status for you."
        elif any(w in text_lower for w in ["idk", "don't know", "working on our end"]):
            risk, issues = "Medium", ["Dismissive", "Short tone"]
            improved = "It looks like our systems are green, but I want to make sure your case is solved."
        
        return {"risk": risk, "issues": issues, "improved": improved}

# --- APP UI ---
st.title("📥 Social Inbox Triage")
st.caption("AI-Powered Support Co-Pilot • Real-time Stream")

# Inbound Message
st.markdown('<div class="message-card">', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 10])
with col_a: st.markdown('<div class="avatar">👤</div>', unsafe_allow_html=True)
with col_b: st.markdown('<div class="user-name">Unknown User</div><div class="user-handle">@customer</div>', unsafe_allow_html=True)
message = st_keyup("Incoming message", value="your app just charged me twice?? what is this", key="msg_input", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Triage Results
analysis = TriageAI.analyze(message)
st.markdown(f"""
<div class="triage-grid">
    <div class="badge-card"><div class="badge-label">Intent</div><div class="badge-value val-{analysis['intent'].lower()}">{analysis['intent']}</div></div>
    <div class="badge-card"><div class="badge-label">Sentiment</div><div class="badge-value val-{analysis['sentiment'].lower()}">{analysis['sentiment']}</div></div>
    <div class="badge-card"><div class="badge-label">Urgency</div><div class="badge-value val-{analysis['urgency'].lower()}">{analysis['urgency']}</div></div>
    <div class="badge-card"><div class="badge-label">Risk Level</div><div class="badge-value val-{analysis['risk'].lower()}">{analysis['risk']}</div></div>
    <div class="badge-card"><div class="badge-label">Channel</div><div class="badge-value">{analysis['channel']}</div></div>
    <div class="badge-card"><div class="badge-label">Action</div><div class="badge-value">{analysis['action']}</div></div>
</div>
""", unsafe_allow_html=True)

# Suggested Response
st.markdown(f"""
<div class="response-card">
    <div class="response-label">AI REASONING</div>
    <div class="reasoning">"{analysis['reasoning']}"</div>
    <div class="response-label">SUGGESTED RESPONSE</div>
    <div style="font-size: 15px; color: #f7f9f9;">{analysis['suggested_response']}</div>
</div>
""", unsafe_allow_html=True)

# Tone Check Section
st.markdown('<div class="tone-section">', unsafe_allow_html=True)
st.subheader("✍️ Tone check")
st.markdown('<p style="color: var(--text-secondary); font-size: 13px; margin-top: -10px;">Refine and verify the draft before sending.</p>', unsafe_allow_html=True)

# Handle dynamic default for Tone Check
if 'last_suggested' not in st.session_state: st.session_state.last_suggested = analysis['suggested_response']
if st.session_state.last_suggested != analysis['suggested_response']:
    st.session_state.last_suggested = analysis['suggested_response']
    # Force key change to reset the keyup component if suggested response changes
    st.session_state.tone_key = f"tone_{time.time()}" 
if 'tone_key' not in st.session_state: st.session_state.tone_key = "tone_init"

draft = st_keyup("Edit reply", value=analysis['suggested_response'], key=st.session_state.tone_key, label_visibility="collapsed")
tone_analysis = ToneAI.analyze(draft)

# Tone Analysis Output
risk_c = f"risk-{tone_analysis['risk'].lower()}"
st.markdown(f'<div class="risk-ribbon {risk_c}">{tone_analysis["risk"]} Tone Risk</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<div style="font-weight: 700; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">ISSUES</div>', unsafe_allow_html=True)
    for issue in tone_analysis['issues']: st.markdown(f'<div class="issue-item">{issue}</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="improved-box">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight: 700; font-size: 11px; color: var(--success); margin-bottom: 4px;">IMPROVED VERSION</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size: 13px; color: #f7f9f9;">"{tone_analysis["improved"]}"</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br><center style='color: #8b98a5; font-size: 11px;'>Refinement > Expansion • Reactive Engine v2.1</center>", unsafe_allow_html=True)
