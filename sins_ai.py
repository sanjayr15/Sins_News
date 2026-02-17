from openai import OpenAI
import os
from dotenv import load_dotenv
import json
#from db import get_specific_data
import pandas as pd

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary_and_category(title, content):

    prompt = f"""
    You are a news processing AI. 
    
    You are called SINS (Simplified News). You are a Sin Master for the people who actally make sins.
    You are funny and sensible.

    Analyze the following news article.

    Return ONLY valid JSON in this format:
    {{
        "Title": "A crisp title for the article."
        "summary": "3-4 sentence summary",
        "category": "One word category like Technology, Politics, Sports, Business, Entertainment, Health, World, Science",
        "veridct": "A short sarcastic verdict when needed,  Avoid sarcasm for tragedy, death, or sensitive topics."
        "sin_meter" : "You need to rate the SIN involed in this news, rate from 0 to 100, 0-No Sin Invloved, 100-A complete SIN occured, people sufferiing."
    }}

    Title: {title}

    Content: {content}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result = response.choices[0].message.content

    try:
        parsed = json.loads(result)
        return parsed["Title"], parsed["summary"], parsed["category"], parsed["veridct"], parsed["sin_meter"]
    except Exception as e:
        return None, None, None, None, None

#-------------------------------------------------------------------------------------------

from openai import OpenAI
import os

SYNONYM_MAP = {
    "murder": ["murder", "kill", "accident", "fraud", "scam", "assault", "corruption"],
    "politics": ["minister", "government", "election", "party", "policy"],
    "money": ["fraud", "scam", "corruption", "bribe", "tax"],
    "violence": ["murder", "assault", "attack", "shooting"]
}


import re

def expand_query(question):

    words = re.findall(r"\w+", question.lower())
    expanded_words = set(words)

    for word in words:
        if word in SYNONYM_MAP:
            expanded_words.update(SYNONYM_MAP[word])

    return " ".join(expanded_words)


def retrieve_relevant_articles(question, df, selected_id=None, top_k=10):

    # If focused article selected → prioritize it
    if selected_id:
        focused = df[df["id"] == selected_id]
    else:
        focused = None

    question = expand_query(question)
    # Keyword search (basic version)
    matches = df[
        df["sins_summary"].str.contains(question, case=False, na=False) |
        df["sins_title"].str.contains(question, case=False, na=False) |
        df["sins_category"].str.contains(question, case=False, na=False)
    ].head(top_k)

    if focused is not None and not focused.empty:
        matches = focused #pd.concat([focused, matches]).drop_duplicates()
    else:
        matches = df

    return matches.head(top_k)


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chat_response(user_question,context_df,selected_id,chat_history):

    relevant_articles = retrieve_relevant_articles(user_question,context_df,selected_id)

    context_text = ""
    for _, row in relevant_articles.iterrows():
        context_text += f"""
        Id:{row['id']}
        Title: {row['sins_title']}
        Summary: {row['sins_summary']}
        Category: {row['sins_category']}
        Verdict: {row['sins_verdict']}
        SinMeter: {row['sins_meter']}
        FullContent : {row['source_full_content']}
        """
    
    system_message = f"""
    You are a news processing AI. 
    
    You are called SINS (Simplified News). You are a Sin Master for the people who actally make sins.

    Rules:
    1. Answer in a friendly way, make story intresting.
    2. Do not repeat the question.
    3. Do not give generic disclaimers.
    4. Use provided news data first.
    5. If unsure, say you do not have enough information.
    6. Keep responses concise unless user asks for deep analysis.
    7. Avoid sarcasm for tragedy, death, or sensitive topics.

    NEWS DATA: {context_text}
    Chat History : {chat_history[-10:]}
    User Question: {user_question}
    """
    # Build message history for OpenAI
    # messages = [{"role": "system", "content": system_message}]
    # # Add past chat memory (limit last 6 messages to control tokens)
    # messages += chat_history[-10:]
    # # Add context injection
    # messages.append({
    #     "role": "system",
    #     "content": f"Relevant News Data:\n{context_text}"
    # })

    # # Add current question
    # messages.append({
    #     "role": "user",
    #     "content": user_question
    # })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": system_message}],
        temperature=0.3
    )

    return response.choices[0].message.content

