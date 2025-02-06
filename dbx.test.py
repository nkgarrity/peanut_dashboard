# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 12:16:29 2025

@author: nkgarrit
"""

import os
from dropbox import Dropbox
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_dropbox_connection():
    try:
        # Get token from environment
        token = os.getenv('DROPBOX_ACCESS_TOKEN')
        if not token:
            print("No token found in environment variables")
            return
            
        # Initialize Dropbox
        dbx = Dropbox(token)
        
        # Test connection by listing files
        files = dbx.files_list_folder('')
        
        print("Connection successful!")
        print("\nFiles in root:")
        for entry in files.entries:
            print(f"- {entry.path_display}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dropbox_connection()