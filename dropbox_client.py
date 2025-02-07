# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 09:13:25 2025

@author: nkgarrit
"""

# dropbox_client.py
import os
from dropbox import Dropbox
from dropbox.oauth import DropboxOAuth2FlowNoRedirect
from datetime import datetime, timedelta
import json

class DropboxClientManager:
    def __init__(self):
        self.APP_KEY = os.getenv('DROPBOX_APP_KEY')
        self.APP_SECRET = os.getenv('DROPBOX_APP_SECRET')
        self.REFRESH_TOKEN = os.getenv('DROPBOX_REFRESH_TOKEN')
        self.dbx = None
        self.token_expiry = None
        
    def refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        try:
            auth_flow = DropboxOAuth2FlowNoRedirect(
                self.APP_KEY,
                self.APP_SECRET,
                token_access_type='offline'
            )
            
            # Use the refresh token to get a new access token
            token_response = auth_flow.finish({'refresh_token': self.REFRESH_TOKEN})
            
            # Update the token expiry time (token usually valid for 4 hours)
            self.token_expiry = datetime.now() + timedelta(hours=3.9)
            
            return token_response.access_token
            
        except Exception as e:
            print(f"Error refreshing token: {e}")
            raise
    
    def get_client(self):
        """Get a Dropbox client with a valid access token"""
        try:
            # If we don't have a client or the token is expired/close to expiring
            if (self.dbx is None or 
                self.token_expiry is None or 
                datetime.now() + timedelta(minutes=5) >= self.token_expiry):
                
                # Get new access token
                access_token = self.refresh_access_token()
                
                # Create new client
                self.dbx = Dropbox(access_token)
            
            return self.dbx
            
        except Exception as e:
            print(f"Error getting Dropbox client: {e}")
            raise
    
    def get_file(self, dropbox_path):
        """Get a file from Dropbox with automatic token refresh"""
        try:
            dbx = self.get_client()
            metadata, response = dbx.files_download(dropbox_path)
            return response.content
        except Exception as e:
            print(f"Error accessing Dropbox: {e}")
            return None

# Initial setup helper function
def setup_dropbox_auth():
    """
    Helper function to get initial refresh token.
    Run this once to get your refresh token.
    """
    app_key = input("Enter your app key: ")
    app_secret = input("Enter your app secret: ")
    
    auth_flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        app_secret,
        token_access_type='offline'
    )
    
    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click 'Allow' (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()
    
    try:
        oauth_result = auth_flow.finish(auth_code)
        print("\nRefresh token:", oauth_result.refresh_token)
        print("Access token:", oauth_result.access_token)
        print("\nStore the refresh token in your environment variables as DROPBOX_REFRESH_TOKEN")
        
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    # Run this script directly to get your initial refresh token
    setup_dropbox_auth()