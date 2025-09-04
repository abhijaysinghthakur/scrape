# 🚀 Competitor Watch Agent

A full-stack application featuring an autonomous AI agent that provides strategic intelligence to e-commerce businesses by monitoring their competitors and suggesting new ones.

## The Problem
Small e-commerce businesses operate in a highly competitive market but lack the resources to constantly track competitors or discover new ones. They often miss critical changes and strategic opportunities.

## The Solution
This agent provides a complete dashboard for competitor intelligence:
1.  **Proactive Suggestions:** The agent can analyze a user's own store URL to proactively suggest relevant competitors to track.
2.  **Automated Monitoring:** It scrapes competitor websites for product and pricing data, comparing it against historical snapshots to detect changes.
3.  **AI-Powered Reporting:** It uses the **IO Intelligence API** to synthesize raw data into professional reports, providing strategic insights on competitor activity.
4.  **Interactive UI:** A clean, multi-page web application allows users to manage their list, trigger scans, and view live progress updates.

## How it Uses IO Intelligence
The intelligence of this agent is powered by the **IO Intelligence Models API**. It uses the `meta-llama/Llama-3.3-70B-Instruct` model to transform raw data (lists of product changes) into professional, easy-to-read reports. This gives the user not just data, but actionable insights, demonstrating a powerful real-world application of AI in a strategic business context.

## Tech Stack
* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, Vanilla JavaScript
* **Core AI:** IO Intelligence API
* **Data Sources:** Google Search (via `googlesearch-python`)
* **Web Scraping:** Requests, BeautifulSoup