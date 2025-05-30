
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
#from langchain.agents import create_pandas_dataframe_agent
from langchain_experimental.agents import create_pandas_dataframe_agent
import streamlit as st
#from dotenv import load_dotenv

#load_dotenv()
#openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_key = st.secrets["OPENAI_API_KEY"]

def ask_llm_question(df, question):
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment.")

    llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=openai_api_key)
    agent = create_pandas_dataframe_agent(llm, df, verbose=False)
    return agent.run(question)
