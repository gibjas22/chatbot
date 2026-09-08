import streamlit as st
from openai import OpenAI, OpenAIError

from chat_errors import safe_error_text

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API. If the call fails, the prompt
        # above is removed again so a failed turn does not linger in the history
        # and get resent with every later message.
        try:
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # Stream the response to the chat using `st.write_stream`, then store it
            # in session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
        except OpenAIError as error:
            st.session_state.messages.pop()
            st.error(
                "That request to OpenAI failed, so your message was not sent. "
                "Check that the API key is valid and still has credit, then try "
                f"again.\n\nDetails: {safe_error_text(error)}",
                icon="🚫",
            )
        else:
            # An empty response would leave a blank turn in the history, which the
            # API then rejects on the next request.
            if response:
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            else:
                st.session_state.messages.pop()
                st.warning(
                    "OpenAI returned an empty response, so nothing was added to "
                    "the conversation. Try sending the message again.",
                    icon="⚠️",
                )
