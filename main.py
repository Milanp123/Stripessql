import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# Define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Load the Google Sheets API credentials from Streamlit secrets
creds = st.secrets["gcp_service_account"]

# Authorize the client
client = gspread.service_account_from_dict(creds, scope)

# Open the Google Sheet
sheet = client.open('SQLSnippets')

# Get the first sheet of the Spreadsheet
sheet_instance = sheet.sheet1

# Get all the records of the data
records_data = sheet_instance.get_all_records()

# Convert dict to dataframe
records_df = pd.DataFrame.from_records(records_data)

# Get snippets
def get_snippets(search_query=None):
    if search_query:
        return records_df[records_df['title'].str.contains(search_query, case=False) | records_df['description'].str.contains(search_query, case=False)]
    else:
        return records_df

# Add a new snippet
def add_snippet(title, description, code, category_id):
    global records_df
    new_data = {'title': title, 'description': description, 'code': code, 'category_id': category_id}
    records_df = records_df.append(new_data, ignore_index=True)
    set_with_dataframe(sheet_instance, records_df)

# Edit a snippet
def edit_snippet(index, title, description, code, category_id):
    global records_df
    records_df.loc[index, 'title'] = title
    records_df.loc[index, 'description'] = description
    records_df.loc[index, 'code'] = code
    records_df.loc[index, 'category_id'] = category_id
    set_with_dataframe(sheet_instance, records_df)

# Delete a snippet
def delete_snippet(index):
    global records_df
    records_df = records_df.drop(index)
    set_with_dataframe(sheet_instance, records_df)

# Streamlit app
def app():
    st.title("SQL Snippets")

    # Sidebar for adding a new snippet
    st.sidebar.subheader('Add a new SQL Snippet')
    new_snippet_title = st.sidebar.text_input('Title')
    new_snippet_description = st.sidebar.text_area('Description')
    new_snippet_code = st.sidebar.text_area('Code')
    new_snippet_category_id = st.sidebar.text_input('Category')
    if st.sidebar.button('Add Snippet'):
        add_snippet(new_snippet_title, new_snippet_description, new_snippet_code, new_snippet_category_id)
        st.sidebar.success('Snippet added successfully.')

    # Main section
    search_query = st.text_input('Search snippets')
    snippets = get_snippets(search_query)
    for index, snippet in snippets.iterrows():
        st.subheader(snippet['title'])  # title
        st.text(snippet['description'])  # description
        st.code(snippet['code'], language='sql')  # code
        if st.button('Copy to clipboard', key=snippet.name):
            st.success('Copied to clipboard.')

if __name__ == "__main__":
    app()
