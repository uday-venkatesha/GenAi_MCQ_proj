import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logging
import streamlit as st  # Correct import statement for Streamlit

# Importing necessary packages from langchain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

# Load environment variables (if you're using a .env file for secrets)
load_dotenv()

# Retrieve the API key from Streamlit secrets or environment variable
key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Check if the key exists
if not key:
    raise ValueError("OpenAI API key is missing! Please set it in Streamlit secrets or .env file.")

# Initialize the LLM
llm = ChatOpenAI(openai_api_key=key, model_name="gpt-3.5-turbo", temperature=1)

# Define the quiz generation prompt template
template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to conform to the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide. \
Ensure to make {number} MCQs.
### RESPONSE_JSON
{response_json}
"""

# Create the prompt template for quiz generation
quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=template
)

# Create the LLM chain for quiz generation
quiz_chain = LLMChain(
    llm=llm,
    prompt=quiz_generation_prompt,
    output_key="quiz",
    verbose=True
)

# Define the evaluation prompt template
template2 = """
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
If the quiz is not at par with the cognitive and analytical abilities of the students,\
update the quiz questions which need to be changed and change the tone such that it perfectly fits the student abilities.
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

# Create the prompt template for quiz evaluation
quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=template2
)

# Create the LLM chain for quiz evaluation
review_chain = LLMChain(
    llm=llm,
    prompt=quiz_evaluation_prompt,
    output_key="review",
    verbose=True
)

# Overall chain that runs the two chains sequentially
generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"],
    verbose=True
)

# Usage of the chain
# Assuming you will call this chain with the appropriate variables later
# result = generate_evaluate_chain.invoke({
#    'text': 'some text content', 
#    'number': 5, 
#    'subject': 'Math', 
#    'tone': 'formal', 
#    'response_json': '{}'
# })
