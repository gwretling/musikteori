import streamlit as st
import openai
from elevenlabs import generate, set_api_key
from midiutil import MIDIFile
import pygame
import io

# API-nycklar
openai.api_key = "DIN_OPENAI_API"
set_api_key("DIN_ELEVENLABS_API")

st.title("🎵 GPT med Ljudbaserade Musikteoriexempel")

fråga = st.text_input("Vad vill du höra eller veta om musikteori?")

# Hjälpfunktion för ackord och skalor
def skapa_midi(noter, längd=1):
    midi = MIDIFile(1)
    spår = 0
    tid = 0
    kanal = 0
    volym = 100
    midi.addTempo(spår, tid, 120)

    for nothöjd in noter:
        midi.addNote(spår, kanal, nothöjd, tid, längd, volym)
        tid += längd

    # Spara i minnet (bytesIO)
    midi_data = io.BytesIO()
    midi.writeFile(midi_data)
    midi_data.seek(0)
    return midi_data

# Enkel mappning (notnamn → MIDI-nummer)
noter_dict = {'C':60, 'C#':61, 'Db':61, 'D':62, 'D#':63, 'Eb':63, 'E':64, 
              'F':65, 'F#':66, 'Gb':66, 'G':67, 'G#':68, 'Ab':68, 'A':69, 
              'A#':70, 'Bb':70, 'B':71}

# Funktion för skalor/ackord
def skapa_notlista(typ, grundton):
    grundton = grundton.capitalize()
    start_not = noter_dict.get(grundton, 60)  # Standard C om inte hittad

    if typ == "dur":
        intervaller = [0,2,4,5,7,9,11,12]
    elif typ == "moll":
        intervaller = [0,2,3,5,7,8,10,12]
    elif typ == "dominant7":
        intervaller = [0,4,7,10]
    else:  # durackord
        intervaller = [0,4,7]

    return [start_not + intervall for intervall in intervaller]

if st.button("Fråga"):
    if fråga:
        # GPT-svar
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Identifiera tydligt om frågan handlar om att höra en skala eller ett ackord, och ange typ och grundton. Ge ett pedagogiskt svar."},
                {"role": "user", "content": fråga}
            ],
            max_tokens=150
        )

        svar = response.choices[0].message.content
        st.write("**GPT Svar:**", svar)

        # Tolka GPT-svaret (för ljudgenerering)
        if "skala" in svar.lower():
            if "dur" in svar.lower():
                typ = "dur"
            elif "moll" in svar.lower():
                typ = "moll"
            else:
                typ = "dur"
        elif "dominantseptimackord" in svar.lower() or "g7" in fråga.lower():
            typ = "dominant7"
        else:
            typ = "durackord"

        # Hitta grundton från frågan
        ord_i_fråga = fråga.split()
        grundton = next((ord.capitalize() for ord in ord_i_fråga if ord.capitalize() in noter_dict), 'C')

        noter = skapa_notlista(typ, grundton)
        midi_data = skapa_midi(noter)

        # Spela MIDI-fil med pygame
        pygame.init()
        pygame.mixer.init()

        with open("temp.mid", "wb") as f:
            f.write(midi_data.getbuffer())

        pygame.mixer.music.load("temp.mid")
        pygame.mixer.music.play()

        st.write(f"🎹 Spelar upp ett exempel på {grundton} {typ}")

        # Vänta tills uppspelningen är klar
        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

        pygame.mixer.music.stop()
        pygame.quit()

        # Skapa ElevenLabs-ljud av GPT-svar
        ljud = generate(
            text=svar,
            voice="DIN_RÖSTKLON",
            model="eleven_multilingual_v2"
        )

        st.audio(ljud, format="audio/mp3", autoplay=True)
