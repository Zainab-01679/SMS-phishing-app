import streamlit as st
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# =========================
# LOAD MODEL
# =========================
MODEL_PATH = "Mimsss/SMS-phishing-model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()


# =========================
# RULE ENGINE
# =========================
def smart_rules(text):
    t = text.lower()

    safe_patterns = [
        "mtn", "glo", "airtel", "9mobile",
        "*131#", "*556#", "*123#",
        "data bundle", "airtime", "recharge",
        "balance", "subscription", "gb", "mb"
    ]

    risky_patterns = [
        "click link", "verify account", "urgent action",
        "bank account locked", "update kyc",
        "win prize", "lottery", "free money"
    ]

    if any(p in t for p in safe_patterns):
        return "LEGIT_RULE"

    if any(p in t for p in risky_patterns):
        return "PHISH_RULE"

    return None


# =========================
# ML PREDICTION
# =========================
def ml_predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = F.softmax(outputs.logits, dim=1)
    confidence, pred = torch.max(probs, dim=1)

    return pred.item(), confidence.item()


# =========================
# FINAL DECISION ENGINE
# =========================
def predict_sms(text):
    rule = smart_rules(text)

    # Rule-based decisions
    if rule == "LEGIT_RULE":
        return "LEGIT", 0.99, "Recognized telecom/balance message"

    if rule == "PHISH_RULE":
        return "PHISH", 0.99, "Matched common phishing pattern"

    # ML prediction
    pred, conf = ml_predict(text)

    # Confidence threshold
    if conf < 0.65:
        return "UNCERTAIN", conf, "Low confidence prediction"

    label = "PHISH" if pred == 1 else "LEGIT"
    return label, conf, "AI model prediction"


# =========================
# STREAMLIT UI
# =========================
st.set_page_config(
    page_title="SMS Security AI",
    page_icon="📱",
    layout="centered"
)

st.title("📱 SMS Phishing Detection System")
st.write("Detect whether an SMS is Legitimate or a Phishing attempt")

sms = st.text_area("Enter SMS message")

if st.button("Predict"):
    if sms.strip():

        label, confidence, reason = predict_sms(sms)
        percent = confidence * 100

        st.markdown("---")

        if label == "PHISH":
            st.error("⚠️ PHISHING MESSAGE DETECTED")
        elif label == "LEGIT":
            st.success("✅ LEGITIMATE MESSAGE")
        else:
            st.warning("⚠️ UNCERTAIN MESSAGE")

        st.metric("Confidence Score", f"{percent:.2f}%")
        st.progress(confidence)

        st.info(f"🧠 Reason: {reason}")

    else:
        st.warning("Please enter a message")
        
