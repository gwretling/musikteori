import streamlit as st
from elevenlabs import generate, play, set_api_key
import openai

# Sätt API-nycklar
set_api_key(st.secrets["elevenlabs_api_key"])
openai.api_key = st.secrets["openai_api_key"]

st.title("🧠 AI Röst- och Textgenerator")

# Textinput
user_text = st.text_input("Skriv något du vill att en AI ska säga:")

# När användaren klickar
if st.button("Generera tal"):
    if user_text:
        # Elevenlabs genererar röst
        audio = generate(text=user_text, voice="Rachel", model="eleven_monolingual_v1")
        play(audio)
        st.success("Spelar upp texten med AI-röst!")
    else:
        st.warning("Skriv något först!")
