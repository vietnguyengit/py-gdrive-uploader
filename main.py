import os
import argparse
from collections import defaultdict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm

# Define the scopes for Google Drive API
SCOPES = ["https://www.googleapis.com/auth/drive"]


# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Upload files to Google Drive")
    parser.add_argument(
        "-s", "--source", type=str, help="Source folder path", required=True
    )
    parser.add_argument(
        "-a", "--auth", type=str, help="Path to credentials.json", required=True
    )
    return parser.parse_args()


# Authenticate and authorise the user
def authorize(credentials_path):
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    credentials = flow.run_local_server()
    return credentials


# Upload file to Google Drive
def upload_file(file_path, folder_id=None, credentials=None):
    service = build("drive", "v3", credentials=credentials)

    file_name = os.path.basename(file_path)
    file_metadata = {"name": file_name, "parents": [folder_id] if folder_id else None}

    media = MediaFileUpload(file_path)

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )


# Recursively upload files from a directory
def upload_from_directory(
    directory_path, parent_folder_id=None, credentials=None, pbar=None
):
    service = build("drive", "v3", credentials=credentials)

    # Create a folder in Google Drive corresponding to the current directory
    folder_name = os.path.basename(directory_path)
    folder_metadata = {
        "name": folder_name,
        "parents": [parent_folder_id] if parent_folder_id else None,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder.get("id")

    # Upload files directly within the current directory to the created folder
    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            upload_file(file_path, folder_id, credentials)
            # Update the progress bar
            pbar.update(1)

    # Recursively upload files from subdirectories
    for root, dirs, _ in os.walk(directory_path):
        for subdir in dirs:
            subdir_path = os.path.join(root, subdir)
            upload_from_directory(subdir_path, folder_id, credentials, pbar)


# Count files by type
def count_files_by_type(directory_path):
    file_count = defaultdict(int)
    for root, _, files in os.walk(directory_path):
        for file in files:
            _, extension = os.path.splitext(file)
            file_count[extension.lower()] += 1
    return file_count


# Display folder structure and file count summary
def display_summary(directory_path):
    print("Folder Structure Summary:")
    root_dir_name = os.path.basename(directory_path)
    print(root_dir_name + "/")
    for root, dirs, _ in os.walk(directory_path):
        if root != directory_path:
            level = root.replace(directory_path, "").count(os.sep)
            indent = " " * 4 * (level)
            print(f"{indent}{os.path.basename(root)}/")
    print("\nFile Count Summary:")
    file_count = count_files_by_type(directory_path)
    for extension, count in file_count.items():
        print(f"  {extension}: {count} file(s)")


def main():
    args = parse_arguments()
    credentials = authorize(args.auth)
    display_summary(args.source)
    upload_confirmation = input("Ready to upload? (y/n): ")
    # Initialise tqdm progress bar with the total number of files
    total_files = sum(len(files) for _, _, files in os.walk(args.source))
    with tqdm(total=total_files, unit="file") as pbar:
        if upload_confirmation.lower() == "y":
            upload_from_directory(args.source, credentials=credentials, pbar=pbar)
        else:
            print("Upload cancelled. Exiting...")


# Entry point
if __name__ == "__main__":
    main()
