import streamlit as st
from openai import OpenAI

# Streamlit page configuration
st.set_page_config(page_title="Mars Chat", page_icon="🪐")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "client" not in st.session_state:
    st.session_state.client = None

# Title
st.title("Mars Information Chat")

# Load API key from secrets and initialize client
try:
    api_key = st.secrets["SUTRA_API_KEY"]
    if not st.session_state.client:
        with st.spinner("Initializing API connection..."):
            st.session_state.client = OpenAI(
                base_url='https://api.two.ai/v2',
                api_key=api_key
            )
            st.success("API connection established!")
except KeyError:
    st.error("SUTRA_API_KEY not found in secrets. Please configure it in Streamlit Community Cloud settings.")
    st.stop()
except Exception as e:
    st.error(f"Error initializing API connection: {str(e)}")
    st.stop()

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

# Instructions in sidebar
st.sidebar.markdown("""
### About
This app uses the Sutra API to provide information about Mars.
The API key is managed through Streamlit Community Cloud's secret management.
""")