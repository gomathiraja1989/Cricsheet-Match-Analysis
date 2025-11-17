"""
Selenium Web Scraper for Cricsheet Match Data
Downloads JSON files for Test, ODI, T20, and IPL matches from cricsheet.org
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json


class CricsheetScraper:
    """Scraper class for downloading cricket match JSON files from cricsheet.org"""
    
    def __init__(self, download_dir="data/raw"):
        """
        Initialize the scraper
        
        Args:
            download_dir (str): Directory to save downloaded JSON files
        """
        self.download_dir = download_dir
        self.base_url = "https://cricsheet.org"
        self.matches_url = "https://cricsheet.org/matches/"
        
        # Create download directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        # Setup Chrome options
        self.chrome_options = Options()
        prefs = {
            "download.default_directory": os.path.abspath(download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        self.chrome_options.add_experimental_option("prefs", prefs)
        # Comment out headless mode for better debugging (uncomment if needed)
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
    def setup_driver(self):
        """Setup and return Chrome WebDriver"""
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            return driver
        except Exception as e:
            print(f"Error setting up driver: {e}")
            raise
    
    def get_match_links(self, driver, match_type):
        """
        Get all JSON file links for a specific match type
        
        Args:
            driver: Selenium WebDriver instance
            match_type (str): Type of match (test, odi, t20, ipl)
            
        Returns:
            list: List of JSON file URLs
        """
        json_links = []
        
        try:
            # Navigate to matches page
            driver.get(self.matches_url)
            time.sleep(3)  # Wait for page to load
            
            # Find links based on match type
            # Cricsheet organizes matches by type in different sections
            match_type_lower = match_type.lower()
            
            # Find all links that contain the match type and end with .json
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                href = link.get_attribute("href")
                if href and match_type_lower in href.lower() and href.endswith(".json"):
                    json_links.append(href)
            
            # Also check for zip files that might contain multiple JSON files
            zip_links = []
            for link in links:
                href = link.get_attribute("href")
                if href and match_type_lower in href.lower() and href.endswith(".zip"):
                    zip_links.append(href)
            
            print(f"Found {len(json_links)} JSON links and {len(zip_links)} ZIP links for {match_type}")
            
            return json_links, zip_links
            
        except Exception as e:
            print(f"Error getting match links for {match_type}: {e}")
            return [], []
    
    def download_file(self, url, filename):
        """
        Download a file from URL
        
        Args:
            url (str): URL of the file to download
            filename (str): Local filename to save
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return False
    
    def scrape_matches(self, match_types=["test", "odi", "t20", "ipl"], max_files_per_type=50):
        """
        Scrape matches for specified match types
        
        Args:
            match_types (list): List of match types to scrape
            max_files_per_type (int): Maximum number of files to download per type
        """
        driver = self.setup_driver()
        total_downloaded = 0
        
        try:
            for match_type in match_types:
                print(f"\n{'='*50}")
                print(f"Scraping {match_type.upper()} matches...")
                print(f"{'='*50}")
                
                json_links, zip_links = self.get_match_links(driver, match_type)
                
                # Download JSON files
                downloaded_count = 0
                for i, link in enumerate(json_links[:max_files_per_type]):
                    filename = f"{match_type}_{i+1}.json"
                    if self.download_file(link, filename):
                        downloaded_count += 1
                        total_downloaded += 1
                    time.sleep(1)  # Be respectful with requests
                
                # Download ZIP files if available
                for i, link in enumerate(zip_links[:5]):  # Limit ZIP files
                    filename = f"{match_type}_archive_{i+1}.zip"
                    if self.download_file(link, filename):
                        downloaded_count += 1
                        total_downloaded += 1
                    time.sleep(2)
                
                print(f"Downloaded {downloaded_count} files for {match_type}")
                
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            driver.quit()
            print(f"\n{'='*50}")
            print(f"Scraping completed! Total files downloaded: {total_downloaded}")
            print(f"{'='*50}")
    
    def scrape_from_downloads_page(self):
        """
        Scrape download links from the cricsheet downloads page
        This method finds the actual download URLs from the website
        """
        driver = self.setup_driver()
        downloads_url = "https://cricsheet.org/downloads/"
        
        print("Navigating to downloads page...")
        
        try:
            driver.get(downloads_url)
            time.sleep(5)  # Wait for page to load
            
            # Wait for page content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            
            # Find all download links
            links = driver.find_elements(By.TAG_NAME, "a")
            
            # Dictionary to store found URLs
            match_urls = {
                "test": [],
                "odi": [],
                "t20": [],
                "ipl": []
            }
            
            print("Searching for download links...")
            
            for link in links:
                href = link.get_attribute("href")
                if href:
                    href_lower = href.lower()
                    try:
                        text = link.text.lower()
                    except:
                        text = ""
                    
                    # Check for Test matches
                    if (("test" in href_lower or "test" in text) and 
                        (".zip" in href_lower or ".json" in href_lower)):
                        match_urls["test"].append(href)
                    
                    # Check for ODI matches
                    if (("odi" in href_lower or "one-day" in text or "one day" in text) and 
                        (".zip" in href_lower or ".json" in href_lower)):
                        match_urls["odi"].append(href)
                    
                    # Check for T20 matches
                    if (("t20" in href_lower or "t20i" in href_lower or "twenty20" in text or "twenty-20" in text) and 
                        (".zip" in href_lower or ".json" in href_lower)):
                        match_urls["t20"].append(href)
                    
                    # Check for IPL matches
                    if (("ipl" in href_lower or "indian premier league" in text) and 
                        (".zip" in href_lower or ".json" in href_lower)):
                        match_urls["ipl"].append(href)
            
            # Prioritize ZIP files, but keep JSON files as backup
            final_urls = {}
            for match_type, url_list in match_urls.items():
                zip_urls = [url for url in url_list if ".zip" in url.lower()]
                json_urls = [url for url in url_list if ".json" in url.lower()]
                
                if zip_urls:
                    final_urls[match_type] = zip_urls[0]  # Use first ZIP file found
                    print(f"Found {match_type.upper()} ZIP download: {final_urls[match_type]}")
                elif json_urls:
                    print(f"Found {len(json_urls)} {match_type.upper()} JSON files (will download individually)")
                    final_urls[match_type] = json_urls  # Store list of JSON files
                else:
                    final_urls[match_type] = None
            
            driver.quit()
            
            # Download found files
            print("\nDownloading match archives...")
            for match_type, url_data in final_urls.items():
                if url_data:
                    if isinstance(url_data, list):
                        # Download individual JSON files
                        print(f"\nDownloading {len(url_data)} {match_type.upper()} JSON files...")
                        for i, url in enumerate(url_data[:100]):  # Limit to 100 files
                            filename = f"{match_type}_{i+1}.json"
                            if self.download_file(url, filename):
                                if (i + 1) % 10 == 0:
                                    print(f"Downloaded {i + 1} files...")
                            time.sleep(0.5)  # Be respectful
                    else:
                        # Download ZIP file
                        print(f"\nDownloading {match_type.upper()} matches from {url_data}...")
                        filename = f"{match_type}_matches.zip"
                        if self.download_file(url_data, filename):
                            print(f"Successfully downloaded {filename}")
                    time.sleep(2)
                else:
                    print(f"Warning: Could not find download URL for {match_type.upper()}")
            
        except Exception as e:
            print(f"Error scraping downloads page: {e}")
            driver.quit()
            raise
    
    def scrape_from_direct_urls(self):
        """
        Alternative method: Try common URL patterns
        This method tries various URL patterns that might work
        """
        # Try different URL patterns
        url_patterns = {
            "test": [
                "https://cricsheet.org/downloads/all_test_json.zip",
                "https://cricsheet.org/downloads/test_json.zip",
                "https://cricsheet.org/downloads/tests_json.zip"
            ],
            "odi": [
                "https://cricsheet.org/downloads/all_odi_json.zip",
                "https://cricsheet.org/downloads/odi_json.zip",
                "https://cricsheet.org/downloads/odis_json.zip"
            ],
            "t20": [
                "https://cricsheet.org/downloads/all_t20_json.zip",
                "https://cricsheet.org/downloads/t20_json.zip",
                "https://cricsheet.org/downloads/t20s_json.zip",
                "https://cricsheet.org/downloads/t20i_json.zip"
            ],
            "ipl": [
                "https://cricsheet.org/downloads/all_ipl_json.zip",
                "https://cricsheet.org/downloads/ipl_json.zip",
                "https://cricsheet.org/downloads/ipls_json.zip"
            ]
        }
        
        print("Trying direct URL patterns...")
        
        for match_type, urls in url_patterns.items():
            print(f"\nTrying to download {match_type.upper()} matches...")
            downloaded = False
            
            for url in urls:
                filename = f"{match_type}_matches.zip"
                try:
                    if self.download_file(url, filename):
                        print(f"Successfully downloaded {filename} from {url}")
                        downloaded = True
                        break
                except:
                    continue
            
            if not downloaded:
                print(f"Warning: Could not download {match_type.upper()} matches from any URL pattern")
                print(f"Please use scrape_from_downloads_page() method instead")
            
            time.sleep(2)


def main():
    """Main function to run the scraper"""
    scraper = CricsheetScraper(download_dir="data/raw")
    
    # Option 1: Scrape from downloads page (recommended - finds actual URLs)
    try:
        scraper.scrape_from_downloads_page()
    except Exception as e:
        print(f"Error with downloads page method: {e}")
        print("\nTrying alternative method...")
        # Option 2: Try direct URL patterns (fallback)
        scraper.scrape_from_direct_urls()
    
    # Option 3: Scrape individual matches from matches page (slower but more selective)
    # scraper.scrape_matches(match_types=["test", "odi", "t20", "ipl"], max_files_per_type=20)


if __name__ == "__main__":
    main()

