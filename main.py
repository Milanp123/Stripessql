import pandas as pd
import gspread
import streamlit as st

# Authenticate and open the Google Sheet
gc = gspread.service_account()
sheet_url = 'https://docs.google.com/spreadsheets/d/1f65SYuwx77ZWheN1TYocAH_yEr-SSH33sqHwapPMLQM/edit#gid=0'  # Replace with your Google Sheet URL
sheet = gc.open_by_url(sheet_url)
worksheet = sheet.get_worksheet(0)  # Assuming the data is on the first sheet

# Get all the records from the sheet
records_data = worksheet.get_all_values()
headers = records_data[0]
records_data = records_data[1:]

# Convert records to DataFrame
records_df = pd.DataFrame(records_data, columns=headers)

# Search snippets
def search_snippets(search_query):
    return records_df[records_df['title'].str.contains(search_query, case=False) | records_df['description'].str.contains(search_query, case=False)]

# Streamlit app
def app():
    st.title("SQL Snippets")

    # Search snippets
    search_query = st.text_input('Search snippets')
    search_results = search_snippets(search_query)

    if search_query:
        st.subheader(f"Search results for '{search_query}':")
        for index, snippet in search_results.iterrows():
            st.subheader(snippet['title'])  # title
            st.text(snippet['description'])  # description
            st.code(snippet['code'], language='sql')  # code
    else:
        st.subheader("All snippets:")
        for index, snippet in records_df.iterrows():
            st.subheader(snippet['title'])  # title
            st.text(snippet['description'])  # description
            st.code(snippet['code'], language='sql')  # code

if __name__ == "__main__":
    app()
