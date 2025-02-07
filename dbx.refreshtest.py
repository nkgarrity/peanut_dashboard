# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 10:21:23 2025

@author: nkgarrit
"""

# test_dropbox.py
import os
from dropbox import Dropbox
from dropbox.oauth import DropboxOAuth2FlowNoRedirect
from datetime import datetime, timedelta
from dotenv import load_dotenv

def test_dropbox_auth():
    """Test Dropbox authentication and file access"""
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    APP_KEY = os.getenv('DROPBOX_APP_KEY')
    APP_SECRET = os.getenv('DROPBOX_APP_SECRET')
    REFRESH_TOKEN = os.getenv('DROPBOX_REFRESH_TOKEN')
    
    # Verify credentials exist
    print("\nChecking environment variables:")
    print(f"APP_KEY exists: {bool(APP_KEY)}")
    print(f"APP_SECRET exists: {bool(APP_SECRET)}")
    print(f"REFRESH_TOKEN exists: {bool(REFRESH_TOKEN)}")
    
    if not all([APP_KEY, APP_SECRET, REFRESH_TOKEN]):
        print("\nError: Missing required environment variables!")
        return
    
    try:
        print("\nAttempting to get access token...")
        # Initialize the OAuth2 flow
        auth_flow = DropboxOAuth2FlowNoRedirect(
            APP_KEY,
            APP_SECRET,
            token_access_type='offline'
        )
        
        # Try to get a new access token using the refresh token
        token_response = auth_flow.finish({'refresh_token': REFRESH_TOKEN})
        print("Successfully obtained access token!")
        
        print("\nTrying to initialize Dropbox client...")
        # Try to initialize the Dropbox client
        dbx = Dropbox(token_response.access_token)
        
        print("\nTesting API access...")
        # Test the connection by trying to get account info
        account = dbx.users_get_current_account()
        print(f"Successfully connected to Dropbox account: {account.email}")
        
        # Try to list files in the root directory
        print("\nListing files in root directory:")
        files = dbx.files_list_folder('')
        for entry in files.entries:
            print(f"Found: {entry.path_display}")
            
        print("\nAll tests passed successfully!")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nPlease verify:")
        print("1. Your APP_KEY and APP_SECRET are correct")
        print("2. Your REFRESH_TOKEN is valid")
        print("3. Your app has the correct permissions (files.metadata.read, files.content.read)")
        print("4. Your app is active in the Dropbox App Console")

if __name__ == "__main__":
    test_dropbox_auth()