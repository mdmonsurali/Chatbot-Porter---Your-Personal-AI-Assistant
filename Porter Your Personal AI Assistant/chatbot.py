import streamlit as st  # Import Streamlit here
import json
from pathlib import Path
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain.schema import messages_from_dict, messages_to_dict  # Import these!
from langchain.memory.buffer import ConversationBufferMemory
from langchain.memory.chat_message_histories.file import FileChatMessageHistory
from langchain_community.chat_models.ollama import ChatOllama
from langchain.chains.llm import LLMChain

def initialize_chat():
    
    def get_llm():
        llm = ChatOllama(
            model=st.session_state.model,  # Use model selected in the sidebar
            temperature=st.session_state.temperature,  # Use temperature selected
            max_tokens=st.session_state.max_tokens,  # Use max tokens selected
        )
        return llm

    from langchain.prompts import (
        HumanMessagePromptTemplate,
        ChatPromptTemplate,
        MessagesPlaceholder,
        SystemMessagePromptTemplate,
    )

    def get_chat_prompt_template():
        """Generate and return the prompt
        template that will answer the users query
        """
        return ChatPromptTemplate(
            input_variables=["content", "messages"],
            messages=[
                SystemMessagePromptTemplate.from_template(
                    """
                        You're a Personal Assistant, and your name is Porter.
                        
                        Give a short answer when you have a question. Answers will be max 50 words and concise, but you will always provide a full sentence.
                        try to answer the questions to the best of your knowledge
                    """
                ),
                MessagesPlaceholder(variable_name="messages"),
                HumanMessagePromptTemplate.from_template("{content}"),
            ],
        )

    class SafeFileChatMessageHistory(FileChatMessageHistory):
        @property
        def messages(self):
            
            file_path = Path(self.file_path)
            
            # Check if the file exists or is empty
            if not file_path.exists() or file_path.stat().st_size == 0:
                # Create an empty list and write to the file
                file_path.write_text('[]', encoding=self.encoding)
                return []
            
            # Try to load messages from the file
            try:
                items = json.loads(file_path.read_text(encoding=self.encoding))
                messages = messages_from_dict(items)  # Use messages_from_dict here
                return messages
            except json.JSONDecodeError:
                # In case of a JSON decode error, reset to an empty list
                return []

        def add_message(self, message):
            
            messages = messages_to_dict(self.messages)  # Convert to dict
            messages.append(messages_to_dict([message])[0])
            self.file_path.write_text(
                json.dumps(messages, ensure_ascii=self.ensure_ascii), encoding=self.encoding
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
