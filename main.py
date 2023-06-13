# Import the necessary libraries
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import yaml
import pyperclip
import os
import json

# Define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# Get the credentials from the environment variables
creds_json = json.loads(os.getenv("GOOGLE_SHEETS_API_CREDENTIALS"))

# Create the credentials object
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)

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

# Load the config file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Get snippets
def get_snippets(search_query=None):
    if search_query:
        return records_df[records_df['title'].str.contains(search_query) | records_df['description'].str.contains(search_query)]
    else:
        return records_df

# Add a new snippet
def add_snippet(title, description, code, category_id, user_id):
    global records_df
    new_data = {'title': title, 'description': description, 'code': code, 'category_id': category_id, 'user_id': user_id}
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

    # Authenticate user
    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        # Allow user to logout
        if st.button('Logout'):
            authenticator.logout()
            st.write('You have been logged out.')

        # Sidebar for adding a new snippet
        with st.sidebar:
            st.subheader('Add a new SQL Snippet')
            new_snippet_title = st.text_input('Title')
            new_snippet_description = st.text_area('Description')
            new_snippet_code = st.text_area('Code')
            new_snippet_category_id = st.text_input('Category')
            if st.button('Add Snippet'):
                add_snippet(new_snippet_title, new_snippet_description, new_snippet_code, new_snippet_category_id, username)
                st.success('Snippet added successfully!')

        # Search bar
        search_query = st.text_input('Search snippets')
        snippets = get_snippets(search_query)

        # Display snippets
        for index, snippet in snippets.iterrows():
            with st.beta_expander(snippet['title']):
                st.write(snippet['description'])
                st.code(snippet['code'])
                st.write('Category: ', snippet['category_id'])
                st.write('Contributor: ', snippet['user_id'])

                # Buttons for editing and deleting the snippet
                if st.button('Edit', key=f'edit_{index}'):
                    title = st.text_input('Title', value=snippet['title'])
                    description = st.text_area('Description', value=snippet['description'])
                    code = st.text_area('Code', value=snippet['code'])
                    category_id = st.text_input('Category', value=snippet['category_id'])
                    if st.button('Save Changes', key=f'save_{index}'):
                        edit_snippet(index, title, description, code, category_id)
                        st.success('Changes saved successfully!')

                if st.button('Delete', key=f'delete_{index}'):
                    delete_snippet(index)
                    st.success('Snippet deleted successfully!')

# Run the app
if __name__ == '__main__':
    app()
