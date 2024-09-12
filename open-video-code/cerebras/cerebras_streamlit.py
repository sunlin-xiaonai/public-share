import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()


def chat_completion(api_key, message, model="llama3.1-70b", max_tokens=4096, temperature=0.2, top_p=1):
    url = "https://api.cerebras.ai/v1/chat/completions"
    api_key = api_key if api_key  else os.getenv("CEREBRAS_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Please try to provide useful, helpful and actionable answers. use chinese to answer"},
            {"role": "user", "content": message}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": True
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    if response.status_code == 200:
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    json_line = json.loads(line.decode('utf-8').split('data: ')[1])
                    content = json_line['choices'][0]['delta'].get('content', '')
                    if content:
                        full_response += content
                        yield content
                except Exception as e:
                    pass
    else:
        yield f"Error: {response.status_code} - {response.text}"

st.title("Cerebras AI Chat")

api_key = st.sidebar.text_input("Enter your API key", type="password")
model = st.sidebar.selectbox("Select model", ["llama3.1-70b", "llama3.1-8b"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2)
max_tokens = st.sidebar.number_input("Max tokens", 1, 4096, 4096)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in chat_completion(api_key, prompt, model, max_tokens, temperature):
            full_response += response
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})