import streamlit as st
import requests
import pandas as pd

st.title("🏥 AI Hospital Assistant")

# Loading the doctor database
doctors = pd.read_csv("doctors.csv")

# Chat memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
user_input = st.chat_input("Ask about doctors, timings, appointments...")

if user_input:

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    question = user_input.lower()

    department = None

    # Symptom / keyword detection
    if "skin" in question:
        department = "Dermatology"

    elif "ear" in question:
        department = "Otolaryngology"

    elif "heart" in question or "chest pain" in question:
        department = "Cardiology"

    elif "brain" in question or "headache" in question:
        department = "Neurology"

    elif "bone" in question or "fracture" in question:
        department = "Orthopedic"

    elif "fever" in question or "cough" in question:
        department = "General Medicine"

    # Search doctor database
    if department:

        doctor_info = doctors[
            doctors["department"].str.lower() == department.lower()
        ]

        if not doctor_info.empty:

            doc = doctor_info.iloc[0]

            answer = f"""
Doctor available for your problem:

Doctor: {doc['doctor']}\n
Department: {doc['department']}\n
Available time: {doc['time']}\n

Please visit the hospital at the given time.
"""

        else:
            answer = "Sorry, no doctor available in that department right now."

    else:

        # Hospital context for AI
        context = f"""
You are a hospital assistant chatbot.

Hospital timings: 8 AM to 8 PM
Emergency number: +91 9876543210

Doctors available:
{doctors.to_string(index=False)}
"""

        prompt = context + "\nUser: " + user_input

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()
        answer = data.get("response", "Sorry, I couldn't generate a response.")

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.write(answer)