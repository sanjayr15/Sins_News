import streamlit as st
import psycopg2
import pandas as pd
from db import get_ai_data, add_like, get_like_count, add_comment, get_comments
from sins_ai import get_chat_response
from main import main

try:

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    if "chat_article_id" not in st.session_state:
        st.session_state.chat_article_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "likes" not in st.session_state:
        st.session_state.likes = {}

    if "comments" not in st.session_state:
        st.session_state.comments = {}


    st.set_page_config(
        page_title="SINS",
        page_icon="📰",
        layout="wide"
    )

    #st.title("🧠 AI Powered News Intelligence")
    #st.title("SINS - SimplIfied NewS")
    st.markdown("""
    <style>

    /* Keep Streamlit menu visible */
    div[data-testid="stHeader"] {
        z-index: 100;
    }

    /* Sticky custom title BELOW the menu */
    .sticky-title {
        position: fixed;
        top: 60px;   /* pushes below Streamlit top bar */
        left: 0;
        width: 100%;
        background-color: #DAE1ED;
        background: rgba(14,17,23,0.85);
        backdrop-filter: blur(10px);
        text-align: center;
        padding: 15px 0px;
        font-size: 26px;
        font-weight: bold;
        color: white;
        z-index: 999;
        border-bottom: 1px solid #333;
    }

    /* Push page content down */
    .main-content {
        margin-top: 130px;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sticky-title">SINS - SimplAIfied NewS</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-content">', unsafe_allow_html=True)





    #Get Data
    df = get_ai_data()

    if "all_news_df" not in st.session_state:
        st.session_state.all_news_df = df


    categories = st.sidebar.selectbox(
        "Filter by Category",
        ["All"] + list(df["sins_category"].dropna().unique())
    )

    search = st.sidebar.text_input("Search News")

    filtered_df = df.copy()

    if categories != "All":
        filtered_df = filtered_df[filtered_df["sins_category"] == categories]

    if search:
        filtered_df = filtered_df[
            filtered_df["source_title"].str.contains(search, case=False)
        ]

    for index, row in filtered_df.iterrows():

        with st.container():

            col1, col2 = st.columns([1, 3])

            with col1:
                if row["source_image_url"]:
                        st.image(row["source_image_url"], use_container_width=True,)

            with col2:
                st.subheader(row["source_title"])
                st.write(row["sins_summary"])

                st.markdown(f"""
                **Category:** {row['sins_category']}  
                **Sin Verdict:** {row['sins_verdict']}
                """)
                
                sin_value = int(row["sins_meter"]) if row["sins_meter"] else 0

                if sin_value == 0:
                    bar_color = "#4CAF50"   # green
                elif sin_value < 30:
                    bar_color = "#4CAF50"   # green
                elif sin_value < 70:
                    bar_color = "#FFA726"   # orange
                else:
                    bar_color = "#EF5350"   # red

                st.markdown(f"""
                <div style="background:#333; border-radius:10px;">
                    <div style="width:{max(sin_value,30)}%; 
                                background:{bar_color}; 
                                padding:6px; 
                                border-radius:10px;
                                text-align:left;
                                color:white;
                                font-size:12px;">
                        Sin Meter - {sin_value}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
                #st.progress(sin_value)
                #st.caption(f"Sin Meter: {sin_value}/100")
    
                #**Sin Meter:** {row['sins_meter']}

                st.markdown(f"[ Source : {row["source"]} - Read Full Article]({row['source_link']})")
                st.write(f"Published On : {row["fetched_at"]}")

                #st.subheader("💬 Chat with SIN Master")

                #if st.button(f"Know more about {row['source_title']}", key=f"chat_{row['id']}"):
                if st.button(f"Chat with Sinner about this article.",key=f"chat_btn_{row['id']}"):
                    st.session_state.chat_open = True
                    st.session_state.chat_article_id = row["id"]
                    #st.session_state.messages = []  # reset chat for new article
                    st.switch_page("pages/SinBot.py")

                col3, col4 = st.columns([1],gap='xxsmall')
                with col3:
                    like_count = get_like_count(row["id"])

                    if st.button(f"👍 Like ({like_count})", key=f"like_{row["id"]}"):
                        add_like(row["id"])
                        st.rerun()

                    comments = get_comments(row["id"])
                    comment_count = len(comments)
                
                with col4:
                    with st.expander(f"💬 Comments ({comment_count})"):

                        # Add comment box
                        comment_text = st.text_input(
                            "Write a comment",
                            key=f"comment_input_{row["id"]}"
                        )

                        if st.button("Post", key=f"post_comment_{row["id"]}"):
                            if comment_text.strip():
                                add_comment(row["id"], comment_text)
                                st.rerun()

                        # Display existing comments
                        if comments:
                            for comment, created_at in comments:
                                st.markdown(
                                    f"**{created_at.strftime('%Y-%m-%d %H:%M')}**  \n{comment}"
                                )
                        else:
                            st.info("No comments yet.")

            st.divider()


    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    print(e)
    st.warning("Uh-Oh !, You should not see this, please return to home page.")
