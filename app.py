import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "Mimsss/SMS-phishing-model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

def smart_rules(text):
    t = text.lower()

    # SAFE telecom patterns (VERY IMPORTANT)
    safe_patterns = [
        "mtn", "glo", "airtel", "9mobile",
        "*131#", "*556#", "*123#",
        "data bundle", "airtime", "recharge",
        "balance", "subscription", "gb", "mb"
    ]

    # HIGH RISK phishing patterns
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

import torch
import torch.nn.functional as F

def ml_predict(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = F.softmax(outputs.logits, dim=1)
    confidence, pred = torch.max(probs, dim=1)

    return pred.item(), confidence.item()

    def predict_sms(text):
    rule = smart_rules(text)

    # CASE 1: SAFE RULE (MTN, Airtime, etc.)
    if rule == "LEGIT_RULE":
        return "LEGIT", 0.99, "Matched telecom/bank safe pattern"

    # CASE 2: HIGH RISK RULE
    if rule == "PHISH_RULE":
        return "PHISH", 0.99, "Matched known phishing pattern"

    # CASE 3: ML MODEL
    pred, conf = ml_predict(text)

    # confidence threshold (VERY IMPORTANT)
    if conf < 0.65:
        return "UNCERTAIN", conf, "Low confidence model prediction"

    label = "PHISH" if pred == 1 else "LEGIT"
    reason = "AI model prediction"

    return label, conf, reason

st.set_page_config(page_title="SMS Security AI", page_icon="📱", layout="centered")

st.title("📱 SMS Security Detection System")
st.write("Production-grade phishing detection using AI + rules")

sms = st.text_area("Enter SMS message")

if st.button("Analyze"):

    if sms.strip():

        label, confidence, reason = predict_sms(sms)
        percent = confidence * 100

        st.markdown("---")

        if label == "PHISH":
            st.error("⚠️ PHISHING DETECTED")
        elif label == "LEGIT":
            st.success("✅ LEGITIMATE MESSAGE")
        else:
            st.warning("⚠️ UNCERTAIN MESSAGE")

        st.metric("Confidence Score", f"{percent:.2f}%")
        st.progress(confidence)

        st.info(f"🧠 Reason: {reason}")

    else:
        st.warning("Please enter a message")
