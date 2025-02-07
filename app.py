# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
from datetime import datetime
from dotenv import load_dotenv
from dropbox_client import DropboxClientManager

# Load environment variables
load_dotenv()

# Initialize the Dropbox client manager
@st.cache_resource
def get_dropbox_manager():
    """Create or get cached DropboxClientManager"""
    try:
        return DropboxClientManager()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error initializing Dropbox client: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(dropbox_path):
    """Load data from Dropbox with caching"""
    try:
        manager = get_dropbox_manager()
        if manager is None:
            return None
            
        content = manager.get_file(dropbox_path)
        if content is None:
            return None
            
        # Read CSV from bytes content
        df = pd.read_csv(io.BytesIO(content))
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Set up the Streamlit page
st.set_page_config(page_title="Sample Analysis Dashboard", layout="wide")

# Debug information (will be hidden in production)
if st.secrets.get("show_debug", False):
    st.write("Debug Information:")
    st.write(f"APP_KEY exists: {bool(os.getenv('DROPBOX_APP_KEY'))}")
    st.write(f"APP_SECRET exists: {bool(os.getenv('DROPBOX_APP_SECRET'))}")
    st.write(f"REFRESH_TOKEN exists: {bool(os.getenv('DROPBOX_REFRESH_TOKEN'))}")

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

else:
    st.error("""
    Unable to load data from Dropbox. Please check:
    1. Your Dropbox credentials are correctly set in the environment variables
    2. The file path is correct
    3. Your refresh token has the correct permissions
    """)
    
    # Show the file path for verification
    st.info(f"Attempting to access file at: {DROPBOX_PATH}")