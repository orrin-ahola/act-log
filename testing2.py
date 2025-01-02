from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import streamlit as st
from datetime import datetime
import io
import json

# Google Drive setup
SERVICE_ACCOUNT_FILE = '/home/orrin/PycharmProjects/act-log/act-log-006dc2903420.json'  # Replace with your service account JSON file path
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1lZgB4eAXuWyvf3-QyYB-X3OgwsgoXHT9'  # Replace with the ID of your Google Drive folder
JSON_FILE_NAME = 'submissions.json'

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)


# Load submissions from Google Drive
def load_submissions():
    try:
        # Search for the JSON file in the folder
        query = f"'{FOLDER_ID}' in parents and name = '{JSON_FILE_NAME}' and mimeType = 'application/json'"
        results = drive_service.files().list(q=query, spaces='drive').execute()
        files = results.get('files', [])
        if not files:
            return []  # Return an empty list if the file doesn't exist

        file_id = files[0]['id']
        request = drive_service.files().get_media(fileId=file_id)
        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        file_data.seek(0)
        return json.load(file_data)
    except Exception as e:
        print(f"Error loading submissions: {e}")
        return []


# Save submissions to Google Drive
def save_submissions(submissions):
    try:
        # Search for the JSON file in the folder
        query = f"'{FOLDER_ID}' in parents and name = '{JSON_FILE_NAME}' and mimeType = 'application/json'"
        results = drive_service.files().list(q=query, spaces='drive').execute()
        files = results.get('files', [])

        file_metadata = {
            'name': JSON_FILE_NAME,
            'parents': [FOLDER_ID],
            'mimeType': 'application/json'
        }
        file_data = io.BytesIO(json.dumps(submissions).encode())

        if files:
            # Update the existing file
            file_id = files[0]['id']
            media = MediaFileUpload(file_data, mimetype='application/json')
            drive_service.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Create a new file
            media = MediaFileUpload(file_data, mimetype='application/json')
            drive_service.files().create(body=file_metadata, media_body=media).execute()
    except Exception as e:
        print(f"Error saving submissions: {e}")


def submit_form():
    if st.session_state.user_input:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submission = f"{timestamp} - {st.session_state.user_input}"
        st.session_state.submissions.append(submission)
        st.session_state.user_input = ""
        save_submissions(st.session_state.submissions)


def delete_submission(index):
    st.session_state.submissions.pop(index)
    save_submissions(st.session_state.submissions)


def edit_submission(index, new_value):
    st.session_state.submissions[index] = new_value
    st.session_state.edit_index = None
    st.session_state.edit_value = ""
    save_submissions(st.session_state.submissions)


# Initialize session state for inputs and submissions if not already initialized
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'submissions' not in st.session_state:
    st.session_state.submissions = load_submissions()
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
if 'edit_value' not in st.session_state:
    st.session_state.edit_value = ""

# App title
st.title("Activity Log")

# Input form
with st.form(key="input_form"):
    user_input = st.text_input("Enter an item:", key="user_input")
    submit_button = st.form_submit_button(label="Submit", on_click=submit_form)

# Display the submissions
st.subheader("Entries")
if st.session_state.submissions:
    for i, item in enumerate(reversed(st.session_state.submissions)):
        actual_index = len(st.session_state.submissions) - 1 - i
        if st.session_state.edit_index == actual_index:
            cols = st.columns([7, 2, 2])
            st.session_state.edit_value = cols[0].text_input("Edit item:", value=st.session_state.edit_value,
                                                             key=f"edit_input_{actual_index}")
            cols[1].button("Save", key=f"save_{actual_index}", on_click=edit_submission,
                           args=(actual_index, st.session_state.edit_value))
            cols[2].button("Cancel", key=f"cancel_{actual_index}",
                           on_click=lambda: st.session_state.update(edit_index=None, edit_value=""))
        else:
            cols = st.columns([7, 2, 2, 1])
            cols[0].write(item)
            cols[1].button("Edit", key=f"edit_{actual_index}",
                           on_click=lambda idx=actual_index, val=item: st.session_state.update(edit_index=idx,
                                                                                               edit_value=val))
            cols[2].button("Delete", key=f"delete_{actual_index}", on_click=delete_submission, args=(actual_index,))
else:
    st.write("No submissions yet.")
