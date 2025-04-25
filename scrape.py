import cloudscraper
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
from googletrans import Translator
import mimetypes
import time
import random
from requests.exceptions import RequestException

def create_scraper():
    return cloudscraper.create_scraper(browser='chrome', delay=10)

def download_file(url, directory, scraper):
    try:
        response = scraper.get(url, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            extension = mimetypes.guess_extension(content_type) or ''
            if not extension and url.lower().endswith('.pdf'):
                extension = '.pdf'
            filename = os.path.join(directory, os.path.basename(url) + extension)
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return f"Downloaded: {filename}"
    except Exception as e:
        return f"Failed to download {url}: {str(e)}"

def extract_text_links_and_files(url, base_domain, visited_urls, media_directory, scraper):
    try:
        if url in visited_urls:
            return "", [], []

        visited_urls.add(url)

        response = scraper.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            text = soup.get_text(separator='\n', strip=True)
            
            links = []
            for a_tag in soup.find_all('a', href=True):
                link = urljoin(url, a_tag['href'])
                if urlparse(link).netloc == base_domain:
                    links.append(link)
            
            files_to_download = []
            for tag in soup.find_all(['img', 'a']):
                src = tag.get('src') or tag.get('href')
                if src:
                    file_url = urljoin(url, src)
                    if file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf')):
                        files_to_download.append(file_url)
            
            return text, links, files_to_download
        else:
            print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")
            return "", [], []
    except RequestException as e:
        print(f"Network error occurred while accessing {url}: {str(e)}")
        return "", [], []
    except Exception as e:
        print(f"An unexpected error occurred while processing {url}: {str(e)}")
        return "", [], []

def recursive_extract(url, base_domain, visited_urls, media_directory, scraper, max_depth=5):
    if max_depth == 0:
        return ""

    text, links, files_to_download = extract_text_links_and_files(url, base_domain, visited_urls, media_directory, scraper)
    
    for file_url in files_to_download:
        download_file(file_url, media_directory, scraper)
        time.sleep(random.uniform(1, 3))  # Random delay between downloads
    
    for link in links:
        if link not in visited_urls:
            text += "\n\n" + recursive_extract(link, base_domain, visited_urls, media_directory, scraper, max_depth - 1)
            time.sleep(random.uniform(1, 3))  # Random delay between page visits
    
    return text

def translate_text(text, dest='en'):
    translator = Translator()
    try:
        chunks = [text[i:i+5000] for i in range(0, len(text), 5000)]
        translated_chunks = []
        for chunk in chunks:
            translated = translator.translate(chunk, dest=dest)
            translated_chunks.append(translated.text)
            time.sleep(random.uniform(1, 3))  # Random delay between translations
        return ' '.join(translated_chunks)
    except Exception as e:
        return f"Translation failed: {str(e)}\n\nOriginal text:\n{text}"

def save_text_to_file(text, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

# List of websites to extract text from
urls = [
    'https://iiitn.ac.in/'
    # Add more URLs here
]

# Directory to store the text files and media
output_directory = "extracted_data"
os.makedirs(output_directory, exist_ok=True)

scraper = create_scraper()

for url in urls:
    base_domain = urlparse(url).netloc
    visited_urls = set()
    
    media_directory = os.path.join(output_directory, f"{base_domain}_media")
    os.makedirs(media_directory, exist_ok=True)
    
    print(f"Extracting text and downloading files from {url} and its sub-links...")
    text = recursive_extract(url, base_domain, visited_urls, media_directory, scraper)
    
    print(f"Extraction complete. Translating text to English...")
    translated_text = translate_text(text)
    
    filepath = os.path.join(output_directory, f"{base_domain}_translated.txt")
    save_text_to_file(translated_text, filepath)

    print(f"Text from {url} and its sub-links has been translated and saved to {filepath}")
    print(f"Media files and PDFs have been downloaded to {media_directory}")