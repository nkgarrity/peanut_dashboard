# dropbox_client.py
import os
from dropbox import Dropbox
from datetime import datetime, timedelta
import json
import requests
import streamlit as st

class DropboxClientManager:
    def __init__(self):
        # Check for environment variables
        self.APP_KEY = os.getenv('DROPBOX_APP_KEY')
        self.APP_SECRET = os.getenv('DROPBOX_APP_SECRET')
        self.REFRESH_TOKEN = os.getenv('DROPBOX_REFRESH_TOKEN')
        
        # Validate credentials
        if not all([self.APP_KEY, self.APP_SECRET, self.REFRESH_TOKEN]):
            missing = []
            if not self.APP_KEY: missing.append('DROPBOX_APP_KEY')
            if not self.APP_SECRET: missing.append('DROPBOX_APP_SECRET')
            if not self.REFRESH_TOKEN: missing.append('DROPBOX_REFRESH_TOKEN')
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
            
        self.dbx = None
        self.token_expiry = None
        
    def refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        try:
            token_url = "https://api.dropboxapi.com/oauth2/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.REFRESH_TOKEN,
                "client_id": self.APP_KEY,
                "client_secret": self.APP_SECRET
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                # Update the token expiry time (token usually valid for 4 hours)
                self.token_expiry = datetime.now() + timedelta(hours=3.9)
                return token_data['access_token']
            else:
                st.error(f"Token refresh failed: {response.text}")
                raise Exception(f"Token refresh failed: {response.text}")
                
        except Exception as e:
            st.error(f"Error refreshing token: {str(e)}")
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
            st.error(f"Error getting Dropbox client: {str(e)}")
            raise
    
    def get_file(self, dropbox_path):
        """Get a file from Dropbox with automatic token refresh"""
        try:
            dbx = self.get_client()
            metadata, response = dbx.files_download(dropbox_path)
            return response.content
        except Exception as e:
            st.error(f"Error accessing Dropbox file {dropbox_path}: {str(e)}")
            return None

# For testing the client directly
if __name__ == "__main__":
    # Simple test function
    client = DropboxClientManager()
    dbx = client.get_client()
    account = dbx.users_get_current_account()
    print(f"Successfully connected to account: {account.email}")