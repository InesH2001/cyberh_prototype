import streamlit as st
from transformers import pipeline
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
import json
import os

model = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

st.set_page_config(
    page_title="Détection du Cyberharcèlement",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY_COLOR = "#1E3A8A"
SECONDARY_COLOR = "#D1D5DB"
WHITE_COLOR = "#FFFFFF"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {SECONDARY_COLOR};
        color: {PRIMARY_COLOR};
    }}
    .title {{
        font-size: 24px;
        font-weight: bold;
        color: {PRIMARY_COLOR};
    }}
    .subtitle {{
        font-size: 18px;
        font-weight: bold;
    }}
    .comment-box, .message-box {{
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }}
    .user-avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: {PRIMARY_COLOR};
        color: {WHITE_COLOR};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        margin-right: 10px;
    }}
    .timestamp {{
        font-size: 12px;
        color: #607D8B;
        margin-left: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

def load_data(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            return json.load(file)
    return []

def save_data(file_name, data):
    with open(file_name, "w") as file:
        json.dump(data, file)

COMMENTS_FILE = "comments.json"
MESSAGES_FILE = "messages.json"

comments_data = load_data(COMMENTS_FILE)
messages_data = load_data(MESSAGES_FILE)

tab1, tab2 = st.tabs(["🗿 Posts", "💬 Messages"])

# ---------------------- SECTION POSTS ----------------------
with tab1:
    st.markdown("<div class='title'>Posts</div>", unsafe_allow_html=True)

    st.markdown("<div class='subtitle'>Post existant</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="comment-box">
            <div class="user-avatar">A</div>
            <div>
                <p><strong>Alice :</strong> Hey everyone! 📝</p>
                <p>How are you doing?</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='subtitle'>Commentaires</div>", unsafe_allow_html=True)
    for comment in comments_data:
        st.markdown(
            f"""
            <div class="comment-box">
                <div class="user-avatar">U</div>
                <div>
                    <p><strong>Vous :</strong> {comment['content']}</p>
                    <p class="timestamp">{comment['timestamp']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    new_comment = st.text_input("Ajoutez votre commentaire ici 👇")
    if st.button("Publier le commentaire"):
        if new_comment:
            prediction = model(new_comment, ["offensive"])
            score = prediction["scores"][0]

            if score > 0.3:
                st.error(f"Ce commentaire est offensant : {new_comment}")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_entry = {"content": new_comment, "timestamp": timestamp}
                comments_data.append(new_entry)
                save_data(COMMENTS_FILE, comments_data)
                st.markdown(
                    f"""
                    <div class="comment-box">
                        <div class="user-avatar">U</div>
                        <div>
                            <p><strong>Vous :</strong> {new_comment}</p>
                            <p class="timestamp">{timestamp}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.success("Commentaire publié avec succès !")

# ---------------------- SECTION MESSAGES ----------------------
with tab2:
    st.markdown("<div class='title'>Messagerie</div>", unsafe_allow_html=True)

    for message in messages_data:
        st.markdown(
            f"""
            <div class="message-box">
                <div class="user-avatar">U</div>
                <div>
                    <p>{message['content']}</p>
                    <p class="timestamp">{message['timestamp']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='subtitle'>Envoyez un message vocal :</div>", unsafe_allow_html=True)
    audio_file = st.file_uploader("Enregistrez un message vocal (formats supportés : WAV, MP3, FLAC, M4A)", type=["wav", "mp3", "flac", "m4a"])

    if st.button("Analyser le vocal"):
        if audio_file:
            recognizer = sr.Recognizer()
            try:
                with open("temp_audio", "wb") as f:
                    f.write(audio_file.read())

                audio_path = "temp_audio"
                if audio_file.name.endswith(".m4a"):
                    sound = AudioSegment.from_file(audio_path, format="m4a")
                    sound.export("temp_audio_converted.wav", format="wav")
                    audio_path = "temp_audio_converted.wav"

                with sr.AudioFile(audio_path) as source:
                    audio_data = recognizer.record(source)
                    transcript = recognizer.recognize_google(audio_data)

                    prediction = model(transcript, ["offensive"])
                    score = prediction["scores"][0]

                    if score > 0.3:
                        st.error(f"Message vocal offensant détecté : {transcript}")
                    else:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        new_entry = {"content": transcript, "timestamp": timestamp}
                        messages_data.append(new_entry)
                        save_data(MESSAGES_FILE, messages_data)
                        st.markdown(
                            f"""
                            <div class="message-box">
                                <div class="user-avatar">U</div>
                                <div>
                                    <p>{transcript}</p>
                                    <p class="timestamp">{timestamp}</p>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.success("Message vocal accepté.")

            except Exception as e:
                st.error(f"Erreur lors de la reconnaissance vocale : {e}")

    user_message = st.text_input("Votre message :")
    if st.button("Envoyer le message"):
        if user_message:
            prediction = model(user_message, ["offensive"])
            score = prediction["scores"][0]

            if score > 0.3:
                st.error(f"Message offensant détecté : {user_message}")
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_entry = {"content": user_message, "timestamp": timestamp}
                messages_data.append(new_entry)
                save_data(MESSAGES_FILE, messages_data)
                st.markdown(
                    f"""
                    <div class="message-box">
                        <div class="user-avatar">U</div>
                        <div>
                            <p>{user_message}</p>
                            <p class="timestamp">{timestamp}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.success("Message envoyé avec succès !")
