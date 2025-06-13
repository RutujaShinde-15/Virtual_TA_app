import os
import json
from pathlib import Path

CONTENT_DIR = Path("content_md")
OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "tds_course_content.json"

sections = []
content = {}

for md_file in CONTENT_DIR.glob("*.md"):
    section_name = md_file.stem  # filename without .md
    sections.append(section_name)
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()
    content[section_name] = {
        "content": md_text,
        "filename": md_file.name
    }

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({
        "sections": sections,
        "content": content
    }, f, ensure_ascii=False, indent=4)

print(f"JSON file created at: {OUTPUT_FILE.resolve()}") 