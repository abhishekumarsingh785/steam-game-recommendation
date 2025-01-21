#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pickle
import os
from io import StringIO
from azure.storage.blob import BlobServiceClient

connect_str = "DefaultEndpointsProtocol=https;AccountName=steamgamesraw;AccountKey=AccountKey;EndpointSuffix=core.windows.net"

# Specify your container and blob names
container_name = 'steamgamesdata'  # Replace with your actual container name
blob_name = 'games.csv'

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Get a BlobClient object for the blob
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# Download the blob's content
download_stream = blob_client.download_blob()
csv_content = download_stream.content_as_text()

# Read the CSV content into a pandas DataFrame
data = pd.read_csv(StringIO(csv_content))

# Feature extraction using 'Genres', 'Tags', and 'Developers'
data['combined_features'] = data['Genres'].fillna('') + ' ' + data['Tags'].fillna('') + ' ' + data['Developers'].fillna('')

# Convert the text features into a TF-IDF vector
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['combined_features'])

# Using Nearest Neighbors to find similar games
nn_model = NearestNeighbors(metric='cosine', algorithm='brute')
nn_model.fit(tfidf_matrix)

# Save the necessary components to disk using pickle
with open('data.pkl', 'wb') as f:
    pickle.dump(data, f)

with open('tfidf_matrix.pkl', 'wb') as f:
    pickle.dump(tfidf_matrix, f)

with open('nn_model.pkl', 'wb') as f:
    pickle.dump(nn_model, f)


# In[ ]:




