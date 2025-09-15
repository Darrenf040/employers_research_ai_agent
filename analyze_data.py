import streamlit as st
import time
import pandas as pd
from ollama import chat
import json

import re

def clean_markdown(text: str) -> str:
    # Fix bold/italic spacing
    text = re.sub(r"\*\s+(.*?)\s+\*", r"*\1*", text)
    text = re.sub(r"\*\*\s+(.*?)\s+\*\*", r"**\1**", text)

    # Add line breaks before headers
    text = re.sub(r"(?m)(\*\*.*?\*\*)", r"\n\n\1\n", text)

    # Ensure bullets render properly
    text = re.sub(r"(?m)^\s*[\*\-]\s*", "- ", text)

    # Collapse weird spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def df_to_json(dataframe):
    df_json = dataframe.to_json()
    df_json = json.dumps(dataframe.to_dict(orient="records"), indent=2)
    return df_json




# DATAFRAME INITIALIZATION
df = pd.read_csv("output.csv")
df = df.fillna("N/A")
df_json = df_to_json(df)


st.sidebar.title("Filter Dataset")
st.sidebar.caption("Note: Leaving all filters unselected will load the entire dataset for that column")

industry = st.sidebar.multiselect(
        "industry", 
        ['Accounting Services', 'Aerospace', 'Chemicals', 'Consulting', 'Construction & Building Trades', 
        'Educational Instruction and Administration', 'Engineering', 'Energy & Environmental Resources', 'Finance', 'Healthcare/Medical Equipment', 
        'Information Technology', 'Insurance', 'Legal/Law', 'Manufacturing, Machinery & Equipment', 'Pharmaceuticals/Biotechnology', 'Other'
        ]
    )

selected_majors_list = st.sidebar.multiselect(
        "Major",
        ["Computer Science", "Data Science", "MS", "Math", "Statistics", "Biology", "Chemistry", "Biochemistry", "Physics"]
    )

work_authorization = st.sidebar.multiselect(
        "Work Authorization",
        ["Authorized to work in the U.S.", "Not authorized to work in the U.S."]
    )

degree = st.sidebar.multiselect(
        "Degree",
        ["Bachelors", "Masters", "Doctorate"]
    )

positions = st.sidebar.multiselect(
        "Job Positions",
        ["Internship", "Full Time", "Part Time", "Co-Op", "Graduate and Professional Schools", "Graduate Fellowship"]
    )



st.title("NSM Career Fair")
tab1, tab2, = st.tabs(["Dataframe", "Chatbot"])


with tab1:
    st.caption("Filter the career fair employers dataset and ask questions about the dataset")

    # dataset filters
    industry_pattern = "|".join(industry)
    major_pattern = "|".join(selected_majors_list)
    work_authorization_pattern = "|".join(work_authorization)
    degree_pattern = "|".join(degree)
    positions_pattern = "|".join(positions)
        

    # FILTER DATA FRAME

    df = df[df["industry"].str.contains(industry_pattern, case=False, na=False)]
    # major_pattern is your regex for selected majors
    df = df[
        df["majors"].str.contains(major_pattern, case=False, na=False) |
        (df["majors"] == "All Majors")
    ]
    df = df[df["work_authorization"].str.contains(work_authorization_pattern, case=False, na=False)]
    df = df[df["degree"].str.contains(degree_pattern, case=False, na=False)]
    df = df[df["positions"].str.contains(positions_pattern, case=False, na=False)]

    display_df = df[["company", "industry", "website", "majors", "work_authorization", "degree", "positions"]]
    df_json = df_to_json(df)

    st.dataframe(display_df, width="stretch")

with tab2: 
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


prompt = st.chat_input("Learn about the companies in the dataset")
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with tab2:  # responses still render inside tab2
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            user_message = {"role": "user", "content": prompt}
            system_message = {
                "role": "system",
                "content": f"""
            You are an assistant helping a student prepare for a career fair.
            You are given a list of companies attending the fair. Each company is a dictionary with the following keys:
            - 'company': name of the company
            - 'overview': short description of the company
            - 'industry': industry they belong to
            - 'majors': which majors they recruit
            - 'positions': positions they are hiring for

            Answer questions only using this data. If information is missing, clearly state it is not available. Do not invent details.
            Here is the company data (JSON format):{df_json}
            """
            }


            stream = chat(
                model='llama3.2',
                messages=[system_message, user_message],
                stream=True,
            )

            # Simulate stream of response with milliseconds delay
            for chunk in stream:
                msg = chunk['message']['content']
                full_response += msg + " "
                time.sleep(0.05)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(clean_markdown(full_response) + "▌")

            message_placeholder.markdown(clean_markdown(full_response))

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )


