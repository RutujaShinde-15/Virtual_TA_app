#!/usr/bin/env python3
import os
import json
from datetime import datetime
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
import getpass
import re

class DiscourseForumScraper:
    def __init__(self):
        # Load credentials from config file
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.username = None
        self.password = None
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.username = config.get('username')
                    self.password = config.get('password')
            except json.JSONDecodeError:
                print("\nError reading config.json. Make sure it's properly formatted JSON.")
                raise
        # Fallback to environment variables if not found in config.json
        if not self.username:
            self.username = os.environ.get('DISCOURSE_USERNAME')
        if not self.password:
            self.password = os.environ.get('DISCOURSE_PASSWORD')
        if not self.username or not self.password:
            print("\nCredentials not found in config.json or environment variables.")
            print("Please make sure your config.json contains:")
            print('''{
    "username": "your_email@example.com",
    "password": "your_password"
}''')
            print("Or set DISCOURSE_USERNAME and DISCOURSE_PASSWORD as environment variables.")
            raise ValueError("Missing credentials.")
        
        self.base_url = "https://discourse.onlinedegree.iitm.ac.in"
        self.forum_url = f"{self.base_url}/c/courses/tds-kb/34"
        self.start_date = datetime(2025, 1, 1)
        self.end_date = datetime(2025, 4, 14)
        self.posts_data = []

    def setup_driver(self):
        """Initialize and return the Chrome WebDriver"""
        try:
            # Initialize Chrome options with more robust settings
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless=new')  # Disable headless mode for debugging
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Add user agent to make the request look more like a real browser
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Create and return the WebDriver instance using Selenium Manager
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print(f"Error setting up Chrome WebDriver: {str(e)}")
            print("Please make sure Chrome is installed and up to date")
            raise

    def login(self, driver):
        """Login to the Discourse forum"""
        try:
            print(f"\nAttempting to login via Google...")
            
            # Navigate to login page
            print("1. Navigating to login page...")
            driver.get(f"{self.base_url}/login")
            print(f"Current URL: {driver.current_url}")
            
            # Wait for page to be fully loaded
            print("2. Waiting for page to be fully loaded...")
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Add a small delay to let any JavaScript execute
            time.sleep(3)
            
            # Look for Google login button with different possible selectors
            print("3. Looking for Google sign-in button...")
            try:
                # Try different possible selectors for the Google sign-in button
                selectors = [
                    "button[title*='Google']",
                    "button[class*='google']",
                    "a[href*='google']",
                    "button:contains('Sign in with Google')",
                    ".btn-social-login-google",
                    ".google-oauth2",
                    "button.google",
                    "//button[contains(text(), 'Sign in with Google')]",  # XPath
                    "//button[contains(., 'Google')]"  # XPath
                ]
                
                google_button = None
                for selector in selectors:
                    try:
                        if selector.startswith("//"):
                            # XPath selector
                            google_button = WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            # CSS selector
                            google_button = WebDriverWait(driver, 2).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        if google_button:
                            break
                    except:
                        continue
                
                if not google_button:
                    raise Exception("Google sign-in button not found")
                
                print("4. Found Google sign-in button, clicking...")
                
                # Scroll the button into view
                driver.execute_script("arguments[0].scrollIntoView(true);", google_button)
                time.sleep(1)
                
                # Try both normal click and JavaScript click
                try:
                    google_button.click()
                except:
                    driver.execute_script("arguments[0].click();", google_button)
                
                # Wait for Google login page
                print("5. Waiting for Google login page...")
                WebDriverWait(driver, 10).until(
                    lambda d: "accounts.google.com" in d.current_url.lower()
                )
                
                print("\n=== MANUAL LOGIN REQUIRED ===")
                print("1. Please complete the Google login in the browser window")
                print("2. The script will continue automatically once you're logged in")
                print("3. You have 5 minutes to complete the login")
                print("================================\n")
                
                # Wait for successful login (up to 5 minutes)
                print("Waiting for manual login completion...")
                WebDriverWait(driver, 300).until(
                    lambda d: (
                        # Check if we're back on the Discourse site
                        self.base_url in d.current_url
                        # And check for elements that indicate successful login
                        and (
                            len(d.find_elements(By.CLASS_NAME, "current-user")) > 0
                            or len(d.find_elements(By.CLASS_NAME, "user-menu")) > 0
                            or "login" not in d.current_url.lower()
                        )
                    )
                )
                
                print("\nLogin successful!")
                return True
                
            except Exception as e:
                print(f"\nError with Google sign-in: {str(e)}")
                if "accounts.google.com" in driver.current_url:
                    print("\nStill on Google login page. Login was not completed in time.")
                return False
            
        except Exception as e:
            print("\nLogin failed!")
            print(f"Error details: {str(e)}")
            print(f"Current URL: {driver.current_url}")
            
            # Take a screenshot for debugging
            try:
                screenshot_file = "login_error.png"
                driver.save_screenshot(screenshot_file)
                print(f"\nScreenshot saved as {screenshot_file}")
            except:
                print("\nFailed to save screenshot")
                
            return False

    def is_post_in_date_range(self, post_date):
        """Check if post date is within the specified range"""
        try:
            post_datetime = datetime.strptime(post_date, "%Y-%m-%d")
            return self.start_date <= post_datetime <= self.end_date
        except ValueError as e:
            print(f"Error parsing date {post_date}: {str(e)}")
            return False

    def extract_post_data(self, post_element):
        """Extract relevant data from a post element"""
        try:
            # Debug: Print raw HTML
            print("\nProcessing post:")
            print(post_element.prettify())
            
            # Get title
            title_elem = post_element.select_one('a.title.raw-link.raw-topic-link')
            if not title_elem:
                print("Could not find title element")
                return None
            title = title_elem.get_text(strip=True)
            print(f"Found title: {title}")
            
            # Get author (original poster)
            author = None
            posters_td = post_element.select_one('td.posters')
            if posters_td:
                # Try different ways to find the original poster
                poster_links = posters_td.select('a')
                for link in poster_links:
                    title_attr = link.get('title', '')
                    if 'Original Poster' in title_attr:
                        author = link.get('aria-label', '').replace("'s profile", '')
                        break
            
            if not author:
                print("Could not find author")
                return None
            print(f"Found author: {author}")
            
            # Get date
            date = None
            activity_td = post_element.select_one('td.activity')
            if activity_td:
                date_title = activity_td.get('title', '')
                print(f"Found date title: {date_title}")
                if date_title:
                    # Extract date from "Created: Sep 6, 2024 7:32 am" format
                    date_match = re.search(r'Created: ([A-Za-z]+ \d+, \d{4})', date_title)
                    if date_match:
                        try:
                            date_obj = datetime.strptime(date_match.group(1), '%b %d, %Y')
                            date = date_obj.strftime('%Y-%m-%d')
                        except Exception as e:
                            print(f"Error parsing date: {str(e)}")
            
            if not date:
                print("Could not find or parse date")
                return None
            print(f"Found date: {date}")
            
            # Get URL
            post_url = None
            if title_elem:
                href = title_elem.get('href')
                if href:
                    post_url = self.base_url + href
            
            if not post_url:
                print("Could not find URL")
                return None
            print(f"Found URL: {post_url}")
            
            print(f"\nSuccessfully extracted post: {title} by {author} on {date}")
            
            return {
                'title': title,
                'author': author,
                'date': date,
                'url': post_url
            }
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

    def scrape_post_content(self, post_url, driver, topic_id):
        """Scrape the content of an individual post and its replies"""
        try:
            print(f"\nFetching complete thread for topic {topic_id}")
            
            # Create session with cookies from Selenium
            session = requests.Session()
            cookies = driver.get_cookies()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            # Get the topic JSON data
            topic_json_url = f"{self.base_url}/t/{topic_id}.json"
            print(f"Fetching topic JSON from: {topic_json_url}")
            
            response = session.get(topic_json_url)
            response.raise_for_status()
            
            topic_data = response.json()
            
            # Extract all posts from the topic
            posts = topic_data.get('post_stream', {}).get('posts', [])
            
            if not posts:
                print("No posts found in topic")
                return ""
            
            # Process all posts in the thread
            thread_content = []
            for post in posts:
                username = post.get('username', '')
                created_at = post.get('created_at', '')
                content = post.get('cooked', '')  # 'cooked' contains the HTML content
                
                # Convert HTML to plain text
                soup = BeautifulSoup(content, 'html.parser')
                text_content = soup.get_text(separator='\n', strip=True)
                
                post_info = f"""
Author: {username}
Date: {created_at}
Content:
{text_content}
-------------------"""
                thread_content.append(post_info)
            
            return '\n'.join(thread_content)
            
        except Exception as e:
            print(f"Error scraping topic content: {str(e)}")
            return ""

    def scrape_forum(self):
        """Main method to scrape the forum"""
        try:
            driver = self.setup_driver()
            print("Chrome WebDriver initialized successfully")
            
            if not self.login(driver):
                raise Exception("Failed to login")

            page = 0  # Discourse API uses 0-based page numbers
            has_more_pages = True
            
            # Create a session with cookies from Selenium
            session = requests.Session()
            cookies = driver.get_cookies()
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            while has_more_pages:
                print(f"\nScraping page {page + 1}...")
                
                # Get the JSON data using requests instead of Selenium
                json_url = f"{self.forum_url}.json?page={page}"
                print(f"Fetching JSON from: {json_url}")
                
                try:
                    response = session.get(json_url)
                    response.raise_for_status()
                    
                    print(f"Response status code: {response.status_code}")
                    
                    # Try to parse the JSON
                    try:
                        data = response.json()
                    except json.JSONDecodeError as e:
                        print("Failed to decode JSON. Response content:")
                        print(response.text[:1000])
                        raise e
                    
                    # Extract topics from the JSON
                    topics = data.get('topic_list', {}).get('topics', [])
                    
                    if not topics:
                        print("No more topics found.")
                        has_more_pages = False
                        continue
                    
                    print(f"Found {len(topics)} topics on page {page + 1}")
                    
                    for topic in topics:
                        try:
                            # Extract post data from JSON
                            created_at = topic.get('created_at')
                            topic_id = topic.get('id')
                            
                            if isinstance(created_at, str):
                                # Parse ISO format date string
                                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            else:
                                # Parse Unix timestamp
                                date_obj = datetime.fromtimestamp(created_at)
                            
                            post_data = {
                                'id': topic_id,
                                'title': topic.get('title'),
                                'author': topic.get('posters', [{}])[0].get('user', {}).get('username'),
                                'date': date_obj.strftime('%Y-%m-%d'),
                                'url': f"{self.base_url}/t/{topic.get('slug')}/{topic_id}",
                                'views': topic.get('views'),
                                'replies': topic.get('posts_count', 1) - 1,  # Subtract 1 for the original post
                                'tags': topic.get('tags', [])
                            }
                            
                            print(f"\nProcessing topic: {post_data['title']}")
                            print(f"Date: {post_data['date']}")
                            
                            if self.is_post_in_date_range(post_data['date']):
                                # Get the complete thread content including replies
                                post_data['thread_content'] = self.scrape_post_content(post_data['url'], driver, topic_id)
                                self.posts_data.append(post_data)
                                print(f"Added post: {post_data['title']} by {post_data['author']} on {post_data['date']}")
                                print(f"Total posts collected: {len(self.posts_data)}")
                                
                                # Add delay to avoid overwhelming the server
                                time.sleep(1)
                                
                        except Exception as e:
                            print(f"Error processing topic: {str(e)}")
                            continue
                    
                    page += 1
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error making request: {str(e)}")
                    has_more_pages = False
                except Exception as e:
                    print(f"Unexpected error: {str(e)}")
                    has_more_pages = False
                
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
        
        finally:
            if 'driver' in locals():
                driver.quit()
            self.save_data()

    def save_data(self):
        """Save scraped data to a JSON file"""
        output_file = "tds_posts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.posts_data, f, ensure_ascii=False, indent=2)
        print(f"\nScraped data saved to {output_file}")
        print(f"Total posts collected: {len(self.posts_data)}")

if __name__ == "__main__":
    print("Starting TDS Discourse Forum Scraper...")
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Scrape TDS Discourse Forum')
    parser.add_argument('--username', help='Discourse forum username')
    parser.add_argument('--password', help='Discourse forum password')
    args = parser.parse_args()
    
    try:
        scraper = DiscourseForumScraper()
        scraper.scrape_forum()
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please provide credentials either through environment variables (DISCOURSE_USERNAME and DISCOURSE_PASSWORD)")
        print("or through command line arguments (--username and --password)") 