import csv
import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import JavascriptException
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from webdriver_manager.chrome import ChromeDriverManager
import subprocess

# ANSI escape codes for colors and styles
class Style:
    GREEN = '\033[92m'
    PINK = '\033[95m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'
    CLEAR_LINE = '\033[K'

if len(sys.argv) != 3:
    print("Usage: python crawl.py [domain] [max_urls]")
    sys.exit(1)

domain = sys.argv[1]
max_urls = int(sys.argv[2])
visited_urls_file = "visited_urls.txt"

# Use a persistent set for visited URLs, handling missing files
visited_urls = set()
try:
    with open(visited_urls_file, "r") as file:  # Load previously visited URLs
        visited_urls.update(file.read().splitlines())
except FileNotFoundError:
    with open(visited_urls_file, "w") as file:  # Create the file if it doesn't exist
        pass  # Leave the file empty for now

results = []  # Store the results of the heading checks
crawled_count = 0  # Initialize the crawled URL count

def check_headings(driver):
    errors = []
    headings = driver.find_elements(By.XPATH, "//h1|//h2|//h3|//h4|//h5|//h6")
    
    if not headings:
        errors.append("No Headings")
        return "Fail: " + ", ".join(errors)

    heading_tags = [h.tag_name for h in headings]
    
    if heading_tags.count('h1') > 1:
        errors.append("Multiple H1 Tags")
    if 'h1' not in heading_tags:
        errors.append("No H1 Tag")
    
    last_level = 0
    for tag in heading_tags:
        tag_level = int(tag[1])
        if tag_level > last_level + 1:
            errors.append("Improper Heading Order")
            break
        last_level = tag_level

    if errors:
        return "Fail: " + ", ".join(errors)
    return "Pass"

def normalize_url(url):
    parsed_url = urlparse(url)
    url_without_fragment = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
    normalized_url = url_without_fragment.lower().rstrip("/")
    return normalized_url

def get_base_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def crawl_page(url, driver, base_domain):
    global crawled_count  # Use the global counter
    if crawled_count >= max_urls:
        return  # Stop crawling if the max_urls limit is reached

    normalized_url = normalize_url(url)
    print(f"\r{Style.GREEN}{Style.BOLD}Crawling page: {Style.PINK}({crawled_count+1}/{Style.PINK}{max_urls}){Style.END} {Style.END}{Style.BOLD}{normalized_url}{Style.END}{Style.CLEAR_LINE}", end='')

    if normalized_url in visited_urls:
        print(f"URL already visited: {normalized_url}")
        return

    driver.get(url)

    # Check the status code using JavaScript
    try:
        status_code = driver.execute_script("""
            var xhr = new XMLHttpRequest();
            xhr.open('GET', arguments[0], false);
            xhr.send(null);
            return xhr.status;
        """, url)
    except JavascriptException:
        print(f"Failed to retrieve status code for: {url}")
        return

    if status_code != 200:
        print(f"URL returned status code {status_code}, skipping: {normalized_url}")
        return  # Skip this URL as it didn't return a 200 status

    challenge_elements = driver.find_elements(By.ID, "challenge-form")
    if challenge_elements:
        print(f"\n{Style.BOLD}Cloudflare challenge detected, skipping page:{Style.END} {normalized_url}")
        return  # Skip further processing for this URL

    result = check_headings(driver)  # Check the heading hierarchy
    results.append([normalized_url, result])  # Append the results
    visited_urls.add(normalized_url)  # Add the URL to the visited set
    crawled_count += 1  # Increment the crawled URL count
    
    if crawled_count >= max_urls:
        return  # Stop crawling if the max_urls limit is reached

    with open(visited_urls_file, "a") as file:
        file.write(normalized_url + "\n")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]

    for link in links:
        absolute_link = urljoin(url, link)
        normalized_link = normalize_url(absolute_link)
        if get_base_domain(normalized_link) == base_domain and normalized_link not in visited_urls:
            crawl_page(normalized_link, driver, base_domain)  # Recursively crawl linked pages

def crawl_site(url, max_urls):
    base_domain = get_base_domain(url)  # Get the base domain of the starting URL

    caffeinate_process = subprocess.Popen(['caffeinate'])

    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)

    try:
        crawl_page(url, driver, base_domain)
    finally:
        driver.quit()  # Ensure the driver is closed even if an error occurs
        caffeinate_process.terminate()  # Terminate caffeinate process

    # Writing results to CSV after crawling is finished
    results_file_name = f"{domain}_results.csv"
    with open(results_file_name, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['URL', 'Result'])
        csvwriter.writerows(results)

    # Delete the visited_urls.txt file
    if os.path.exists(visited_urls_file):
        os.remove(visited_urls_file)

    print(f"\n{Style.BLUE}{Style.BOLD}Crawl Complete!{Style.END}")

# Start crawling
start_url = f"https://{domain}"  # Construct the start URL
crawl_site(start_url, max_urls)
