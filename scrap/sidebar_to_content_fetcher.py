import os
import requests
from pathlib import Path
import re

# URL to the raw _sidebar.md file in the GitHub repo
SIDEBAR_MD_URL = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/main/_sidebar.md"
# Base URL for raw markdown files in the repo
RAW_BASE_URL = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/main/"
# Directory to save downloaded markdown files
CONTENT_DIR = Path("content_md")
CONTENT_DIR.mkdir(exist_ok=True)

def fetch_sidebar_md():
    resp = requests.get(SIDEBAR_MD_URL)
    resp.raise_for_status()
    return resp.text

def extract_links(sidebar_md):
    # Match markdown links: [Title](link)
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    links = pattern.findall(sidebar_md)
    return links

def fetch_and_save_content(links):
    for title, link in links:
        # Ignore external links (http/https)
        if link.startswith("http"): continue
        # Remove leading './' or '/' if present
        clean_link = link.lstrip('./').lstrip('/')
        # Only process .md files
        if not clean_link.endswith('.md'): continue
        url = RAW_BASE_URL + clean_link
        print(f"Fetching: {title} -> {url}")
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            # Save content to file named after the markdown file
            out_path = CONTENT_DIR / os.path.basename(clean_link)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

def main():
    sidebar_md = fetch_sidebar_md()
    links = extract_links(sidebar_md)
    fetch_and_save_content(links)
    print("\nAll content files downloaded to:", CONTENT_DIR.resolve())

if __name__ == "__main__":
    main() 