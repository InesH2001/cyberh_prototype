import streamlit as st
from transformers import pipeline
from datetime import datetime

model = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-offensive",
    tokenizer="cardiffnlp/twitter-roberta-base-offensive",
    device=-1,
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
BORDER_COLOR = "#B0BEC5"  

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
    .comment {{
        border: 1px solid {PRIMARY_COLOR};
        padding: 10px;
        border-radius: 10px;
        background-color: {WHITE_COLOR};
        margin-bottom: 10px;
        font-size: 16px;
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
    .comment-box {{
        display: flex;
        align-items: center;
    }}
    .message-box {{
        display: flex;
        align-items: center;
        margin-bottom: 10px;
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

tab1, tab2 = st.tabs(["📝 Posts", "💬 Messages"])

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
    new_comment = st.text_input("Ajoutez votre commentaire ici 👇")
    if st.button("Publier le commentaire"):
        if new_comment:
            prediction = model(new_comment)[0]
            label = prediction["label"]
            score = prediction["score"]

            if label == "offensive" and score > 0.6:
                st.session_state["show_alert"] = True
                st.session_state["alert_message"] = "🚨 Ce commentaire est offensant. Veuillez modifier votre contenu avant de le poster."
            else:
                st.success("Commentaire publié avec succès !")
                st.markdown(
                    f"""
                    <div class="comment-box">
                        <div class="user-avatar">U</div>
                        <div>
                            <p><strong>Vous :</strong> {new_comment}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Veuillez écrire un commentaire avant de publier.")

    if st.session_state.get("show_alert", False):
        st.markdown(
            f"""
            <div style='border: 1px solid {BORDER_COLOR}; padding: 15px; border-radius: 10px; background-color: {WHITE_COLOR};'>
                <p style='font-weight: bold; color: red;'>{st.session_state["alert_message"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["show_alert"] = False

# ---------------------- SECTION MESSAGES ----------------------
with tab2:
    st.markdown("<div class='title'>Messagerie</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Envoyez des messages analysés en direct</div>", unsafe_allow_html=True)

    messages = st.session_state.get("messages", [])

    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_input("Votre message :")
        submitted = st.form_submit_button("Envoyer")

        if submitted and user_message:
            prediction = model(user_message)[0]
            label = prediction["label"]
            score = prediction["score"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if label == "offensive" and score > 0.6:
                messages.append(
                    ("red", f"🚨 Message offensant détecté : {user_message}", timestamp)
                )
            else:
                messages.append(("blue", f"Vous : {user_message}", timestamp))

            st.session_state["messages"] = messages

    for color, msg, timestamp in messages:
        st.markdown(
            f"""
            <div class="message-box">
                <div class="user-avatar">U</div>
                <div>
                    <p style="color:{color};">{msg}</p>
                    <p class="timestamp">{timestamp}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
