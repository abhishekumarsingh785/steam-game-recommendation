import pandas as pd
import streamlit as st
from PIL import Image
import requests
import pickle
import os
import numpy as np

# Caching the data loading function
@st.cache_data
def load_data():
    with open('data.pkl', 'rb') as f:
        data = pickle.load(f)
    return data

# Caching the model loading function
@st.cache_resource
def load_model():
    with open('tfidf_matrix.pkl', 'rb') as f:
        tfidf_matrix = pickle.load(f)
    with open('nn_model.pkl', 'rb') as f:
        nn_model = pickle.load(f)
    return tfidf_matrix, nn_model

# Function to get recommendations
def get_recommendations(game_name, data, tfidf_matrix, nn_model, n_recommendations=5):
    try:
        idx = data.index[data['Name'] == game_name][0]
    except IndexError:
        st.error("Game not found! Please check the game name and try again.")
        return pd.DataFrame()
    
    distances, indices = nn_model.kneighbors(tfidf_matrix[idx], n_neighbors=n_recommendations*2)
    indices = indices.flatten()
    distances = distances.flatten()
    
    # Exclude the input game itself
    mask = indices != idx
    indices = indices[mask]
    distances = distances[mask]
    
    # Remove duplicates based on 'Name'
    neighbor_names = data.iloc[indices]['Name'].values
    unique_names, unique_indices = np.unique(neighbor_names, return_index=True)
    indices = indices[unique_indices]
    
    # Get top N recommendations
    top_indices = indices[:n_recommendations]
    similar_games = data.iloc[top_indices]
    return similar_games[['Name', 'Header_image', 'Website']]

# Apply custom CSS for styling
st.markdown(
    """
    <style>
    .stMarkdown a img {
        border-radius: 15px;
    }
    .game-name {
        color: #FF5722;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load data and model
data = load_data()
tfidf_matrix, nn_model = load_model()

# Streamlit interface
st.title("🎮 Game Recommendation Engine")
st.markdown("Get personalized game recommendations!")

# Get the list of game names
game_names = data['Name'].unique()
default_game = "need for speed™"

# Ensure that the default game exists in the list
if default_game in game_names:
    default_index = list(game_names).index(default_game)
else:
    default_index = 0  # If not found, default to the first game

# Auto-suggestion search box for game names with default value
game_name = st.selectbox("Enter a game name:", game_names, index=default_index)

# Option to select the number of recommendations
num_recommendations = st.radio("Select number of recommendations:", [5, 10], index=0)

if game_name:
    recommendations = get_recommendations(game_name, data, tfidf_matrix, nn_model, n_recommendations=num_recommendations)
    
    if not recommendations.empty:
        # Display recommendations in rows of 2
        cols = st.columns(2)
        for idx, row in enumerate(recommendations.iterrows()):
            with cols[idx % 2]:
                game_name_rec = row[1]['Name']
                image_url = row[1]['Header_image']
                website = row[1]['Website'] if pd.notnull(row[1]['Website']) else "#"

                # Display the game image with hyperlink
                st.markdown(
                    f'<a href="{website}" target="_blank"><img src="{image_url}" style="width:100%; border-radius:15px;"></a>',
                    unsafe_allow_html=True
                )

                # Bold and color the game name
                st.markdown(f'<p class="game-name">{game_name_rec}</p>', unsafe_allow_html=True)
