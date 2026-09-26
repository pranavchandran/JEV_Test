import streamlit as st

st.title("NEEPS")

user_input = st.text_input("Enter your message")

if user_input:
    if user_input.strip().lower() == "hello":
        st.write("Hai welcome to NEEPS")
    else:
        st.write(f"You said: {user_input}")
