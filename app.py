%%writefile app.py

import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "Mimsss/SMS-phishing-model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# ---------------- RULE SYSTEM ---------------- #
def smart_rules(text):
    t = text.lower()

    telecom_keywords = [
        "mtn", "airtel", "glo", "9mobile",
        "balance", "recharged", "credited",
        "data bundle", "valid till", "bonus"
    ]

    phishing_keywords = [
        "click", "verify", "urgent", "suspend",
        "login", "account blocked", "claim",
        "win", "prize", "bvn"
    ]

    if "http" in t or "www" in t:
        return "PHISHING_RULE"

    if any(word in t for word in phishing_keywords):
        return "PHISHING_RULE"

    if any(word in t for word in telecom_keywords):
        return "LEGIT_RULE"

    return "UNKNOWN"

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="SMS Threat Dashboard", layout="wide")

# ---------------- HEADER ---------------- #
st.title("SMS Threat Intelligence Dashboard")
st.caption("Hybrid AI + Rule-Based Smishing Detection System")

# ---------------- LAYOUT ---------------- #
col1, col2 = st.columns([2, 1])

with col1:
    text = st.text_area("Enter SMS Message", height=150)

with col2:
    st.subheader("System Status")
    st.write("Model: Active")
    st.write("Rules Engine: Active")

# ---------------- ANALYSIS ---------------- #
if st.button("Run Analysis"):

    rule = smart_rules(text)

    if rule == "LEGIT_RULE":
        prediction = "LEGIT"
        confidence = 0.95
        reason = "Recognized telecom/balance message"

    elif rule == "PHISHING_RULE":
        prediction = "PHISHING"
        confidence = 0.95
        reason = "Matched phishing pattern"

    else:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)

        probs = torch.nn.functional.softmax(outputs.logits, dim=1)
        confidence = torch.max(probs).item()
        pred = torch.argmax(probs).item()

        if confidence < 0.6:
            prediction = "UNCERTAIN"
            reason = "Low confidence prediction"
        else:
            prediction = "PHISHING" if pred == 1 else "LEGIT"
            reason = "AI model prediction"

    # ---------------- RESULTS ---------------- #
    st.subheader("Analysis Result")

    st.write("Prediction:", prediction)
    st.write("Confidence Score:", round(confidence, 2))
    st.write("Detection Reason:", reason)

    # ---------------- CONFIDENCE BAR ---------------- #
    st.subheader("Confidence Level")
    st.progress(int(confidence * 100))

    # ---------------- RULE OUTPUT ---------------- #
    st.subheader("Rule Engine Output")
    st.write(rule)
