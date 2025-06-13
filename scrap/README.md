# TDS Virtual TA - Discourse Scraper

This script scrapes the IIT Madras Online Degree Tools in Data Science (TDS) Discourse forum for posts within a specific date range (1 Jan 2025 - 14 Apr 2025).

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- ChromeDriver (compatible with your Chrome version)

## Setup

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Discourse forum credentials:
   ```bash
   cp .env.example .env
   ```
4. Edit the `.env` file with your username and password

## Usage

Run the scraper:
```bash
python scraper2.py
```

The script will:
1. Login to the Discourse forum
2. Scrape all TDS posts within the specified date range
3. Save the data to `tds_posts.json`

## Output Format

The scraped data will be saved in JSON format with the following structure:
```json
[
  {
    "title": "Post Title",
    "author": "Author Name",
    "date": "YYYY-MM-DD",
    "url": "Post URL",
    "content": "Post Content"
  },
  ...
]
```

## Error Handling

- The script includes error handling for network issues and authentication failures
- Failed login attempts will be logged
- Rate limiting is implemented to avoid overwhelming the server

## Notes

- This script is designed specifically for the IITM Online Degree TDS Discourse forum
- Please be respectful of the forum's resources and avoid excessive scraping
- The script uses headless Chrome to run without a visible browser window 