import streamlit as st
import json
import pandas as pd
import os
from dotenv import load_dotenv
import traceback
from src.mcqgenerator.mcqgenerator import generate_evaluate_chain
from src.mcqgenerator.utils import read_file, get_table_data
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Set page configuration
st.set_page_config(
    page_title="MCQ Generator",
    page_icon="🧠",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Load response JSON format from file
try:
    with open("response.json", "r") as f:
        response_json_template = json.load(f)
except Exception as e:
    st.error(f"Error loading response.json file: {str(e)}")
    response_json_template = {}

# Title and description
st.title("📝 MCQ Generator App")
st.markdown("""
    Upload a file (PDF or TXT), set your preferences, and get AI-generated multiple choice questions!
""")

# File upload section
with st.sidebar:
    st.header("Input Parameters")
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
    
    # Input fields
    mcq_count = st.number_input("Number of MCQs", min_value=1, max_value=50, value=5)
    subject = st.text_input("Subject", value="General Knowledge")
    tone = st.selectbox("Tone", options=["Simple", "Complex"])
    
    generate_button = st.button("Generate MCQs")

# Main content area
if uploaded_file and generate_button:
    try:
        # Read file content
        text = read_file(uploaded_file)
        
        # Show a spinner while generating
        with st.spinner("Generating MCQs... This may take a moment."):
            # Generate MCQs
            response = generate_evaluate_chain(
                {
                    "text": text,
                    "number": mcq_count,
                    "subject": subject,
                    "tone": tone,
                    "response_json": json.dumps(response_json_template)
                }
            )
            
            # Display the generated MCQs
            st.success("MCQs generated successfully!")
            
            # Extract and display quiz data
            with st.expander("Generated Questions", expanded=True):
                # Parse the quiz string to get the table data
                try:
                    quiz_str = response.get("quiz", "")
                    # Find the JSON part in the response
                    json_str = quiz_str[quiz_str.find('{'):quiz_str.rfind('}')+1]
                    table_data = get_table_data(json_str)
                    
                    if table_data:
                        st.table(pd.DataFrame(table_data))
                    else:
                        st.error("Could not parse the quiz response into a table.")
                        st.code(quiz_str)
                except Exception as e:
                    st.error(f"Error parsing the quiz: {str(e)}")
                    st.code(quiz_str)
            
            # Display the review
            with st.expander("Expert Review"):
                st.write(response.get("review", "No review available."))
            
            # Download options
            try:
                quiz_json = json.loads(json_str)
                quiz_df = pd.DataFrame(table_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        "Download as CSV",
                        quiz_df.to_csv(index=False).encode('utf-8'),
                        f"mcq_{subject.lower().replace(' ', '_')}.csv",
                        "text/csv"
                    )
                
                with col2:
                    st.download_button(
                        "Download as JSON",
                        json.dumps(quiz_json, indent=4),
                        f"mcq_{subject.lower().replace(' ', '_')}.json",
                        "application/json"
                    )
            except Exception as e:
                st.warning(f"Could not prepare download files: {str(e)}")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error(traceback.format_exc())

# Display instructions when no file is uploaded
if not uploaded_file:
    st.info("Please upload a file to generate MCQs.")
    
    st.markdown("""
    ### How to use this app:
    1. Upload a PDF or TXT file using the sidebar
    2. Set the number of MCQs you want to generate
    3. Enter the subject for which the MCQs are intended
    4. Select the complexity tone (Simple or Complex)
    5. Click "Generate MCQs" to create your questions
    
    The app will process your file and generate high-quality MCQs based on the content.
    """)

# Add footer
st.markdown("---")
st.markdown("Built with Streamlit and OpenAI GPT")