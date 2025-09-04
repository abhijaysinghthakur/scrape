from flask import Flask, jsonify, render_template, Response, request
import json
import os
import time
from watcher import run_scan
import requests
from bs4 import BeautifulSoup
from googlesearch import search

app = Flask(__name__)
COMPETITORS_FILE = 'competitors.json'

# --- Helper Functions (get_competitors, save_competitors) ---
def get_competitors():
    if not os.path.exists(COMPETITORS_FILE): return []
    try:
        with open(COMPETITORS_FILE, 'r') as f: return json.load(f)
    except json.JSONDecodeError: return []

def save_competitors(competitors):
    with open(COMPETITORS_FILE, 'w') as f: json.dump(competitors, f, indent=4)

# --- Page Routes (home, show_scan_result_page) ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan-result/<int:competitor_id>')
def show_scan_result_page(competitor_id):
    competitor = next((c for c in get_competitors() if c.get('id') == competitor_id), None)
    if not competitor: return "Competitor not found.", 404
    return render_template('scan_result.html', competitor=competitor)

# --- API Routes ---
@app.route('/api/competitors', methods=['GET', 'POST'])
def api_manage_competitors():
    if request.method == 'POST':
        competitors = get_competitors()
        max_id = max([c.get('id', 0) for c in competitors]) if competitors else 0
        competitors.append({"id": max_id + 1, "url": request.get_json().get('url')})
        save_competitors(competitors)
    return jsonify(get_competitors())

@app.route('/api/competitors/<int:competitor_id>', methods=['DELETE'])
def api_delete_competitor(competitor_id):
    competitors = get_competitors()
    updated_competitors = [c for c in competitors if c.get('id') != competitor_id]
    save_competitors(updated_competitors)
    return jsonify({"success": True})

@app.route('/api/suggest-competitors', methods=['POST'])
def suggest_competitors():
    user_url = request.get_json().get('url')
    if not user_url: return jsonify({"error": "User URL is required."}), 400

    try:
        # 1. Scrape user's site for keywords from the page title
        print(f"Scraping {user_url} for keywords...")
        response = requests.get(user_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ''
        search_query = f"online stores like '{title}'"
        
        # 2. Search Google for competitors
        print(f"Searching Google for: {search_query}")
        suggestions = [url for url in search(search_query, num_results=5, lang="en")]
        
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        print(f"Error during suggestion: {e}")
        return jsonify({"error": "Could not generate suggestions for this URL."}), 500

@app.route('/api/stream-scan/<int:competitor_id>')
def stream_scan(competitor_id):
    competitor = next((c for c in get_competitors() if c.get('id') == competitor_id), None)
    if not competitor: return Response("data: STATUS: Competitor not found.\n\ndata: DONE\n\n", mimetype='text/event-stream')
    
    datastore_file = f"datastore_{competitor_id}.json"
    def generate():
        for update in run_scan(competitor['url'], datastore_file):
            yield f"data: {update.replace('\n', '|||')}\n\n"
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5002)