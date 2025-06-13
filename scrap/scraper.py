import os  #helps with file paths
import time #helps with waiting for pages to load
import json #helps with saving data
from pathlib import Path #more modern way to handle file paths
from selenium import webdriver #automates browser interactions to scrape content from websites that rely on JScript
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait #helps with waiting for elements to load
from selenium.webdriver.support import expected_conditions as EC #helps with expected conditions
# by , webdriverwait, EC are used to wait and locate elements on the page (DOM: Document Object Model?)
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# TimeoutException: raised when a page takes too long to load
# NoSuchElementException: raised when an element is not found on the page

#Class definition and constructor
class TDSScraper:
    #constructor
    def __init__(self, url="https://tds.s-anand.net/#/2025-01/"):
        self.url = url
        self.setup_driver() #initializes the webdriver
        self.data_dir = Path("data") #creates a directory to save the data
        self.data_dir.mkdir(exist_ok=True) #creates the directory if it doesn't exist

    #sets up the webdriver
    def setup_driver(self):
        """Set up Chrome driver with appropriate options"""
        options = webdriver.ChromeOptions() #opens browser in full screen
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        #useful if you're running on a server without a GUI
        
        self.driver = webdriver.Chrome(options=options) #launches the browser

    def wait_for_dynamic_content(self, timeout=30):
        """Wait for dynamic content to load"""
        try:
            # webdriverwait is used to wait for an element to be present on the page
            # EC.presence_of_element_located is used to check if the element is present on the page in this case the sidebar-nav
            print("Waiting for dynamic content to load...")
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar-nav"))
            )
            # Give extra time for JavaScript to fully render
            time.sleep(2)
        except TimeoutException:
            print("Timeout waiting for dynamic content")
            return False
        return True

    def expand_all_folders(self):
        # Expand all folders in the sidebar by clicking them
        print("Expanding all sidebar folders...")
        folders = self.driver.find_elements(By.CSS_SELECTOR, ".sidebar-nav .folder > a")
        for folder in folders:
            try:
                if "open" not in folder.find_element(By.XPATH, "..").get_attribute("class"):
                    self.driver.execute_script("arguments[0].click();", folder)
                    time.sleep(0.2)
            except Exception:
                continue

    def get_full_structure(self):
        # Recursively extract all sections and subsections from the sidebar
        def extract_sections(element, parent_path=None):
            parent_path = parent_path or []
            sections = []
            items = element.find_elements(By.XPATH, ".//li[not(contains(@class, 'divider'))]")
            for item in items:
                try:
                    a_tag = item.find_element(By.TAG_NAME, "a")
                    title = a_tag.text.strip()
                    href = a_tag.get_attribute("href")
                    href_hash = a_tag.get_attribute("href").split("#")[-1] if "#" in href else ""
                    current_path = parent_path + [title]
                    # Check for nested ul (subsections)
                    sub_ul = None
                    try:
                        sub_ul = item.find_element(By.TAG_NAME, "ul")
                    except NoSuchElementException:
                        pass
                    if sub_ul:
                        # Recursively extract subsections
                        subsections = extract_sections(sub_ul, current_path)
                        sections.append({
                            "title": title,
                            "href": href_hash,
                            "path": current_path,
                            "subsections": subsections
                        })
                    else:
                        sections.append({
                            "title": title,
                            "href": href_hash,
                            "path": current_path,
                            "subsections": []
                        })
                except Exception:
                    continue
            return sections
        sidebar = self.driver.find_element(By.CLASS_NAME, "sidebar-nav")
        try:
            ul = WebDriverWait(sidebar, 10).until(
                lambda s: s.find_element(By.TAG_NAME, "ul")
            )
        except Exception as e:
            print("Could not find <ul> in sidebar-nav. Sidebar HTML:")
            print(sidebar.get_attribute('outerHTML'))
            raise e
        return extract_sections(ul)

    def get_section_content(self, href):
        """Get content for a specific section"""
        try:
            # Navigate to section using hash
            self.driver.execute_script(f"window.location.hash = '{href}'")
            time.sleep(1)  # Allow content to load
            
            # Wait for main content to load
            content = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "markdown-section"))
            )
            
            return content.get_attribute('innerHTML')
        except Exception as e:
            print(f"Error getting content for {href}: {e}")
            return ""

    def scrape(self):
        """Main scraping function"""
        try:
            print(f"Starting scrape of {self.url}")
            self.driver.get(self.url)
            
            if not self.wait_for_dynamic_content():
                return
            
            self.expand_all_folders()
            structure = self.get_full_structure()
            if not structure:
                print("No sections found")
                return
            
            # Process each section and its content
            course_content = {}
            section_paths = []
            
            def scrape_recursive(sections):
                for section in sections:
                    path_str = " > ".join(section["path"])
                    print(f"Processing: {path_str}")
                    section_paths.append(path_str)
                    content = self.get_section_content(section["href"])
                    # Store content at full path
                    d = course_content
                    for p in section["path"][:-1]:
                        d = d.setdefault(p, {"subsections": {}})["subsections"]
                    d[section["path"][-1]] = {
                        "content": content,
                        "subsections": {}
                    }
                    if section["subsections"]:
                        scrape_recursive(section["subsections"])
            
            scrape_recursive(structure)
            
            # Save the data
            with open(self.data_dir / "tds_course_content.json", "w", encoding="utf-8") as f:
                json.dump({
                    "sections": section_paths,
                    "content": course_content
                }, f, ensure_ascii=False, indent=4)
                
            print("\nScraping completed successfully!")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = TDSScraper()
    scraper.scrape() 