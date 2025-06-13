# TDS Virtual Teaching Assistant Project

## Project Overview
This project aims to create a Virtual Teaching Assistant for the Tools in Data Science (TDS) course at IIT Madras Online Degree Program. The system is designed to automatically answer student questions by leveraging historical course discussions and content.

## Project Components

### 1. Data Collection (Current Phase)
- **Discourse Forum Scraper** (`scraper2.py`)
  - Collects posts from TDS Knowledge Base forum
  - Date range: January 1, 2025 - April 14, 2025
  - Stores structured data in JSON format

### 2. Data Processing (Upcoming)
- Text preprocessing
- Question-Answer pair extraction
- Topic modeling
- Knowledge base creation

### 3. Question Answering System (Planned)
- Natural Language Processing
- Context-aware response generation
- Answer validation
- Response ranking

## Project Structure
```
TDS_Virtual_TA/
├── scraper2.py          # Discourse forum data scraper
├── requirements.txt     # Python dependencies
├── README.md           # Technical setup guide
├── README2.md          # Project overview (this file)
└── .env                # Configuration (create from .env.example)
```

## Data Collection Details

### Forum Data Structure
The scraper collects the following information for each post:
- Post title
- Author information
- Publication date
- Post URL
- Complete post content

### Data Storage
- Format: JSON
- File: `tds_posts.json`
- Data is structured for easy processing and analysis

## Development Roadmap

### Phase 1: Data Collection (Current)
- [x] Set up Discourse forum scraper
- [x] Implement authentication
- [x] Add date filtering
- [x] Handle pagination
- [x] Error handling and rate limiting

### Phase 2: Data Processing
- [ ] Clean and preprocess text data
- [ ] Extract question-answer pairs
- [ ] Identify topic categories
- [ ] Create structured knowledge base

### Phase 3: QA System Development
- [ ] Implement question analysis
- [ ] Develop answer generation system
- [ ] Add context awareness
- [ ] Create response validation

## Contributing
This project is part of the TDS course improvement initiative. Contributions are welcome through:
- Bug reports
- Feature suggestions
- Code improvements
- Documentation updates

## Project Goals
1. Reduce response time for common student queries
2. Maintain consistency in answers
3. Provide 24/7 assistance
4. Reduce workload on human TAs
5. Build a comprehensive knowledge base

## Note on Data Usage
The collected data is intended solely for educational purposes within the TDS course context. Usage should comply with IITM's data policies and privacy guidelines. 