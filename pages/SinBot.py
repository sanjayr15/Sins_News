import streamlit as st
from db import get_specific_data   # adjust if needed
from sins_ai import get_chat_response  # adjust import if needed
from db import get_ai_data


try:

    # -----------------------------
    # PAGE CONFIG
    # -----------------------------
    st.set_page_config(page_title="SIN Master", page_icon="🤖", layout="wide")

    st.title("🤖 SIN Master")
    st.caption("Ask anything about today's news")


    # -----------------------------
    # SESSION STATE INIT
    # -----------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # if "all_news_df" not in st.session_state:
    #     st.warning("News data not loaded. Please go back to News page.")
    #     st.stop()

    if "chat_article_id" not in st.session_state:
        st.session_state.chat_article_id = None


    #all_news_df = st.session_state.all_news_df
    selected_article_id = st.session_state.chat_article_id


    # -----------------------------
    # BACK BUTTON
    # -----------------------------
    col1, col2 = st.columns([1, 6])

    with col1:
        if st.button("⬅ Back"):
            st.switch_page("Home.py")


    st.divider()


    # -----------------------------
    # DISPLAY CHAT HISTORY
    # -----------------------------


    # -----------------------------
    # CHAT INPUT
    # -----------------------------
    user_input = st.chat_input(
        "Ask something...",
        key="chat_input_global"
    )

    all_news_df = get_ai_data()
    # -----------------------------
    # HANDLE USER INPUT
    # -----------------------------
    if user_input:

        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        # with st.chat_message("user"):
        #     st.markdown(user_input)
            
        #context_df = all_news_df

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
            # Generate response

                response = get_chat_response(
                    user_question=user_input,
                    context_df=all_news_df,
                    selected_id=selected_article_id,
                    chat_history=st.session_state.messages
                )

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

            #st.markdown(response)


    chat_container = st.container(height=250)

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

   
except:
    st.warning("Uh-Oh !, You should not see this, please return to home page.")
     
