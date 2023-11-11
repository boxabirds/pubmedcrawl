import os
import sys
import re
import time
import argparse
from datetime import datetime
from pytz import timezone
from Bio import Entrez
from bs4 import BeautifulSoup

# Always tell NCBI who you are
Entrez.email = "julian.harris@gmail.com"
Entrez.tool = "PubMedCrawler for custom GPTs"

# enforces to the best of my ability the policies of the NCBI here https://www.ncbi.nlm.nih.gov/home/about/policies/
def search_and_download_articles(term, count):
    # Check the current time
    if count > 100:
        now = datetime.now(timezone('US/Eastern'))
        if now.weekday() < 5 and (now.hour < 21 and now.hour > 5):
            print("Please run this script on weekends or between 9 PM and 5 AM Eastern Time on weekdays for more than 100 requests.")
            return

    # Search the PubMed database
    handle = Entrez.esearch(db="pubmed", term=term, retmax=count)
    record = Entrez.read(handle)
    idlist = record["IdList"]

    # Fetch the articles
    for id in idlist:
        time.sleep(0.4)  # delay to ensure no more than 3 requests per second
        handle = Entrez.efetch(db="pubmed", id=id, rettype="gb", retmode="text")
        record = Entrez.read(handle)

        # Create a directory for the articles
        os.makedirs(term, exist_ok=True)

        # Parse the XML and save the articles
        soup = BeautifulSoup(record, 'xml')
        for article in soup.find_all('Article'):
            # Get the title of the article and sanitize it for use as a file name
            title = article.find('ArticleTitle').get_text()
            title = re.sub(r'[\\/:"*?<>|]', '_', title)  # replace invalid characters with underscores
            with open(f'{term}/{title}.txt', 'w') as f:
                f.write(article.get_text())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download articles from PubMed.')
    parser.add_argument('--term', type=str, default='citicoline', help='The search term.')
    parser.add_argument('--count', type=int, default=100, help='The maximum number of articles to download.')
    args = parser.parse_args()

    search_and_download_articles(args.term, args.count)
