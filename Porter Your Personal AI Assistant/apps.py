import streamlit as st
import time  # For measuring response time
from chatbot import initialize_chat  # Import chatbot logic

# Streamlit UI for chat
st.title("Porter - Your Personal AI Assistant")

# Initialize session state for storing messages and settings
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    st.session_state.model = "llama3.1"  # Default model

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.0  # Default temperature

if "max_tokens" not in st.session_state:
    st.session_state.max_tokens = 500  # Default token limit

# Sidebar for uploading documents and adjusting settings
with st.sidebar:
    # Add logo at the top of the sidebar
    logo_path = "/mnt/e/Virtual Agent/Streamlit/montashi_logo.png"
    st.image(logo_path, caption="AI Enterprise", use_column_width=True)

    # Spacer to move upload section to the middle
    st.markdown("<br>", unsafe_allow_html=True)  # Add some vertical space

    st.subheader("Inference Settings")
    
    # User selects the model, temperature, and token settings
    st.session_state.model = st.selectbox("Model", ["llama3.1", "llama3.2:latest"], index=0)
    st.session_state.temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.05)
    st.session_state.max_tokens = st.slider("Max Tokens", min_value=100, max_value=5000, value=500, step=100)

# Load the chain when the app starts, only once
if "chain" not in st.session_state:
    st.session_state.chain = initialize_chat()

# Display previous messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.markdown(message.get("response_time", "")) 

# Run the Streamlit app
if __name__ == "__main__":
    # Chat input
    if prompt := st.chat_input("Ask Porter a question"):
        # Append the user question to the session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user input in the chat
        with st.chat_message("user"):
            st.markdown(prompt)

        # Query your custom chain using LangChain agent
        with st.chat_message("assistant"):
            start_time = time.time()  # Record start time
            with st.spinner("Porter is thinking..."):
                response = st.session_state.chain.run(prompt)
            end_time = time.time()  # Record end time

            # Calculate total response time
            response_time = end_time - start_time
            response_time_str = f"Response time: {response_time:.2f} seconds"

            # Display response and response time
            st.markdown(response)
            st.markdown(f"_{response_time_str}_")  # Italicize the response time for style

        # Save the assistant response and response time separately in session state
        st.session_state.messages.append({"role": "assistant", "content": response, "response_time": response_time_str})
