import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain import hub


my_secret_key = st.secrets["MyOpenAIKey"]
os.environ["openai_api_key"] = my_secret_key

# Streamlit setup
st.title("Jira Task Creator")
#st.sidebar.header("Jira Credentials")

# Initialize Jira credentials
os.environ["JIRA_API_TOKEN"] = st.secrets['JIRA_API_TOKEN']
os.environ["JIRA_USERNAME"] = "rich@bu.edu"
os.environ["JIRA_INSTANCE_URL"] = "https://is883-genai-r.atlassian.net/"
os.environ["JIRA_CLOUD"] = "True"

client_complaint = """ somebody stole money from my saving account
"""
assigned_issue = """ Problem with fraud alerts or security freezes JIRATT1
"""


question = (
    f"Create a single task in my project with the key FST. Take into account tha the Key of this project is FST "
    f"The task's type is 'Task', assignee to rich@bu.edu,"
    f"The summary is '{assigned_issue}'."
    f"Always assign 'Highest' priority if the '{assigned_issue}' is related to fraudulent activities. Fraudulent activities include terms or contexts like unauthorized access, theft, phishing, or stolen accounts. Be strict in interpreting fraud-related issues."
    f"with the priority 'High' for other type of issues"
    f"with the description '{client_complaint}'. "
)

# Execute the agent to create the Jira task

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

# Create a question prompt for the Jira task
# priority = "Highest" if "fraud" in client_complaint.lower() else "High"


try:
    result = agent_executor.invoke({"input": question})
    print("Agent Output:", result)
except Exception as e:
    print(f"Error during Jira task creation: {e}")


st.write("Executing task creation...")
result = agent_executor.invoke({"input": question})
st.write("Task creation result:", result)

