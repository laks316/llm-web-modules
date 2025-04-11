import streamlit as st
from openai import OpenAI
import time

# Streamlit page configuration
st.set_page_config(page_title="Mars Chat", page_icon="🪐")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_validated" not in st.session_state:
    st.session_state.api_validated = False
if "client" not in st.session_state:
    st.session_state.client = None

# Title
st.title("Mars Information Chat")

# API Key input and validation in sidebar
with st.sidebar:
    api_key = st.text_input("Enter your SUTRA API Key", type="password", key="api_key_input")
    
    if api_key and not st.session_state.api_validated:
        with st.spinner("Validating API key..."):
            try:
                # Initialize client
                client = OpenAI(base_url='https://api.two.ai/v2', api_key=api_key)
                
                # Test API call with a simple request
                test_stream = client.chat.completions.create(
                    model='sutra-v2',
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                    stream=True
                )
                
                # Check if we get any response
                for chunk in test_stream:
                    if len(chunk.choices) > 0:
                        st.session_state.api_validated = True
                        st.session_state.client = client
                        st.success("API key validated successfully!")
                        break
                else:
                    st.error("API key validation failed. Please check your key.")
                    
            except Exception as e:
                st.error(f"Error validating API key: {str(e)}")
                st.session_state.api_validated = False

    elif st.session_state.api_validated:
        st.success("API key validated!")

# Chat interface (only if API key is validated)
if st.session_state.api_validated and st.session_state.client:
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about Mars..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from API with streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Create streaming response
                stream = st.session_state.client.chat.completions.create(
                    model='sutra-v2',
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                    temperature=0,
                    stream=True
                )

                # Process stream chunks
                for chunk in stream:
                    if len(chunk.choices) > 0:
                        content = chunk.choices[0].delta.content
                        finish_reason = chunk.choices[0].finish_reason
                        if content and finish_reason is None:
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")

                # Display final message without cursor
                message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                message_placeholder.error(f"Error getting response: {str(e)}")

else:
    if not api_key:
        st.info("Please enter your API key in the sidebar to start chatting about Mars!")
    elif not st.session_state.api_validated:
        st.warning("Waiting for API key validation...")

# Instructions to run
st.sidebar.markdown("""
### How to Run
1. Save this file as `app.py`
2. Install requirements: `pip install streamlit openai`
3. Run: `streamlit run app.py`
""")