"""
This module is used to scrape docs from kubernetes documentation
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor


K8S_ENGLISH_ONLY_PATTERN = re.compile(
    r'^https?://(?:www\.)?kubernetes\.io/(?!(?:[a-z]{2}(?:-[a-z]{2,4})?)(?:/|$)).*$'
)

visited = set()


def is_valid_url(url: str) -> bool:
    """
    Checks whether the url includes the correct domain
    """
    return K8S_ENGLISH_ONLY_PATTERN.match(url) is not None


def clean_text(soup):
    # remove junk elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return " ".join(soup.get_text(separator=" ").split())


def scrape_page(url: str):
    """
    Scrape the given url and return a document object in json format
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.text.strip() if soup.title else url
        text = clean_text(soup)

        document = {
                    "url": url,
                    "title": title,
                    "content": text
                    }
        return soup, document

    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return None


def crawl(start_url=os.environ["BASE_URL"], num_pages=50):
    """
    Scrapes the start url and all its internal links
    """
    queue = [start_url]
    data = []

    while queue and len(data) < num_pages:
        url = queue.pop(0)

        if url in visited:
            continue

        visited.add(url)

        print(f"[SCRAPING] {url}")
        result = scrape_page(url)

        if result:
            page_soup, page_data = result
            data.append(page_data)

            for link in page_soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])

                full_url = full_url.split('#')[0]

                if "_print" in full_url:
                    continue

                if is_valid_url(full_url) and full_url not in visited:
                    queue.append(full_url)

        time.sleep(0.5)

    return data


if __name__ == "__main__":
    docs = crawl(num_pages=100)
    print(docs[1])
    print(docs[2])