
import re
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=openai_api_key)

def extract_rules_from_text(text):
    prompt = PromptTemplate.from_template("""
You are a compliance analyst for a credit fund. Extract structured rules from the following warehouse or loan buyer agreement section.

Text:
{agreement_text}

Return a Python dictionary with keys like:
- eligibility_criteria
- advance_rate
- triggers
- haircuts

Keep it concise and only include rules you are confident about.
""")
    return llm.predict(prompt.format(agreement_text=text))

def generate_code_from_rules(rules_text):
    prompt = PromptTemplate.from_template("""
You are a credit risk engineer. Write Python functions to implement the following rules:

{rules_yaml}

Include functions like:
- is_loan_eligible(loan)
- calculate_advance(principal, fico)
- trigger_checks(df)

Return pure Python code.
""")
    return llm.predict(prompt.format(rules_yaml=rules_text))
