import streamlit as st
import os
from dotenv import load_dotenv
from drive_utils import get_drive_service, get_or_create_folder, upload_file_to_drive

load_dotenv()

def main():
    st.set_page_config(page_title="File Upload with Label", page_icon="📁", layout="centered")
    
    st.title("📁 File Upload Interface")
    st.markdown("Please upload your file and provide a corresponding label.")
    
    # Form to group the inputs and submit button
    with st.form("upload_form"):
        # File uploader
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt", "pdf", "xlsx", "png", "jpg", "jpeg"])
        
        # Selectbox for label
        LABEL_TO_FOLDER = {
            "batch release": "batch-release",
            "pest control logs": "Pestcontrol-logs",
            "COA": "COA"
        }
        label = st.selectbox("Select a label for the file", options=list(LABEL_TO_FOLDER.keys()))
        
        # Submit button
        submit_button = st.form_submit_button(label="Submit")
        
        if submit_button:
            if uploaded_file is None:
                st.error("Please upload a file.")
            elif not label.strip():
                st.error("Please enter a label.")
            else:
                st.success(f"File '{uploaded_file.name}' successfully uploaded with label: '{label}'.")
                
                # Save the uploaded file to the local directory (syncs to OneDrive)
                save_dir = "uploads"
                os.makedirs(save_dir, exist_ok=True)
                
                # Clean up label for filename usage and construct path
                mapped_folder_name = LABEL_TO_FOLDER[label]
                file_name = f"{mapped_folder_name}_{uploaded_file.name}"
                file_path = os.path.join(save_dir, file_name)
                
                # Write file to disk
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"File saved locally to `{file_path}`.")
                
                # Google Drive Upload
                st.info("Uploading to Google Drive...")
                try:
                    BASE_FOLDER_ID = os.getenv("BASE_FOLDER_ID", "14AZi6h0F_Wb4sV70Nexhxl-oaeK8vnrX")
                    
                    service = get_drive_service()
                    folder_id = get_or_create_folder(service, mapped_folder_name, parent_id=BASE_FOLDER_ID)
                    file_id, web_link = upload_file_to_drive(service, file_path, folder_id, mime_type=uploaded_file.type)
                    
                    if file_id:
                        st.success(f"Successfully uploaded to Google Drive folder '{mapped_folder_name}'! [View File]({web_link})")
                    else:
                        st.error("Failed to upload to Google Drive.")
                except Exception as e:
                    st.error(f"Google Drive Error: {str(e)}")
                
                file_details = {
                    "Saved Path": file_path,
                    "Filename": uploaded_file.name,
                    "FileType": uploaded_file.type,
                    "FileSize": f"{uploaded_file.size / 1024:.2f} KB",
                    "Label": label
                }
                st.write("### File Details")
                st.json(file_details)

if __name__ == "__main__":
    main()
