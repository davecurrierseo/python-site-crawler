# Web Crawler

## Overview
This script is a Python-based web crawler designed to navigate through websites, starting from a given domain.

This particular crawler systematically checks each page for proper heading hierarchy and records the results, but can easily be modified for your particular use case. The crawler respects a maximum number of URLs to visit, preventing excessive load on the server and ensuring a focused crawl.

### Features
- **Headings Validation**: Checks for multiple H1 tags, absence of H1 tags, and proper sequential order of headings (H1, H2, H3, etc.).
- **Visited URL Tracking**: Maintains a list of visited URLs to avoid revisiting the same page.
- **Cloudflare Challenge Detection**: Detects and skips pages protected by Cloudflare challenges to ensure smooth operation.
- **Configurable Crawl Limit**: Limits the number of pages to crawl, as specified by the user.
- **Persistent State**: Remembers visited URLs between script runs to prevent redundant visits.
- **Headless Browser**: Utilizes a headless Chrome browser for seamless background operation.
- **Session Persistence**: Keeps the system awake during the crawl process to prevent interruptions.

## Requirements
- Python 3.x
- Selenium WebDriver
- BeautifulSoup4
- ChromeDriverManager
- WebDriver-Manager
- CSV module (built-in)
- Sys module (built-in)
- OS module (built-in)
- Urllib.parse module (built-in)
- Subprocess module (built-in)

## Installation
1. **Python**: Ensure Python 3.x is installed on your system.
2. **Dependencies**: Install the required Python packages by running:
   ```bash
   pip install selenium beautifulsoup4 webdriver-manager
   ```

## Usage
To run the script, use the command line to navigate to the script's directory and execute the following command:

```bash
python crawl.py [domain] [max_urls]
```

- `[domain]`: The starting domain for the crawl (e.g., `example.com`).
- `[max_urls]`: The maximum number of URLs to crawl.

Example:
```bash
python crawl.py example.com 50
```

### Important Notes
- **Domain Input**: Do not include 'http://' or 'https://' in the domain input.
- **Max URLs**: The `max_urls` parameter limits the scope of the crawl to avoid overloading servers and to keep the crawl focused.

## Output
The script will generate the following outputs:
- **Console Logs**: Displays the progress of the crawl in the terminal.
- **Results File**: A CSV file named `[domain]_results.csv` containing the URL and the heading check result for each crawled page.
- **Visited URLs File**: A text file named `visited_urls.txt` that records visited URLs. This file is deleted after the crawl is complete to reset the state for the next run.

## Contribution
Contributions to improve the script or add new features are welcome. Please follow standard coding conventions and provide documentation for your changes.

## License
This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).

---
*Please ensure you comply with the terms of service and robots.txt of the websites you crawl. Happy crawling!*
