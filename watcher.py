# watcher.py
import requests
from bs4 import BeautifulSoup
import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()
IO_API_KEY = os.getenv("IO_API_KEY")

io_client = openai.OpenAI(
    api_key=IO_API_KEY,
    base_url="https://api.intelligence.io.solutions/api/v1/",
)

def scrape_products(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        product_pods = soup.find_all('article', class_='product_pod')
        for product in product_pods:
            title = product.h3.a['title']
            price_str = product.find('p', class_='price_color').get_text(strip=True)
            products.append({'title': title, 'price': price_str})
        return products
    except Exception as e:
        print(f"Scraping failed: {e}")
        return None

def compare_data(old_products, new_products):
    changes = {'new_products': [], 'price_changes': []}
    new_products_dict = {item['title']: item for item in new_products}
    old_products_dict = {item['title']: item for item in old_products}
    
    for title, product in new_products_dict.items():
        if title not in old_products_dict:
            changes['new_products'].append(product)
        elif product['price'] != old_products_dict[title]['price']:
            changes['price_changes'].append({'title': title, 'old_price': old_products_dict[title]['price'], 'new_price': product['price']})
    
    if not changes['new_products'] and not changes['price_changes']:
        return None
    return changes

def generate_ai_report(changes):
    prompt_content = "Recent changes on a competitor's website:\n"
    if changes['new_products']:
        prompt_content += "\nNew Products Added:\n"
        for product in changes['new_products']:
            prompt_content += f"- {product['title']} at {product['price']}\n"
    if changes['price_changes']:
        prompt_content += "\nPrice Changes:\n"
        for change in changes['price_changes']:
            prompt_content += f"- {change['title']}: Price changed from {change['old_price']} to {change['new_price']}\n"

    prompt = f"""
    You are an e-commerce strategy analyst. Provide a brief, easy-to-read summary of a competitor's recent activity.
    Be encouraging and give a brief insight into what these changes might mean. Data: {prompt_content}
    """
    try:
        response = io_client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are an e-commerce strategy analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI report failed: {e}")
        return "Could not generate an AI report due to an error."

# NEW: AI function for when no changes are detected
def generate_no_changes_report(url):
    """Generates an AI report confirming stability and offering a strategic insight."""
    prompt = f"""
    You are an e-commerce strategy analyst. You have just scanned a competitor's website at "{url}" and found NO new products or price changes.

    Write a brief, encouraging report for a business owner. Confirm that the competitor's pricing and product catalog appear stable. Then, offer one brief, creative strategic suggestion they could consider to take advantage of the competitor's stability (e.g., run a limited-time flash sale, bundle products, or highlight a unique selling proposition).
    """
    try:
        response = io_client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {"role": "system", "content": "You are an e-commerce strategy analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI 'no changes' report failed: {e}")
        return "Could not generate an AI report due to an error."


# UPDATED: The main function now generates a report even if there are no changes
def run_scan(url, datastore_file):
    """
    Runs the full scan workflow for a given URL and yields progress.
    """
    yield "STATUS: Loading previous data snapshot..."
    old_data = []
    if os.path.exists(datastore_file):
        with open(datastore_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)

    yield f"STATUS: Scraping {url} for current data..."
    new_data = scrape_products(url)
    if not new_data:
        yield "STATUS: Failed to scrape website. Aborting."
        yield "DONE"
        return

    yield "STATUS: Comparing new data with old snapshot..."
    report = None
    if not old_data:
        yield "STATUS: No previous data. Saving current snapshot as baseline."
        report = f"This is the first scan for {url}. We've saved the current products as a baseline for future comparisons."
    else:
        changes = compare_data(old_data, new_data)
        if changes:
            yield "STATUS: Changes detected! Generating AI report..."
            report = generate_ai_report(changes)
        else:
            # THIS IS THE NEW LOGIC
            yield "STATUS: No changes detected. Generating strategic summary..."
            report = generate_no_changes_report(url)
    
    if report:
        yield f"REPORT:{report}"
    
    with open(datastore_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)
    yield "STATUS: Process complete. Snapshot updated."
    yield "DONE"