from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

app = Flask(__name__)

@app.route('/app')
def download_file():
    file_path = 'Sodi Browser Setup 1.0.0.exe'
    return send_file(file_path, as_attachment=True)

def get_search_results(query, engine="duckduckgo"):
    headers = {"User-Agent": "Mozilla/5.0"}
    if engine == "duckduckgo":
        url = "https://duckduckgo.com/html/"
        params = {"q": query}
    elif engine == "bing":
        url = "https://www.bing.com/search"
        params = {"q": query}
    elif engine == "google":
        url = "https://www.google.com/search"
        params = {"q": query}
    else:
        raise ValueError("Engine not supported")
    
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

def extract_duckduckgo_url(redirect_url):
    """
    Extracts and decodes the actual URL from a DuckDuckGo redirect URL.
    Example redirect URL:
    //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.python.org%2F&rut=...
    """
    parsed = urlparse(redirect_url)
    # If the URL doesn't have a scheme, add "https:" by default
    if not parsed.scheme:
        redirect_url = "https:" + redirect_url
        parsed = urlparse(redirect_url)
    qs = parse_qs(parsed.query)
    if "uddg" in qs:
        return unquote(qs["uddg"][0])
    return redirect_url

def parse_results(html, engine):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    if engine == "duckduckgo":
        for result in soup.find_all("a", attrs={"class": "result__a"}):
            title = result.get_text()
            link = result.get("href")
            # Extract the actual URL from the DuckDuckGo redirect
            direct_link = extract_duckduckgo_url(link)
            results.append({"title": title, "link": direct_link})
    
    elif engine == "bing":
        for result in soup.find_all("li", {"class": "b_algo"}):
            h2 = result.find("h2")
            if h2 and h2.a:
                title = h2.a.get_text()
                link = h2.a.get("href")
                results.append({"title": title, "link": link})
    
    elif engine == "google":
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all("a")
            if anchors:
                link = anchors[0].get("href")
                title_tag = g.find("h3")
                if title_tag:
                    title = title_tag.get_text()
                    results.append({"title": title, "link": link})
    
    return results

def meta_search(query):
    engines = ["duckduckgo", "bing", "google"]
    for engine in engines:
        try:
            print("Trying on: ", engine)
            html = get_search_results(query, engine)
            results = parse_results(html, engine)
            if results:
                return results
        except Exception as e:
            print(f"Error using {engine}: {e}")
    return []

@app.route('/', methods=['GET'])
def index():
    query = request.args.get("q")
    results = None
    if query:
        results = meta_search(query)
    return render_template("index.html", results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)