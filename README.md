# TDS Virtual TA

A virtual Teaching Assistant for IIT Madras' Tools in Data Science course that can automatically answer student questions based on course content and Discourse posts.

## Features

- Question answering using RAG (Retrieval Augmented Generation)
- Support for image attachments with text extraction
- Integration with Google's Gemini for text and image processing
- Semantic search across course content and Discourse posts
- Structured responses with relevant links

## Requirements

- Python 3.9 or higher (recommended: 3.9.x)
- [pip](https://pip.pypa.io/en/stable/)
- (Optional) [python-dotenv](https://pypi.org/project/python-dotenv/) for local environment variable loading

Absolutely! Here is a **comprehensive, copy-paste-ready README** for your `app_ta` app, with clear, step-by-step instructions for scraping, embedding, running, evaluating, and deploying the TDS Virtual TA.  
This version is organized, beginner-friendly, and includes all the details you requested.

---

## **Background**

This project builds an API that can automatically answer student questions based on:

- [Course content](https://tds.s-anand.net/#/2025-01/) (TDS Jan 2025, as of 15 Apr 2025)
- [TDS Discourse posts](https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34) (from 1 Jan 2025 to 14 Apr 2025)

---

## **Directory and Script Usage**

The `app_ta` directory contains all scripts and resources needed to build, test, and deploy the TDS Virtual TA application.

### **1. Scraping and Data Preparation**

- **Markdown Course Content:**
  - Download the course content markdown files as referenced in [`_sidebar.md`](https://github.com/sanand0/tools-in-data-science-public/blob/main/_sidebar.md).
  - Place all markdown files in `app_ta/scrap/content_md/`.
  - Run the following script to convert markdown files into embeddings:
    ```bash
    python scrap/md_to_embeddings.py
    ```
  - This will generate:
    - `app_ta/embeddings/course_embeddings.npy`
    - `app_ta/embeddings/course_metadata.csv`
    - `app_ta/embeddings/course_texts.csv`

- **Discourse Posts:**
  - Scrape Discourse posts using:
    ```bash
    python scrap/scraper2.py
    ```
    - This will create `app_ta/scrap/data/tds_posts.json`.
  - Convert the scraped JSON data into embeddings:
    ```bash
    python scrap/create_embeddings.py
    ```
    - This will generate:
      - `app_ta/embeddings/posts_embeddings.npy`
      - `app_ta/embeddings/posts_metadata.csv`
      - `app_ta/embeddings/posts_texts.csv`

### **2. Embedding Files**

All generated embedding files are stored in `app_ta/embeddings/`.

### **3. Running the API**

- The FastAPI application is located in `app_ta/app/`.
  - `main.py` is the entry point for the API.
  - `embeddings_util.py` contains LLM provider information.
  - `test_images/` contains images for testing image-based queries.

### **4. Evaluation**

- Use `app_ta/evaluate.yaml` for testing and evaluating the application.

---

## **Setup Instructions**

### **1. Clone the Repository**

```bash
git clone https://github.com/yourusername/tds-virtual-ta.git
cd tds-virtual-ta/app_ta
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Set Up Environment Variables**

Create a `.env` file in the `app_ta` directory with the following (replace with your actual keys):

```
GEMINI_API_KEY=your_gemini_api_key_here
AIPIPE_API_KEY=your_aipipe_api_key_here
# (Optional for scraping)
DISCOURSE_USERNAME=your_discourse_username
DISCOURSE_PASSWORD=your_discourse_password
     ```
- **Never commit your `.env` file!**
```

---

## **Building the App: Step-by-Step**

### **A. Prepare Embeddings**

#### **Course Content**

1. Download all markdown files referenced in the course sidebar and place them in `app_ta/scrap/content_md/`.
2. Run:
    ```bash
    python scrap/md_to_embeddings.py
    ```

#### **Discourse Posts**

1. Run:
    ```bash
    python scrap/scraper2.py
    ```
2. Then run:
    ```bash
    python scrap/create_embeddings.py
    ```

### **B. Run the API Locally**

1. Navigate to the app directory:
    ```bash
    cd app
    ```
2. Start the FastAPI server:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    or 
    ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`
3. Test the API with:
    ```bash
    curl "http://localhost:8000/api/json/" \
      -H "Content-Type: application/json" \
      -d "{\"question\": \"Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?\", \"image\": null}"
    ```

---

## **API Endpoint**

- **POST** `/api/json/`
- **Request Body:**
    ```json
    {
      "question": "Your question here",
      "image": "base64-encoded-image-or-null"
    }
    ```
- **Response:**
    ```json
    {
      "answer": "Your answer here.",
      "links": [
        {
          "url": "https://...",
          "text": "Link description"
        }
      ]
    }
    ```

---

## **Evaluation**

- Sample questions and evaluation parameters:  
  [project-tds-virtual-ta-promptfoo.yaml](https://tds.s-anand.net/project-tds-virtual-ta-promptfoo.yaml)
- To run evaluation:
    1. Edit the YAML to set your API URL.
    2. Run:
        ```bash
        npx -y promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
        ```

---

## **Deployment**

### **Deploy on Render**

1. **Create a `render.yaml` file** in `app_ta` (see [Render docs](https://render.com/docs/deploy-fastapi)).
2. **Push your code to GitHub.**
3. **Connect your repo to Render** and deploy as a web service.
4. **Set environment variables** in the Render dashboard (same as your `.env`).
    - `GEMINI_API_KEY`
   - `AIPIPE_API_KEY`
   - (Optional) `DISCOURSE_USERNAME`, `DISCOURSE_PASSWORD`
6. **Your API will be available at:**  
   `https://your-app-name.onrender.com/api/json/`
7. **Monitor logs and test your endpoints at the provided Render URL.**

---

## **Project Structure**

```
app_ta/
├── app/
│   ├── main.py                # Main FastAPI app
│   ├── embeddings_util.py     # LLM provider info
│   └── test_images/           # Test images
├── embeddings/                # Embedding files
├── scrap/
│   ├── md_to_embeddings.py    # Markdown to embeddings
│   ├── scraper2.py            # Discourse scraper
│   ├── create_embeddings.py   # Embedding generator
│   ├── content_md/            # Markdown files for course content
│   └── data/
├── evaluate.yaml              # Evaluation config
├── requirements.txt
├── render.yaml                # Render deployment config
└── .env                       # Environment variables (not committed)
```

---

## **Troubleshooting**

- **502 Bad Gateway on Render:**  
  - Check logs in the Render dashboard.
  - Ensure all environment variables are set.
  - Make sure your app listens on the correct port (`$PORT`).
- **UnicodeDecodeError:**  
  - Ensure `.env` and other text files are saved with UTF-8 encoding.
- **API not responding:**  
  - Check if embeddings are generated and available in the correct paths.
  - Verify all dependencies are installed.
- **UnicodeDecodeError on .env:**
  - Make sure your `.env` file is saved as UTF-8 (no BOM). In VS Code, click the encoding in the bottom right and select "Save with Encoding..." → "UTF-8".
- **Environment variable not set:**
  - Double-check your `.env` file and that you are loading it with `python-dotenv`.
- **404 Not Found on endpoints:**
  - Make sure you are using the correct endpoint (`/api/`, `/api/json/`).
- **Deployment issues:**
  - Check logs on Render for missing dependencies or environment variables.

---
## Security Best Practices
- **Never commit your `.env` file or any secrets to version control.**
- Use `.env.example` to share variable names (not values).
- Always use environment variables for API keys and passwords.


## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgements**

- [IIT Madras Online Degree](https://onlinedegree.iitm.ac.in/)
- [Course content by S. Anand](https://tds.s-anand.net/)
- [Discourse Community](https://discourse.onlinedegree.iitm.ac.in/)

---

**For any questions or contributions, feel free to open an issue or pull request!**

---

Let me know if you want to further customize any section, or need a template for `render.yaml` or `.env.example`!
