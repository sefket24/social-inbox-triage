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
        --border: #38444d;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: var(--bg-main);
        color: var(--text-primary);
    }

    [data-testid="stHeader"] {
        background-color: rgba(21, 32, 43, 0.8);
        backdrop-filter: blur(12px);
    }

    /* Message Card styling */
    .message-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        animation: fadeIn 0.5s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .message-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
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

    .user-info {
        flex-grow: 1;
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

    /* Colors */
    .val-critical { color: #f4212e; }
    .val-high { color: #f4212e; }
    .val-medium { color: #ffad1f; }
    .val-low { color: #00ba7c; }
    .val-positive { color: #00ba7c; }
    .val-negative { color: #f4212e; }
    .val-bug { color: #7856ff; }
    .val-billing { color: #00ba7c; }

    /* Featured Response */
    .response-card {
        background: linear-gradient(145deg, #1e2732, #253341);
        border: 1px solid var(--accent);
        border-radius: 12px;
        padding: 16px;
        margin-top: 12px;
    }

    .response-label {
        color: var(--accent);
        font-weight: 700;
        font-size: 12px;
        margin-bottom: 4px;
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

    /* Override Streamlit input */
    .stTextInput input {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
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
    /* Hide Streamlit elements for a cleaner pro-tool feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
</style>
""", unsafe_allow_html=True)

# --- LOGIC ---
class TriageAI:
    @staticmethod
    def analyze(text):
        text = text.lower()
        
        # Default states
        intent = "Question"
        sentiment = "Neutral"
        urgency = "Low"
        risk = "Low"
        channel = "Public"
        action = "Reply Publicly"
        reasoning = "Standard inquiry detected."
        suggested_response = "Hi! Thanks for reaching out. How can I help you with this?"

        # 1. Detect Intent
        if any(w in text for w in ["bug", "fail", "error", "broken", "disappeared", "fix"]):
            intent = "Bug"
        elif any(w in text for w in ["charge", "billing", "money", "paid", "refund", "price"]):
            intent = "Billing"
        elif any(w in text for w in ["feature", "request", "add", "can you"]):
            intent = "Feature"
        elif any(w in text for w in ["love", "thanks", "great", "awesome", "lol"]):
            intent = "Feedback"

        # 2. Detect Sentiment
        if any(w in text for w in ["charged twice", "wtf", "now", "fix this", "??", "!!"]):
            sentiment = "Negative"
        elif any(w in text for w in ["lol", "thanks", "wow", "love"]):
            sentiment = "Positive"
        elif any(w in text for w in ["maybe", "idk", "but"]):
            sentiment = "Mixed"

        # 3. Detect Urgency & Risk
        if any(w in text for w in ["fix this now", "randomly fail", "disappeared", "charged twice"]):
            urgency = "High"
            risk = "High"
        elif "!" in text or "?" in text:
            urgency = "Medium"
        
        # 4. Channel Logic
        if intent == "Billing" or risk == "High":
            channel = "Private (DM)"
            action = "Move to DM"
        elif intent == "Bug":
            action = "Escalate Internally"
        elif intent == "Feedback" and sentiment == "Positive":
            action = "Reply Publicly"
        
        # 5. Reasoning & Response Generation (Dynamic Templates)
        if intent == "Billing" and sentiment == "Negative":
            reasoning = "Detected duplicate charge complaint. Sensitive financial data requires private channel move."
            suggested_response = "I'm so sorry about the double charge! That sounds frustrating. Can you send us a DM with your email so I can fix this right away?"
        
        elif intent == "Bug" and urgency == "High":
            reasoning = "Critical functional failure reported. Immediate internal escalation recommended."
            suggested_response = "I'm really sorry to hear your projects disappeared—that shouldn't happen. DM us your account details and I’ll get our senior engineers on this now."
        
        elif text.strip() == "":
            reasoning = "Waiting for input..."
            suggested_response = "I'm ready to help! Paste a message above."
        
        elif "dark mode" in text:
            reasoning = "Product feedback regarding feature parity. Low urgency, high engagement opportunity."
            suggested_response = "I hear you! Dark mode is a top request. I'll make sure the product team knows it's still missing in 2026. Stay tuned! 🌑"

        elif "fail lol" in text:
            reasoning = "Snarky feedback reporting UX failure. Medium risk due to public visibility."
            suggested_response = "Ouch, definitely not the experience we want for you. Which deploy failed? I'd love to dig into this for you."

        return {
            "intent": intent,
            "sentiment": sentiment,
            "urgency": urgency,
            "risk": risk,
            "channel": channel,
            "action": action,
            "reasoning": reasoning,
            "suggested_response": suggested_response
        }

# --- APP UI ---
st.title("📥 Social Inbox Triage")
st.caption("AI-Powered Support Co-Pilot • Real-time Stream")

# Input Section (Styled like a Message Card)
st.markdown('<div class="message-card">', unsafe_allow_html=True)
col_a, col_b = st.columns([1, 10])
with col_a:
    st.markdown('<div class="avatar">👤</div>', unsafe_allow_html=True)
with col_b:
    st.markdown('<div class="user-name">Unknown User</div><div class="user-handle">@customer</div>', unsafe_allow_html=True)

# THE INPUT
default_text = "your app just charged me twice?? what is this"
message = st_keyup("Incoming message", value=default_text, key="msg_input", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Analysis
analysis = TriageAI.analyze(message)

# Triage Metrics Grid
st.markdown(f"""
<div class="triage-grid">
    <div class="badge-card">
        <div class="badge-label">Intent</div>
        <div class="badge-value val-{analysis['intent'].lower()}">{analysis['intent']}</div>
    </div>
    <div class="badge-card">
        <div class="badge-label">Sentiment</div>
        <div class="badge-value val-{analysis['sentiment'].lower()}">{analysis['sentiment']}</div>
    </div>
    <div class="badge-card">
        <div class="badge-label">Urgency</div>
        <div class="badge-value val-{analysis['urgency'].lower()}">{analysis['urgency']}</div>
    </div>
    <div class="badge-card">
        <div class="badge-label">Risk Level</div>
        <div class="badge-value val-{analysis['risk'].lower()}">{analysis['risk']}</div>
    </div>
    <div class="badge-card">
        <div class="badge-label">Channel</div>
        <div class="badge-value">{analysis['channel']}</div>
    </div>
    <div class="badge-card">
        <div class="badge-label">Action</div>
        <div class="badge-value">{analysis['action']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# AI Insights
st.markdown(f"""
<div class="response-card">
    <div class="response-label">AI REASONING</div>
    <div class="reasoning">"{analysis['reasoning']}"</div>
    <div class="response-label">SUGGESTED RESPONSE</div>
    <div style="font-size: 15px; line-height: 1.5; color: #f7f9f9;">
        {analysis['suggested_response']}
    </div>
</div>
""", unsafe_allow_html=True)

# Footer info
st.markdown("<br><center style='color: #8b98a5; font-size: 12px;'>Reactive Engine v2.0 • Scanning active...</center>", unsafe_allow_html=True)
