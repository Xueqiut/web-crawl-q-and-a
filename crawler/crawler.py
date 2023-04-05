import requests
import re
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import pandas as pd
#import tiktoken
#import openai
import numpy as np
#from openai.embeddings_utils import distances_from_embeddings, cosine_similarity

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^https*://.+'

# Define root domain to crawl
domain = "openai.com"
full_url = "https://openai.com/"

# Create a class to parse the HTML and get the hyperlinks
class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        # The <a> tag defines a hyperlink. The most important attribute of the <a> element is the href attribute, which indicates the link's destination.
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])

# Function to get the hyperlinks from a URL
def find_hyperlinks(response):
    if not response.headers.get('Content-Type').startswith("text/html"):
        return []
            
    # Decode the HTML
    html = response.text

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks

# Function to validate the the hyperlinks returned from get_hyperlinks
# 1. whether the link is a valid URL
# 1. whether within the same domain
# 2. whether the link is a relative link
def validate_domain_hyperlinks(local_domain, links):
    clean_links = []
    for link in set(links):
        clean_link = None
        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc != local_domain:
                continue
            
            clean_link = link
        # If the link is not a URL, check if it is a relative link
        elif link.startswith("/"):
            clean_link = "https://" + local_domain + "/" + link[1:]
        else:
            continue
        
        # Remove the trailing slash
        if clean_link.endswith("/"):
            clean_link = clean_link[:-1]

        clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))

def get_and_write_text(response, url, f):
    # Get the text from the URL using BeautifulSoup to pull data out of HTML files
    soup = BeautifulSoup(response, "html.parser")

    # Get the text but remove the tags
    text = soup.get_text()

    # If the crawler gets to a page that requires JavaScript, it will stop the crawl
    if ("You need to enable JavaScript to run this app." in text):
        print("Unable to parse page " + url + " due to JavaScript being required")
    else:
        # Otherwise, write the text to the file in the text directory
        f.write(text)

def create_local_dir(local_domain):
    text_dir = "text/"

    # Create a directory to store the text files
    if not os.path.exists(text_dir):
        os.mkdir(text_dir)

    if not os.path.exists(text_dir + local_domain + "/"):
        os.mkdir(text_dir + local_domain + "/")

    # Create a directory to store the csv files
    if not os.path.exists("processed"):
        os.mkdir("processed")

def crawl(local_domain, url):
    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # While the queue is not empty, continue crawling
    while queue:

        # Get the next URL from the queue
        url = queue.pop()
        print(url) # for debugging and to see the progress

        links = None
        with requests.get(url) as response:
            # Save text from the url to a <url>.txt file
            with open('text/' + local_domain + '/' + url[8:].replace("/", "_") + ".txt", "w", encoding="UTF-8") as f:
                get_and_write_text(response.text, url, f)

            links = find_hyperlinks(response)

        if links is None:
            continue

        links_valid = validate_domain_hyperlinks(local_domain, links)

        # Get the embeded hyperlinks from the URL and add them to the queue
        for link in links_valid:
            if link not in seen:
                queue.append(link)
                seen.add(link)

def main(full_url):
    # Parse the URL and get the domain
    local_domain = urlparse(full_url).netloc

    # Create the local directory to store the text files
    create_local_dir(local_domain)

    crawl(local_domain, full_url)