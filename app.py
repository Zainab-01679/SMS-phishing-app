
import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "/content/fine_tuned_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

def predict_sms(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    pred = torch.argmax(outputs.logits, dim=1).item()
    return pred

st.title("📱 SMS Phishing Detection App")

sms = st.text_area("Enter SMS message")

if st.button("Predict"):
    if sms.strip():
        result = predict_sms(sms)

        if result == 1:
            st.error("⚠️ Phishing Message Detected!")
        else:
            st.success("✅ Legitimate Message")
