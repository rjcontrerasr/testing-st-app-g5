import streamlit as st

import pandas as pd

# Add a text input field for the GitHub raw URL
url = st.text_input("Enter the GitHub raw URL of the CSV file:", 
                    "https://raw.githubusercontent.com/JeanJMH/Financial_Classification/main/Classification_data.csv")

# Load the dataset if a valid URL is provided
if url:
    try:
        df = pd.read_csv(url)
        st.write("CSV Data:")
        st.write(df)
    except Exception as e:
        st.error(f"An error occurred: {e}")


st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

st.write(df)
