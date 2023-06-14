import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def fetch_data():
    # Use your service account
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # Use secrets management for credentials
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)

    client = gspread.authorize(creds)

    # Open the google spreadsheet
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1f65SYuwx77ZWheN1TYocAH_yEr-SSH33sqHwapPMLQM/edit?usp=sharing')

    # Get the first sheet of the Spreadsheet
    worksheet = sheet.get_worksheet(0)

    # Get all values from the worksheet
    data = worksheet.get_all_values()

    # Get the data into pandas
    df = pd.DataFrame(data)

    # Set the headers as the first row
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)
    return df

df = fetch_data()

# Your app title
st.title("SQL Snippet Manager")

# Add a search box
search_term = st.text_input("Search snippets")

# Filter the dataframe based on the search term
df_searched = df[df['title'].str.contains(search_term, case=False) | df['description'].str.contains(search_term, case=False)]

# Display category options
categories = df_searched['category_id'].unique().tolist()
selected_category = st.selectbox("Select a category", categories)

# Display snippets in the selected category
df_filtered = df_searched[df_searched['category_id'] == selected_category]
snippet = st.selectbox("Select a snippet", df_filtered['title'].tolist())

# Display the code and description for the selected snippet
selected_snippet = df_filtered[df_filtered['title'] == snippet]

st.write("Description: ", selected_snippet['description'].values[0])
code = selected_snippet['code'].values[0]
st.code(code)
