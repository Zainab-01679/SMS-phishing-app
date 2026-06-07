import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "Mimsss/SMS-phishing-model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

import torch
import torch.nn.functional as F

def predict_sms(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    probs = F.softmax(outputs.logits, dim=1)
    confidence, pred = torch.max(probs, dim=1)

    return pred.item(), confidence.item()

st.set_page_config(page_title="SMS Phishing Detector", page_icon="📱", layout="centered")

st.title("📱 SMS Phishing Detection App")
st.write("Check if an SMS is safe or a phishing attempt")

sms = st.text_area("Enter SMS message here")

if st.button("Predict"):
    if sms.strip():

        label, confidence = predict_sms(sms)
        percent = confidence * 100

        st.markdown("---")

        if label == 1:
            st.error("⚠️ Phishing Message Detected!")
        else:
            st.success("✅ Legitimate Message")

        st.metric(label="Confidence Score", value=f"{percent:.2f}%")

        st.progress(confidence)

    else:
        st.warning("Please enter a message")
