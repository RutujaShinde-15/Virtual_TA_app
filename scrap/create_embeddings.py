"""
Script to create embeddings from JSON content and store them locally using AI Proxy.
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "requests",
#   "numpy",
#   "pandas",
#   "tqdm",
#   "beautifulsoup4",
# ]
# ///

import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import uuid

# AI Proxy endpoint and token
EMBEDDING_ENDPOINT = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"
AIPIPE_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMzMDAwMDQ0QGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.sisufS-0IgJcx0U7PHmzom_2uYTbawSWZikYvRZXx2A"

#Utility functions

#a) load json data from file/path
def load_json_data(file_path):
    """Load and parse JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

#b) clean html text by removing html tags and formatting and returning plain text
def clean_html_text(html_text):
    """Clean HTML text and return plain text."""
    if not isinstance(html_text, str):
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

#c) extract text from posts data 
# get metadata and clean thread content and combine into structured text
def extract_text_from_posts(posts_data):
    """Extract content and metadata separately."""
    content_items = []
    
    for post in posts_data:
        post_id = str(uuid.uuid4())
        
        # Extract metadata
        metadata = {
            'title': post.get('title', ''),
            'date': post.get('date', ''),
            'url': post.get('url', ''),
            'tags': ', '.join(post.get('tags', [])),
            'views': post.get('views', 0),
            'replies': post.get('replies', 0)
        }
        
        # Create metadata chunk
        metadata_text = f"Title: {metadata['title']}\nTags: {metadata['tags']}"
        content_items.append({
            'chunk_id': str(uuid.uuid4()),
            'parent_id': post_id,
            'type': 'metadata',
            'text': metadata_text,
            'url': metadata['url'],
            'path': 'forum/metadata'
        })
        
        # Process main content
        content = clean_html_text(post.get('thread_content', ''))
        if content:
            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                content_items.append({
                    'chunk_id': str(uuid.uuid4()),
                    'parent_id': post_id,
                    'type': 'content',
                    'text': chunk,
                    'url': metadata['url'],
                    'path': f'forum/content/{i+1}'
                })
    
    return content_items

#d) extract text from course data
# recursively process sections and subsections and combine into structured text
def process_course_section(section_data, parent_path=''):
    """Process course content hierarchically."""
    content_items = []
    base_url = "https://tds.s-anand.net/"
    
    def process_section(data, current_path='', parent_id=None):
        for key, value in data.items():
            section_id = str(uuid.uuid4())
            current_full_path = f"{current_path}/{key}" if current_path else key
            
            if isinstance(value, dict):
                # Section header
                content_items.append({
                    'chunk_id': str(uuid.uuid4()),
                    'parent_id': section_id,
                    'type': 'header',
                    'text': key,
                    'url': f"{base_url}#/{current_full_path.lower().replace(' ', '-')}",
                    'path': current_full_path
                })
                # Process subsections
                process_section(value, current_full_path, section_id)
            else:
                # Content
                clean_content = clean_html_text(value)
                if clean_content:
                    chunks = chunk_text(clean_content)
                    for i, chunk in enumerate(chunks):
                        content_items.append({
                            'chunk_id': str(uuid.uuid4()),
                            'parent_id': section_id,
                            'type': 'content',
                            'text': chunk,
                            'url': f"{base_url}#/{current_full_path.lower().replace(' ', '-')}",
                            'path': f"{current_full_path}/chunk_{i+1}"
                        })
    
    process_section(section_data)
    return content_items

def chunk_text(text, max_chunk_size=512):
    """Split text into smaller chunks while preserving meaning."""
    if not text:
        return []
        
    sentences = text.split('.')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip() + '.'
        sentence_size = len(sentence.split())
        
        if current_size + sentence_size > max_chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                # Handle very long sentences by force-splitting
                chunks.append(sentence)
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def create_embeddings_batch(texts, batch_size=32):
    """Create embeddings in batches."""
    embeddings = []
    
    for i in tqdm(range(0, len(texts), batch_size)):
        batch = texts[i:i + batch_size]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPIPE_API_KEY}"
        }
        data = {
            "model": "text-embedding-3-small",
            "input": batch
        }
        
        try:
            response = requests.post(EMBEDDING_ENDPOINT, headers=headers, json=data)
            if response.status_code == 200:
                batch_embeddings = [item['embedding'] for item in response.json()['data']]
                embeddings.extend(batch_embeddings)
            else:
                print(f"Error in batch {i}: {response.text}")
                embeddings.extend([None] * len(batch))
        except Exception as e:
            print(f"Exception in batch {i}: {str(e)}")
            embeddings.extend([None] * len(batch))
    
    return embeddings

def save_embeddings_enhanced(embeddings_data, prefix):
    """Save embeddings with enhanced metadata."""
    os.makedirs('embeddings', exist_ok=True)
    
    # Save embeddings array
    valid_embeddings = [item['embedding'] for item in embeddings_data if item.get('embedding') is not None]
    embeddings_array = np.array(valid_embeddings)
    np.save(f'embeddings/{prefix}_embeddings.npy', embeddings_array)
    
    # Save metadata
    df = pd.DataFrame([{
        'chunk_id': item['chunk_id'],
        'parent_id': item['parent_id'],
        'type': item['type'],
        'text': item['text'],
        'url': item['url'],
        'path': item['path'],
        'embedding_index': idx
    } for idx, item in enumerate(embeddings_data) if item.get('embedding') is not None])
    
    df.to_csv(f'embeddings/{prefix}_metadata.csv', index=False)

def process_course_content_flat(course_data):
    """Process flat course content from markdown-derived JSON."""
    content_items = []
    for section, data in course_data['content'].items():
        text = data.get('content', '')
        if text:
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                content_items.append({
                    'chunk_id': str(uuid.uuid4()),
                    'parent_id': section,
                    'type': 'content',
                    'text': chunk,
                    'url': '',  # Optionally construct a URL if you have one
                    'path': f"{section}/chunk_{i+1}"
                })
    return content_items

def main():
    # Process posts data
    posts_data = load_json_data('data/tds_posts.json')
    posts_content_items = extract_text_from_posts(posts_data)
    
    # Create embeddings for posts
    posts_texts = [item['text'] for item in posts_content_items]
    posts_embeddings = create_embeddings_batch(posts_texts)
    
    # Add embeddings to content items
    for item, embedding in zip(posts_content_items, posts_embeddings):
        item['embedding'] = embedding
    
    # Save posts embeddings and metadata
    save_embeddings_enhanced(posts_content_items, 'posts')
    print(f"Processed {len(posts_content_items)} post chunks")
    
    # Process course content data (from markdown-derived JSON)
    course_data = load_json_data('data/tds_course_content.json')
    course_content_items = process_course_content_flat(course_data)
    
    # Create embeddings for course content
    course_texts = [item['text'] for item in course_content_items]
    course_embeddings = create_embeddings_batch(course_texts)
    
    # Add embeddings to content items
    for item, embedding in zip(course_content_items, course_embeddings):
        item['embedding'] = embedding
    
    # Save course embeddings and metadata
    save_embeddings_enhanced(course_content_items, 'course')
    print(f"Processed {len(course_content_items)} course chunks")

if __name__ == "__main__":
    main()