# Import the necessary libraries
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from yaml.loader import SafeLoader
import yaml
import json
import pyperclip

# Define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# Add your service account file
<<<<<<< HEAD
creds_json = json.loads(st.secrets["service_account"]["GOOGLE_SHEETS_API_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
=======
creds = ServiceAccountCredentials.from_json_keyfile_name(st.secrets['service_account'], scope)
>>>>>>> dbd3a0749447fd79c7bb3fe8b334209df9a98e4a

# Authorize the clientsheet
client = gspread.authorize(creds)

# Get the instance of the Spreadsheet
sheet = client.open('SQLSnippets')  # your Spreadsheet name here

# Get the first sheet of the Spreadsheet
sheet_instance = sheet.get_worksheet(0)

# Get all the records of the data
records_data = sheet_instance.get_all_records()

# Convert dict to dataframe
records_df = pd.DataFrame.from_dict(records_data)

# Get snippets
def get_snippets(search_query=None):
    if search_query:
        return records_df[records_df['title'].str.contains(search_query) | records_df['description'].str.contains(search_query)]
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
    with st.sidebar:
        st.subheader('Add a new SQL Snippet')
        new_snippet_title = st.text_input('Title')
        new_snippet_description = st.text_area('Description')
        new_snippet_code = st.text_area('Code')
        new_snippet_category_id = st.text_input('Category')
        if st.button('Add Snippet'):
            add_snippet(new_snippet_title, new_snippet_description, new_snippet_code, new_snippet_category_id)
            st.success('Snippet added successfully.')

    # Main section
    search_query = st.text_input('Search snippets')
    snippets = get_snippets(search_query)
    for index, snippet in snippets.iterrows():
        st.subheader(snippet['title'])  # title
        st.text(snippet['description'])  # description
        st.code(snippet['code'], language='sql')  # code
        if st.button('Copy to clipboard', key=snippet.name):
            pyperclip.copy(snippet['code'])
            st.success('Copied to clipboard.')

if __name__ == "__main__":
    app()
