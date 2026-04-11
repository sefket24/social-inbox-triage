import streamlit as st

st.set_page_config(page_title="Social Inbox Triage", layout="centered")

st.markdown("""
<style>
.top-section { margin-bottom: 1.5rem; }
.top-section h3 { margin-bottom: 0.1rem; font-size: 1.1rem; }
.top-section p { margin: 0.1rem 0; font-size: 0.9rem; color: #555; }
.top-section .flow { margin-top: 0.5rem; font-size: 0.85rem; color: #888; }
.label-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.4rem 0; }
.badge { padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 500; }
.badge-intent { background: #e8f0fe; color: #1a56db; }
.badge-sentiment-neg { background: #fde8e8; color: #c81e1e; }
.badge-sentiment-pos { background: #e8f8e8; color: #1a7a1a; }
.badge-sentiment-neu { background: #f0f0f0; color: #444; }
.badge-sentiment-mix { background: #fff3e0; color: #b45309; }
.badge-urgency-high { background: #fde8e8; color: #c81e1e; }
.badge-urgency-med { background: #fff3e0; color: #b45309; }
.badge-urgency-low { background: #e8f8e8; color: #1a7a1a; }
.badge-channel { background: #f3e8ff; color: #6d28d9; }
.badge-route { background: #e8f0fe; color: #1e40af; }
.triage-box { border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 1.2rem; background: #fafafa; }
.triage-box h4 { margin: 0 0 0.5rem 0; font-size: 0.95rem; color: #111; }
.suggested { margin-top: 0.8rem; font-size: 0.875rem; color: #333; background: #f0f4ff; padding: 0.6rem 0.9rem; border-radius: 6px; border-left: 3px solid #3b82f6; }
.footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; font-size: 0.8rem; color: #999; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Top section
st.markdown("""
<div class="top-section">
<h3>Sefket Nouri</h3>
<p>Social Media Support Specialist candidate</p>
<p>Support issues repeat. I built small tools to reduce that friction across deployment, billing, and inbound triage.</p>
<p class="flow">Start with: Deployment Debugger → Support Gatekeeper → Social Inbox Triage</p>
</div>
""", unsafe_allow_html=True)

st.markdown("**Demo:** How inbound social messages can be triaged before they become support tickets.")
st.markdown("---")


def classify(text):
    t = text.lower().strip()

    if len(t) < 5 or not any(c.isalpha() for c in t):
        return None

    # Intent
    bug_words = ["stopped", "broken", "not working", "error", "crash", "bug", "failing", "down", "repl stopped", "won't", "wont", "cant", "can't", "issue", "problem", "fix", "idk why"]
    billing_words = ["charge", "charged", "refund", "billing", "invoice", "payment", "subscription", "plan", "money", "price", "cost", "fee", "paid", "paying"]
    feature_words = ["add", "feature", "would be great", "wish", "suggest", "suggestion", "could you", "please add", "support for", "when will"]
    feedback_words = ["love", "great", "awesome", "amazing", "terrible", "hate", "worst", "best", "thank", "thanks"]
    question_words = ["does", "do you", "can i", "is there", "how do", "what is", "does replit", "support", "?"]

    if any(w in t for w in billing_words):
        intent = "billing"
    elif any(w in t for w in bug_words):
        intent = "bug"
    elif any(w in t for w in feature_words):
        intent = "feature request"
    elif any(w in t for w in feedback_words) and not any(w in t for w in question_words):
        intent = "feedback"
    elif any(w in t for w in question_words):
        intent = "question"
    else:
        intent = "question"

    # Sentiment
    neg_words = ["stopped", "broken", "not working", "error", "crash", "hate", "worst", "terrible", "awful", "angry", "frustrated", "disappointed", "😭", "😤", "😡", "wtf", "omg", "ugh"]
    pos_words = ["love", "great", "awesome", "amazing", "thank", "thanks", "perfect", "best", "helpful", "❤️", "🙏", "😊", "👍"]

    has_neg = any(w in t for w in neg_words)
    has_pos = any(w in t for w in pos_words)

    if has_neg and has_pos:
        sentiment = "mixed"
    elif has_neg:
        sentiment = "negative"
    elif has_pos:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    # Urgency
    urgent_words = ["stopped", "broken", "not working", "error", "crash", "urgent", "asap", "immediately", "right now", "emergency", "production", "😭"]
    low_words = ["feature", "suggestion", "love", "great", "just wondering", "does", "do you support"]

    if any(w in t for w in urgent_words):
        urgency = "high"
    elif any(w in t for w in low_words):
        urgency = "low"
    else:
        urgency = "medium"

    # Channel
    dm_words = ["dm", "direct", "private", "account", "password", "email", "login", "billed", "charged", "payment"]
    channel = "private" if any(w in t for w in dm_words) else "public"

    # Route
    if intent == "billing":
        route = "support"
        response = "Acknowledge publicly if on a public channel, then move to DM. Route to billing support with account details."
    elif intent == "bug" and sentiment == "negative" and channel == "public":
        route = "support"
        response = "Acknowledge issue publicly and move to DM for details."
    elif intent == "bug":
        route = "support"
        response = "Ask for error details and environment info. Route to support if unresolved."
    elif intent == "question":
        route = "docs"
        response = "Reply with the relevant docs link. Keep it brief and direct."
    elif intent == "feature request":
        route = "community"
        response = "Thank them and point to the feature request board or community forum."
    elif intent == "feedback" and sentiment == "positive":
        route = "community"
        response = "Reply with a short thank-you. No escalation needed."
    elif intent == "feedback" and sentiment == "negative":
        route = "support"
        response = "Acknowledge the frustration and ask what specifically went wrong."
    else:
        route = "support"
        response = "Review manually and determine best path."

    return {
        "intent": intent,
        "sentiment": sentiment,
        "urgency": urgency,
        "channel": channel,
        "route": route,
        "response": response,
    }


sentiment_class = {
    "negative": "badge-sentiment-neg",
    "positive": "badge-sentiment-pos",
    "neutral": "badge-sentiment-neu",
    "mixed": "badge-sentiment-mix",
}

urgency_class = {
    "high": "badge-urgency-high",
    "medium": "badge-urgency-med",
    "low": "badge-urgency-low",
}


def render_triage(label, text):
    result = classify(text)
    st.markdown(f"**{label}**")
    st.code(text, language=None)

    if result is None:
        st.warning("Could not determine intent. Try a full message.")
        return

    sc = sentiment_class.get(result["sentiment"], "badge-sentiment-neu")
    uc = urgency_class.get(result["urgency"], "badge-urgency-med")

    st.markdown(f"""
    <div class="triage-box">
      <div class="label-row">
        <span class="badge badge-intent">Intent: {result['intent']}</span>
        <span class="badge {sc}">Sentiment: {result['sentiment']}</span>
        <span class="badge {uc}">Urgency: {result['urgency']}</span>
        <span class="badge badge-channel">Channel: {result['channel']}</span>
        <span class="badge badge-route">Route: {result['route']}</span>
      </div>
      <div class="suggested">💬 {result['response']}</div>
    </div>
    """, unsafe_allow_html=True)


# Input
user_input = st.text_area(
    "Paste a tweet, DM, or comment",
    value="yo my repl stopped working and idk why 😭",
    height=80,
)

render_triage("Your input", user_input)

st.markdown("---")

# Second example
render_triage("Example", "does replit support python 3.12?")

# Footer
st.markdown("""
<div class="footer">
Sefket Nouri — Social Media Support Specialist<br>
Focused on reducing repeat support issues through tooling and systems thinking<br>
LinkedIn · View implementation on Replit
</div>
""", unsafe_allow_html=True)
