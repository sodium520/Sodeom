import requests
from bs4 import BeautifulSoup
import webview
import tempfile
import os

def download_and_fix_html(url):
    # Fetch HTML from URL
    response = requests.get(url)
    html = response.text

    # Use BeautifulSoup to parse and fix links
    soup = BeautifulSoup(html, "html.parser")

    # Tags and their attributes to fix
    fix_tags = {
        "a": "href",
        "link": "href",
        "script": "src",
        "img": "src",
        "iframe": "src"
    }

    for tag, attr in fix_tags.items():
        for element in soup.find_all(tag):
            if element.has_attr(attr):
                link = element[attr]
                if not link.startswith(("http", "https", "//")):
                    # Convert relative URL to absolute
                    element[attr] = requests.compat.urljoin(url, link)

    return str(soup)

def save_and_show_html(html_content):
    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        f.write(html_content)
        temp_path = f.name

    # Show using pywebview
    webview.create_window("Game Publishers", f"file://{temp_path}")
    webview.start()

# 🔗 Your target URL
target_url = "https://abdulahdi.pythonanywhere.com/"  # Replace with any page you want

# 🧠 Workflow
html = download_and_fix_html(target_url)
save_and_show_html(html)