import uuid
import time
import logging
import vertexai
import datetime as dt
import streamlit as st
from typing import Dict, Union
from google.cloud import aiplatform
from streamlit_feedback import streamlit_feedback
from langchain.callbacks.base import BaseCallbackHandler

from lib.logo import add_logo
from lib.chain import get_chain
from lib.streaming import StreamHandler
from lib.send_feedback import send_to_pubsub
from lib.source_retriever import list_top_k_sources, get_top_k_urls

from config import (
    PROJECT_ID,
    REGION,
    CONFLUENCE_SPACE_NAMES,
    STREAMING_MODE
)

USER_ID = uuid.uuid4()

vertexai.init(project=PROJECT_ID, location=REGION)

logging.basicConfig(level=logging.INFO)
aiplatform.init(
    project=PROJECT_ID,
    location=REGION
)

octo_logo = add_logo(logo_path="./chatbot/images/logo.png", width=250, height=120)
octo_avatar = add_logo(logo_path="./chatbot/images/avatar.png", width=50, height=50)
st.set_page_config(page_title="Chatbot - Octo", layout="centered", page_icon=octo_avatar)


def _submit_feedback(user_response, *args):
    n_it = args[0]
    question = st.session_state['messages'][2 * n_it - 1]['content']
    response = st.session_state['messages'][2 * n_it]['content']
    thumbs = user_response['score']
    rating = rating = {
        "👍": 1,
        "👎": 0
    }[thumbs]
    feedback_time = dt.dt.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback = user_response['text']
    runtime = st.session_state.runtime[n_it]
    sources = st.session_state.sources[n_it]
    feedback = user_response['text'] or ""
    feedback_dict = {
        "id": str(USER_ID),
        "dt": str(feedback_time),
        "rating": int(rating),
        "feedback": str(feedback),
        "question": str(question),
        "response": str(response),
        "runtime": float(runtime),
        "sources": str(sources)
    }

    send_to_pubsub(feedback_dict)
    st.toast(f"Feedback submitted: {user_response['score']}")


def set_default_button_dict():
    buttons = {
        "docs_start_date": dt.date(2020, 1, 1),
        "docs_end_date": dt.date.today()
    }
    for space_name in CONFLUENCE_SPACE_NAMES:
        buttons[space_name] = True
    return buttons


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How may I help you?"}]

if "runtime" not in st.session_state:
    st.session_state["runtime"] = [0.0]

if "sources" not in st.session_state:
    st.session_state["sources"] = [[]]

if "sources_md" not in st.session_state:
    st.session_state["sources_md"] = [""]

if "buttons" not in st.session_state:
    st.session_state["buttons"] = set_default_button_dict()

if "feedback_key" not in st.session_state:
    st.session_state["feedback_key"] = None

if "streaming_mode" not in st.session_state:
    st.session_state["streaming_mode"] = STREAMING_MODE

st.title("Octo Assistant")
st.session_state["streaming_mode"] = st.checkbox('Stream the answer', value=STREAMING_MODE)
st.text("I already read Octo's documentation, so you don't have to 🙂")


# Initalize model
@st.cache_resource(show_spinner=False)
def cached_get_chain(
    filters: Dict[str, Union[bool, dt.date]] = st.session_state["buttons"],
    streaming: bool = False,
    streaming_handler: BaseCallbackHandler = None
):
    logging.info(f"Re initializing QA agent with filters: {filters}")
    qa_agent = get_chain(filters=filters, streaming=streaming, streaming_handler=streaming_handler)
    return qa_agent


if not st.session_state["streaming_mode"]:
    st.session_state["qa_agent"] = cached_get_chain(filters=st.session_state["buttons"])


# Create sidebar
with st.sidebar:
    st.image(octo_logo)
    st.caption('Select the documents you want to search in:')

    button_dict = {}
    for space_name in CONFLUENCE_SPACE_NAMES:
        st.session_state["buttons"][space_name] = st.checkbox(space_name, value=True)

    st.caption('Search in a specific time range:')
    st.session_state["buttons"]["docs_start_date"] = st.date_input("Start date", dt.date(2020, 1, 1))
    st.session_state["buttons"]["docs_end_date"] = st.date_input("End date", dt.date.today())

    if st.button("Update", type="primary"):
        with st.spinner('Loading') and not st.session_state["streaming_mode"]:
            st.session_state["qa_agent"] = cached_get_chain(filters=st.session_state["buttons"])


# Display the whole conversation in the UI
for n, message in enumerate(st.session_state.messages):
    if message["role"] == "assistant":

        with st.chat_message(message["role"], avatar="./chatbot/images/avatar.png"):
            st.markdown(message["content"])
            feedback_key = f"feedback_{n // 2}"

            # If the feedback was not provied in some question/answer, let the opporunity for the user to provide it
            # Disable with score to None ask for feedback
            if feedback_key not in st.session_state:
                st.session_state[feedback_key] = None

            if n != 0:  # Do not display feedback for first assistant message that is a question
                score = st.session_state[feedback_key].get('score') if st.session_state[feedback_key] else None
                streamlit_feedback(
                    feedback_type="thumbs",
                    on_submit=_submit_feedback,
                    key=feedback_key,
                    args=[n // 2],
                    disable_with_score=score,
                    optional_text_label="Please provide textual feedback"
                )
                if st.session_state.sources_md[n // 2]:
                    st.markdown(st.session_state.sources_md[n // 2])

    else:
        with st.chat_message(message["role"], avatar="🧑‍💻"):
            st.markdown(message["content"])


if prompt := st.chat_input("How may I help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🧑‍💻").write(prompt)

    with st.chat_message("assistant", avatar="./chatbot/images/avatar.png"):
        with st.spinner(text='I am thinking...'):
            time_st = time.time()

            if st.session_state["streaming_mode"]:
                # Chain must be instanciated here because of st.empty behavior
                container = st.empty()
                handler = StreamHandler(container)
                chain = get_chain(filters=st.session_state["buttons"], streaming=True, streaming_handler=[handler])
                result = chain({"query": prompt})
                answer = result["result"]
            else:
                result = st.session_state["qa_agent"]({"query": prompt})
                answer = result["result"]
                st.write(answer)

        time_end = time.time()
        sources = get_top_k_urls(result)
        sources_md = list_top_k_sources(result)

        # Save metadata
        st.session_state.runtime.append(float(round(time_end - time_st, 3)))
        st.session_state.sources.append(sources)
        st.session_state.sources_md.append(sources_md)

        # Write answer and sources
        if sources_md:
            st.markdown(sources_md)
        else:
            print(sources_md)

        st.session_state.messages.append({"role": "assistant", "content": f"{answer}"})

    # Ask for feedback
    feedback_key: str = f"feedback_{len(st.session_state.messages) // 2}"
    streamlit_feedback(
        feedback_type="thumbs",
        on_submit=_submit_feedback,
        key=feedback_key,
        optional_text_label="Please provide textual feedback",
        args=[len(st.session_state.messages) // 2]
    )
