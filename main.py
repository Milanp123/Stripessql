import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def fetch_data():
    # Use your service account
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

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

# Your app title on the sidebar
st.sidebar.title("SQL Snippet Manager")

# Set up filters
st.sidebar.header("Filters")
# Search box
search_term = st.sidebar.text_input("Search snippets")
# Category selection
categories = df['category_id'].unique().tolist()
selected_category = st.sidebar.selectbox("Select a category", ['All'] + categories)

# Filter dataframe based on search term and category
df_searched = df[df['title'].str.contains(search_term, case=False) | df['description'].str.contains(search_term, case=False)]
if selected_category != 'All':
    df_searched = df_searched[df_searched['category_id'] == selected_category]

# Define number of columns based on number of entries
num_entries = len(df_searched)
num_cols = max(1, int(num_entries ** 0.5))

# Create columns
cols = st.columns(num_cols)

# Display snippets
i = 0
for idx, row in df_searched.iterrows():
    with cols[i % num_cols]:
        st.subheader(row['title'])
        st.write("Description: ", row['description'])
        st.code(row['code'])
        st.write("---")
    i += 1
