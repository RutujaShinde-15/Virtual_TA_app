import os
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import uuid

CONTENT_DIR = Path("content_md")
EMBEDDINGS_DIR = Path("embeddings")
EMBEDDINGS_DIR.mkdir(exist_ok=True)

EMBEDDING_ENDPOINT = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"
# Load API key from environment variable
AIPIPE_API_KEY = os.environ.get("AIPIPE_API_KEY")
if not AIPIPE_API_KEY:
    raise ValueError("AIPIPE_API_KEY environment variable not set. Please add it to your .env file.")

# Chunking function
def chunk_text(text, max_chunk_size=512):
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
                chunks.append(sentence)
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

# Embedding function
def create_embeddings_batch(texts, batch_size=32):
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

# Main processing
metadata_rows = []
texts = []
section_names = []

for md_file in CONTENT_DIR.glob("*.md"):
    section = md_file.stem
    print(f"Processing: {md_file.name}")
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()
    chunks = chunk_text(md_text)
    print(f"  Number of chunks: {len(chunks)}")
    if chunks:
        print(f"  First chunk: {chunks[0][:100]}...")
    else:
        print("  No chunks created (file may be empty or too short).")
    # Construct URL for the section
    url = f"https://tds.s-anand.net/#/{section.replace('_', '-')}"
    for i, chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        metadata_rows.append({
            "section": section,
            "chunk_index": i,
            "chunk_id": chunk_id,
            "filename": md_file.name,
            "text": chunk,
            "url": url
        })
        texts.append(chunk)
        section_names.append(section)

# Generate embeddings
embeddings = create_embeddings_batch(texts)

# Save embeddings
embeddings_array = np.array([e for e in embeddings if e is not None])
np.save(EMBEDDINGS_DIR / "course_embeddings.npy", embeddings_array)

# Save metadata
df_meta = pd.DataFrame(metadata_rows)
df_meta.to_csv(EMBEDDINGS_DIR / "course_metadata.csv", index=False)

# Save texts
df_texts = pd.DataFrame({"text": texts, "section": section_names})
df_texts.to_csv(EMBEDDINGS_DIR / "course_texts.csv", index=False)

print("Embeddings, metadata, and texts saved in the 'embeddings' folder.") 
