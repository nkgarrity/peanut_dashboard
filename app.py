import streamlit as st
import pandas as pd
import plotly.express as px
from dropbox import Dropbox
import io
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Dropbox setup
class DropboxClient:
    def __init__(self):
        self.access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
        self.dbx = None
        self.last_refresh = None
        
    def connect(self):
        if not self.dbx:
            self.dbx = Dropbox(self.access_token)
        return self.dbx
    
    def get_file(self, dropbox_path):
        try:
            dbx = self.connect()
            metadata, response = dbx.files_download(dropbox_path)
            return response.content
        except Exception as e:
            st.error(f"Error accessing Dropbox: {e}")
            return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(dropbox_path):
    """Load data from Dropbox with caching"""
    client = DropboxClient()
    content = client.get_file(dropbox_path)
    
    if content:
        # Read CSV from bytes content
        df = pd.read_csv(io.BytesIO(content))
        return df
    return None

# Set up the Streamlit page
st.set_page_config(page_title="Sample Analysis Dashboard", layout="wide")

# Your Dropbox file path
DROPBOX_PATH = '/streamlit_test/data/samples_data.csv'  # Update this to your file path

# Load data
df = load_data(DROPBOX_PATH)

if df is not None:
    # Dashboard title
    st.title("Sample Analysis Dashboard")
    st.write("Comparing yield and disease ratings across samples")
    
    # Add refresh button
    if st.button("Refresh Data"):
        st.cache_data.clear()
        df = load_data(DROPBOX_PATH)
        st.rerun()
    
    # Display last update time
    st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    selected_treatments = st.sidebar.multiselect(
        "Select Treatments",
        options=df['treatment'].unique(),
        default=df['treatment'].unique()
    )
    
    # Filter data based on selection
    filtered_df = df[df['treatment'].isin(selected_treatments)]
    
    # Create two columns for metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Yield comparison box plot
        fig_yield = px.box(
            filtered_df,
            x='treatment',
            y='yield_bushels',
            color='treatment',
            title='Yield Distribution by Treatment'
        )
        st.plotly_chart(fig_yield, use_container_width=True)
        
        # Add summary statistics
        st.write("### Yield Summary Statistics")
        yield_stats = filtered_df.groupby('treatment')['yield_bushels'].agg([
            'mean', 'std', 'min', 'max'
        ]).round(2)
        st.dataframe(yield_stats)
    
    with col2:
        # Disease rating scatter plot
        fig_disease = px.scatter(
            filtered_df,
            x='sample_id',
            y='disease_rating',
            color='treatment',
            title='Disease Ratings by Sample'
        )
        st.plotly_chart(fig_disease, use_container_width=True)
        
        # Add summary statistics
        st.write("### Disease Rating Summary Statistics")
        disease_stats = filtered_df.groupby('treatment')['disease_rating'].agg([
            'mean', 'std', 'min', 'max'
        ]).round(2)
        st.dataframe(disease_stats)