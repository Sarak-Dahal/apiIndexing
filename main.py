# Import necessary libraries
import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Title of the App
st.title("Google SEO Indexing and Checker Tool")

# Sidebar
st.sidebar.header("Enter Details Here:")
urls_input = st.sidebar.text_area('Enter your URL(s) here (one per line):')
json_key_file = st.sidebar.file_uploader("Upload your Google JSON key file:", type='json')

# JSON key data
json_key_data = json.loads(json_key_file.getvalue().decode('utf-8')) if json_key_file else None

#json_key_data = json_key_file.getvalue() if json_key_file else None

# Get URLs
urls = urls_input.split('\n') if urls_input else []

# Function to check SEO best practices
def check_seo(url):
    # Check if url scheme is present
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    st.markdown(f"### SEO Results for {url}")

    # Get the webpage content
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check for title tag
    title = soup.find('title')
    if title is None:
        st.markdown('- ❌ **Title:** No title tag found.')
    else:
        st.markdown(f'- ✅ **Title:** {title.string}')

    # Check for meta description
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description is None:
        st.markdown('- ❌ **Meta Description:** No meta description found.')
    else:
        st.markdown(f'- ✅ **Meta Description:** {meta_description["content"]}')

    # Check for h1 tag and count them
    h1_tags = soup.find_all('h1')
    if not h1_tags:
        st.markdown('- ❌ **H1 Tags:** No h1 tag found.')
    else:
        st.markdown(f'- ✅ **H1 Tags:** Found {len(h1_tags)} H1 tags.')

    # Check for alt attributes in images
    images = soup.find_all('img')
    if images:
        alt_images = [img for img in images if img.has_attr('alt') and img['alt'].strip() != '']
        st.markdown(f'- ✅ **Images with ALT:** {len(alt_images)} out of {len(images)} images have alt attributes.')
    else:
        st.markdown('- ❌ **Images:** No images found.')

    # Check for robots.txt
    robot_url = url + "/robots.txt"
    response = requests.get(robot_url)
    if response.status_code == 200:
        st.markdown(f'- ✅ **Robots.txt:** Robots.txt file exists.')
    else:
        st.markdown('- ❌ **Robots.txt:** No Robots.txt file found.')

def index_url(credentials, url):
    # Check if url scheme is present
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    # Build the service
    service = build('indexing', 'v3', credentials=credentials)
    url_notification_metadata = {
        'url': url,
        'type': 'URL_UPDATED'
    }
    # Execute the request
    response = service.urlNotifications().publish(body=url_notification_metadata).execute()
    return response


if urls and json_key_data:
    credentials = Credentials.from_service_account_info(json_key_data)

    # Sidebar for license key
    license_key = st.sidebar.text_input('Enter your license key here:')
    if license_key:
        index_results = []
        for url in urls:
            # Check SEO
            check_seo(url)

            # Index URL
            response = index_url(credentials, url)
            index_results.append(response)
        st.markdown(f"### Indexing Results")
        st.write(index_results)
    else:
        st.sidebar.error("Please enter your license key.")
else:

    if not json_key_data:
        st.sidebar.error("Please upload your Google JSON key file.")
    if not urls:
        st.sidebar.error("Please enter at least one URL.")
