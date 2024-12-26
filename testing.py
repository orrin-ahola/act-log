import streamlit as st
from datetime import datetime

def submit_form():
    # Check if the input is not empty
    if st.session_state.user_input:
        # Prepend the input with the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submission = f"{timestamp} - {st.session_state.user_input}"
        # Append the submission to the list of submissions
        st.session_state.submissions.append(submission)
        # Clear the input box
        st.session_state.user_input = ""

def delete_submission(index):
    # Remove the submission at the given index
    st.session_state.submissions.pop(index)

def edit_submission(index, new_value):
    # Update the submission at the given index
    st.session_state.submissions[index] = new_value
    # Exit edit mode
    st.session_state.edit_index = None
    st.session_state.edit_value = ""

# Initialize session state for inputs and submissions if not already initialized
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'submissions' not in st.session_state:
    st.session_state.submissions = []
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
    # Display submissions in reverse order (newest first)
    for i, item in enumerate(reversed(st.session_state.submissions)):
        actual_index = len(st.session_state.submissions) - 1 - i  # Get the actual index for editing/deleting
        if st.session_state.edit_index == actual_index:
            # Editing mode
            cols = st.columns([7, 2, 2])  # Adjusted column widths: input, save, cancel
            st.session_state.edit_value = cols[0].text_input("Edit item:", value=st.session_state.edit_value, key=f"edit_input_{actual_index}")
            cols[1].button("Save", key=f"save_{actual_index}", on_click=edit_submission, args=(actual_index, st.session_state.edit_value))
            cols[2].button("Cancel", key=f"cancel_{actual_index}", on_click=lambda: st.session_state.update(edit_index=None, edit_value=""))
        else:
            # Normal mode
            cols = st.columns([7, 2, 2, 1])  # Adjusted column widths: text, edit, delete, placeholder
            cols[0].write(item)
            cols[1].button("Edit", key=f"edit_{actual_index}", on_click=lambda idx=actual_index, val=item: st.session_state.update(edit_index=idx, edit_value=val))
            cols[2].button("Delete", key=f"delete_{actual_index}", on_click=delete_submission, args=(actual_index,))
else:
    st.write("No submissions yet.")
