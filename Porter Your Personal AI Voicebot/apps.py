import streamlit as st
import time
from audio_recorder_streamlit import audio_recorder
from voicebot import initialize_chat, text_to_speech, transcribe_audio

# Title of the Streamlit app
st.title("Porter - Your Personal Voice AI Assistant")

# Initialize session state variables if they are not already
if "messages" not in st.session_state:
    st.session_state.messages = []

if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

# Sidebar Settings
with st.sidebar:
    logo_path = "/mnt/e/Virtual Agent/Streamlit/montashi_logo.png"
    st.image(logo_path, caption="AI Enterprise", use_column_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Inference Settings")
    st.session_state.model = st.selectbox("Model", ["llama3.1", "llama3.2:latest"], index=0)
    st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05)
    st.session_state.max_tokens = st.slider("Max Tokens", 100, 5000, 500, 100)

# Initialize the chat chain
if "chain" not in st.session_state:
    st.session_state.chain = initialize_chat()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.markdown(message.get("response_time", ""))

# Voice input
footer_container = st.container()
with footer_container:
    st.session_state.audio_bytes = audio_recorder(text="Record a question", icon_size="lg")

if st.session_state.audio_bytes:
    transcript = transcribe_audio(st.session_state.audio_bytes)
    if transcript:
        st.session_state.messages.append({"role": "user", "content": transcript})
        
        # Display user voice input in the chat
        with st.chat_message("user"):
            st.markdown(transcript)

        # Query your custom chain
        with st.chat_message("assistant"):
            start_time = time.time()
            with st.spinner("Porter is thinking..."):
                response = st.session_state.chain.run(transcript)
            end_time = time.time()

            # Calculate response time
            response_time_str = f"Response time: {end_time - start_time:.2f} seconds"

            # Display and play assistant response via TTS
            st.markdown(response)
            text_to_speech(response)
            st.markdown(f"_{response_time_str}_")

        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response, "response_time": response_time_str})
