import os
import streamlit as st
import subprocess
from langchain.memory.buffer import ConversationBufferMemory
from langchain.memory.chat_message_histories.file import FileChatMessageHistory
from langchain_community.chat_models.ollama import ChatOllama
from langchain.chains.llm import LLMChain
from transformers import pipeline
import torch

def initialize_chat():
    """Initialize the chat model, prompt, memory, and chain."""
    
    def get_llm():
        return ChatOllama(
            model=st.session_state.model,
            temperature=st.session_state.temperature,
            max_tokens=st.session_state.max_tokens,
        )

    from langchain.prompts import (
        HumanMessagePromptTemplate,
        ChatPromptTemplate,
        MessagesPlaceholder,
        SystemMessagePromptTemplate,
    )

    def get_chat_prompt_template():
        return ChatPromptTemplate(
            input_variables=["content", "messages"],
            messages=[
                SystemMessagePromptTemplate.from_template(
                    """
                    You're a Personal Assistant, and your name is Porter.
                    Give short answers (max 50 words) and concise, but always provide a full sentence.
                    """
                ),
                MessagesPlaceholder(variable_name="messages"),
                HumanMessagePromptTemplate.from_template("{content}"),
            ],
        )

    def get_memory():
        return ConversationBufferMemory(
            memory_key="messages",
            chat_memory=FileChatMessageHistory(file_path="memory.json"),
            return_messages=True,
            input_key="content",
        )

    def create_chain(llm, prompt):
        return LLMChain(llm=llm, prompt=prompt, memory=get_memory())

    llm = get_llm()
    prompt = get_chat_prompt_template()
    chain = create_chain(llm, prompt)
    return chain

def text_to_speech(text):
    """Convert text to speech and play the audio."""
    with open(os.devnull, 'w') as devnull:
        subprocess.call(f'echo "{text}" | piper --model en_US-amy-medium --output_file output.wav', shell=True, stdout=devnull, stderr=subprocess.STDOUT)
    os.system("aplay output.wav")

# Initialize the speech-to-text pipeline
pipe = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", torch_dtype=torch.float16, device="cuda:0")

def speech_to_text(audio_data):
    """Convert audio data to text using a speech recognition model."""
    result = pipe(audio_data)
    transcript = result['text'].strip()
    return transcript

def transcribe_audio(audio_bytes):
    """Save and transcribe audio bytes."""
    webm_file_path = "temp_audio.mp3"
    with open(webm_file_path, "wb") as f:
        f.write(audio_bytes)
    
    transcript = speech_to_text(webm_file_path)
    os.remove(webm_file_path)
    return transcript
