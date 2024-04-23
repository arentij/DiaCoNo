import os
from datetime import datetime

def check_create_folder(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Folder '{path}' created.")
        except OSError as e:
            print(f"Failed to create folder '{path}': {e}")
    else:
        print(f"Folder '{path}' already exists.")

# Generate the folder path based on current date
today = datetime.now()
folder_path = f"/CMFX_RAW_DATA/data/interferometer/test/{today.strftime('%Y_%m_%d')}"

# Check and create the folder if needed
check_create_folder(folder_path)