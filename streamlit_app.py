import streamlit as st

import pandas as pd

# Add a text input field for the GitHub raw URL
url = st.text_input("Enter the GitHub raw URL of the CSV file:", 
                    "https://raw.githubusercontent.com/JeanJMH/Financial_Classification/main/Classification_data.csv")

# Load the dataset if a valid URL is provided
if url:
    try:
        df1 = pd.read_csv(url)
        st.write("CSV Data:")
        st.write(df1)
    except Exception as e:
        st.error(f"An error occurred: {e}")


st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)


product_categories = df1['Product'].unique().tolist()
st.write(df1)

st.write(product_categories)


client_complaint = """ somebody stole money from my saving account
"""
assigned_issue = """ Problem with fraud alerts or security freezes00
"""

from openai import OpenAI
import os
import pandas as pd
from datetime import date
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit

# Load API Key for OpenAI
my_secret_key = userdata.get('MyOpenAIKey')
os.environ["OPENAI_API_KEY"] = my_secret_key
client = OpenAI()







import os
from jira_toolkit import JiraAPIWrapper, JiraToolkit
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import hub

# Set your OpenAI API key securely
my_secret_key = st.secrets["OPENAI_API_KEY"]

# Streamlit App Title
st.title("Jira Task Creator")

# Sidebar for Jira Credentials
st.sidebar.header("Jira Credentials")
jira_token = st.sidebar.text_input("JIRA API Token", type="password")
jira_username = st.sidebar.text_input("JIRA Username")
jira_instance_url = st.sidebar.text_input("JIRA Instance URL", "https://is883-genai-r.atlassian.net/")

# Environment Setup
if jira_token and jira_username and jira_instance_url:
    os.environ["JIRA_API_TOKEN"] = jira_token
    os.environ["JIRA_USERNAME"] = jira_username
    os.environ["JIRA_INSTANCE_URL"] = jira_instance_url
    os.environ["JIRA_CLOUD"] = "True"

# User Inputs for Task Details
st.header("Task Details")
project_key = st.text_input("Project Key", "FST")
assigned_issue = st.text_input("Task Summary")
client_complaint = st.text_area("Task Description")
assignee = st.text_input("Assignee Email", jira_username)

# Fraudulent Activity Detection
fraud_keywords = ["unauthorized access", "theft", "phishing", "stolen accounts"]
priority = "Highest" if any(keyword in client_complaint.lower() for keyword in fraud_keywords) else "High"

# Submit Button
if st.button("Create Jira Task"):
    # Initialize Jira API Wrapper and Toolkit
    jira = JiraAPIWrapper()
    toolkit = JiraToolkit.from_jira_api_wrapper(jira)

    # Fix tool names and descriptions in the toolkit
    for idx, tool in enumerate(toolkit.tools):
        toolkit.tools[idx].name = toolkit.tools[idx].name.replace(" ", "_")
        if "create_issue" in toolkit.tools[idx].name:
            toolkit.tools[idx].description += " Ensure to specify the project ID."

    # Add tools for the agent
    tools = toolkit.get_tools()

    # LLM Setup for LangChain
    chat = ChatOpenAI(openai_api_key=my_secret_key, model="gpt-4o-mini")

    # Prepare the LangChain ReAct Agent
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(chat, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Question for the agent
    question = (
        f"Create a task in my project with the key {project_key}. "
        f"The task's type is 'Task', assigned to {assignee}. "
        f"The summary is '{assigned_issue}'. "
        f"Always assign 'Highest' priority if the '{assigned_issue}' is related to fraudulent activities. "
        f"Fraudulent activities include terms or contexts like unauthorized access, theft, phishing, or stolen accounts. "
        f"Be strict in interpreting fraud-related issues. "
        f"Assign 'High' priority for other types of issues. "
        f"The description is '{client_complaint}'."
    )

    # Try to execute the agent
    try:
        result = agent_executor.invoke({"input": question})
        st.success("Jira Task Created Successfully!")
        st.json(result)
    except Exception as e:
        st.error(f"Error during Jira task creation: {e}")

