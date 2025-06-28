"""
Indian Kanoon Dual RAG Pipeline
==============================

Fetches batches of cases from Indian Kanoon API, processes each case for structure and content RAG, and saves results batchwise.
"""

import os
import time
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- CONFIG ---
BATCH_SIZE = 5
API_SLEEP = 2  # seconds between API calls
STRUCTURE_DIR = "rag_ready/structure/"
CONTENT_DIR = "rag_ready/content/"

# --- SETUP ---
os.makedirs(STRUCTURE_DIR, exist_ok=True)
os.makedirs(CONTENT_DIR, exist_ok=True)

logger = logging.getLogger("dual_rag_pipeline")
logging.basicConfig(level=logging.INFO)

# --- API CLIENT ---
class IndianKanoonAPI:
    def __init__(self, api_key: Optional[str] = None):
        import requests
        self.session = requests.Session()
        self.base_url = "https://api.indiankanoon.org"
        self.session.headers.update({
            'User-Agent': 'Legal-AI-Collector/1.0',
            'Accept': 'application/json'
        })
        if api_key:
            self.session.headers['Authorization'] = f'Token {api_key}'

    def search_cases(self, query: str, maxpages: int = 1) -> List[Dict[str, Any]]:
        import urllib.parse
        params = {'formInput': query, 'pagenum': 0, 'maxpages': maxpages, 'format': 'json'}
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/search/?{query_string}"
        logger.info(f"Making POST request to {url}")
        try:
            resp = self.session.post(url)
            logger.info(f"Request method: {resp.request.method}, URL: {resp.request.url}")
            resp.raise_for_status()
            data = resp.json()
            return data.get('docs', [])
        except Exception as e:
            logger.error(f"API search error: {e}")
            return []

    def get_case_details(self, case_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.session.get(f"{self.base_url}/doc/{case_id}")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"API detail error for {case_id}: {e}")
            return None

# --- DUAL RAG PROCESSING ---
def process_structure_rag(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structure-focused RAG info from case data."""
    content = case_data.get('content', '')
    import re
    headers = re.findall(r'([A-Z][A-Z\s]+:)', content)
    legal_phrases = [
        phrase for phrase in [
            'IN THE HIGH COURT OF', 'IN THE SUPREME COURT OF INDIA', 'COMES NOW',
            'WHEREFORE', 'PRAYED FOR', 'RESPECTFULLY SUBMITS', 'MAY IT PLEASE THE COURT'
        ] if phrase in content
    ]
    court = case_data.get('court', '')
    return {
        'case_id': case_data.get('id'),
        'title': case_data.get('title', ''),
        'court': court,
        'date': case_data.get('date', ''),
        'headers': headers,
        'legal_phrases': legal_phrases,
        'citations': case_data.get('citations', [])
    }

def process_content_rag(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract content-focused RAG info from case data."""
    content = case_data.get('content', '')
    import re
    def extract_section(name):
        match = re.search(rf'{name}:\s*(.*?)(?=\n[A-Z][A-Z\s]+:|$)', content, re.DOTALL)
        return match.group(1).strip() if match else ''
    parties = re.findall(r'(Petitioner|Respondent|Appellant|Defendant|Plaintiff)[:\s]+([^\n]+)', content)
    precedents = re.findall(r'(\d{4})\s+(\d+)\s+([A-Z]+)\s+(\d+)', content)
    return {
        'case_id': case_data.get('id'),
        'facts': extract_section('FACTS'),
        'grounds': extract_section('GROUNDS'),
        'relief': extract_section('RELIEF'),
        'arguments': extract_section('ARGUMENTS'),
        'conclusion': extract_section('CONCLUSION'),
        'parties': [f"{p[0]}: {p[1]}" for p in parties],
        'precedents': [' '.join(p) for p in precedents]
    }

# --- MAIN PIPELINE ---
def fetch_and_process_batches(api_key: Optional[str] = None, queries: List[str] = None, max_batches: int = 10):
    api = IndianKanoonAPI(api_key)
    batch_num = 0
    queries = queries or ["contract dispute", "criminal appeal", "public interest", "writ petition", "consumer protection"]
    for query in queries:
        logger.info(f"Query: {query}")
        search_results = api.search_cases(query, maxpages=BATCH_SIZE)
        if not search_results:
            continue
        structure_batch = []
        content_batch = []
        for result in search_results:
            case_id = result.get('id')
            if not case_id:
                continue
            case_data = api.get_case_details(case_id)
            if not case_data:
                continue
            structure = process_structure_rag(case_data)
            content = process_content_rag(case_data)
            structure_batch.append(structure)
            content_batch.append(content)
            logger.info(f"Processed case {case_id}")
            time.sleep(API_SLEEP)
        # Save batch
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f"{STRUCTURE_DIR}structure_batch_{batch_num}_{ts}.json", 'w', encoding='utf-8') as f:
            json.dump(structure_batch, f, ensure_ascii=False, indent=2)
        with open(f"{CONTENT_DIR}content_batch_{batch_num}_{ts}.json", 'w', encoding='utf-8') as f:
            json.dump(content_batch, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved batch {batch_num} ({len(structure_batch)} cases)")
        batch_num += 1
        if batch_num >= max_batches:
            break
        time.sleep(API_SLEEP * 2)

if __name__ == "__main__":
    # Optionally set your API key here
    API_KEY = os.environ.get("INDIAN_KANOON_API_KEY", None)
    fetch_and_process_batches(api_key=API_KEY, max_batches=10) 