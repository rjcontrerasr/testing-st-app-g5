import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain import hub

# Streamlit setup
st.title("Jira Task Creator")
st.sidebar.header("Jira Credentials")

# Sidebar inputs
jira_token = st.sidebar.text_input("JIRA API Token", type="password")
jira_username = st.sidebar.text_input("JIRA Username")
jira_instance_url = st.sidebar.text_input("JIRA Instance URL", "https://is883-genai-r.atlassian.net/")

# OpenAI Key
try:
    my_secret_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Missing OpenAI API Key in Streamlit secrets.")

# Load CSV
url = st.text_input("Enter the GitHub raw URL of the CSV file:", "https://raw.githubusercontent.com/JeanJMH/Financial_Classification/main/Classification_data.csv")
try:
    df1 = pd.read_csv(url)
    st.write(df1)
except Exception as e:
    st.error(f"Failed to load CSV: {e}")

# Task details
st.header("Task Details")
project_key = st.text_input("Project Key", "FST")
assigned_issue = st.text_input("Task Summary")
client_complaint = st.text_area("Task Description")
assignee = st.text_input("Assignee Email", jira_username)

# Fraud detection
fraud_keywords = ["unauthorized access", "theft", "phishing", "stolen accounts"]
priority = "Highest" if any(keyword in client_complaint.lower() for keyword in fraud_keywords) else "High"

# Create Jira Task
if st.button("Create Jira Task"):
    if not jira_token or not jira_username or not jira_instance_url:
        st.error("Please provide valid Jira credentials.")
    else:
        try:
            jira = JiraAPIWrapper()
            toolkit = JiraToolkit.from_jira_api_wrapper(jira)
            tools = toolkit.get_tools()
            chat = ChatOpenAI(openai_api_key=my_secret_key, model="gpt-4o-mini")
            prompt = hub.pull("hwchase17/react")
            agent = create_react_agent(chat, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            question = (
                f"Create a task in my project with the key {project_key}. "
                f"The task's type is 'Task', assigned to {assignee}. "
                f"The summary is '{assigned_issue}'. "
                f"The description is '{client_complaint}'. "
                f"Assign priority as '{priority}'."
            )
            result = agent_executor.invoke({"input": question})
            st.success("Jira Task Created Successfully!")
            st.json(result)
        except Exception as e:
            st.error(f"Error creating Jira Task: {e}")

