"""
Indian Kanoon Data Collector using Official IKApi
================================================

Uses the official Indian Kanoon API client to collect legal documents
and integrate them with the LangGraph petition system.
"""

import os
import json
import logging
import argparse
import time
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import the official IKApi class
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ikapi_2 import IKApi, FileStorage

logger = logging.getLogger("ik_collector")
logging.basicConfig(level=logging.INFO)

class IndianKanoonCollector:
    def __init__(self, api_token: str, data_dir: str = "collected_data", 
                 batch_size: int = 5, delay_between_batches: int = 10,
                 max_retries: int = 3):
        """Initialize the collector with API token and data directory."""
        self.api_token = api_token
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
        self.max_retries = max_retries
        
        os.makedirs(data_dir, exist_ok=True)
        
        # Create args object for IKApi
        self.args = self._create_args()
        self.storage = FileStorage(data_dir)
        self.api = IKApi(self.args, self.storage)
        
    def _create_args(self):
        """Create args object for IKApi initialization."""
        class Args:
            def __init__(self, token, datadir):
                self.token = token
                self.datadir = datadir
                self.maxcites = 0
                self.maxcitedby = 0
                self.orig = False
                self.maxpages = 1  # Process one page at a time for better control
                self.pathbysrc = False
                self.numworkers = 1  # Single worker for better rate limiting
                self.addedtoday = False
                self.fromdate = None
                self.todate = None
                self.sortby = None
        
        return Args(self.api_token, self.data_dir)
    
    def _exponential_backoff(self, attempt: int, base_delay: float = 2.0) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
        return min(delay, 60)  # Cap at 60 seconds
    
    def _safe_api_call(self, func, *args, **kwargs):
        """Execute API call with retry logic and exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                # Add small delay after successful call
                time.sleep(random.uniform(1, 3))
                return result
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"API call failed after {self.max_retries} attempts")
                    raise
    
    def search_and_collect_batched(self, queries: List[str], max_pages: int = 5) -> List[str]:
        """Search for documents using batched approach with proper rate limiting."""
        collected_docids = []
        total_queries = len(queries)
        
        for i, query in enumerate(queries):
            logger.info(f"Processing query {i+1}/{total_queries}: {query}")
            
            try:
                # Process in smaller batches
                for page in range(max_pages):
                    logger.info(f"  Processing page {page+1}/{max_pages} for query: {query}")
                    
                    # Update maxpages for this specific call
                    self.args.maxpages = 1
                    
                    # Use safe API call with retry logic
                    docids = self._safe_api_call(self.api.save_search_results, query)
                    
                    if docids:
                        collected_docids.extend(docids)
                        logger.info(f"  Collected {len(docids)} documents from page {page+1}")
                    else:
                        logger.info(f"  No more documents found on page {page+1}")
                        break
                    
                    # Delay between pages
                    if page < max_pages - 1:
                        delay = random.uniform(3, 7)
                        logger.info(f"  Waiting {delay:.1f} seconds before next page...")
                        time.sleep(delay)
                
                # Delay between queries
                if i < total_queries - 1:
                    delay = self.delay_between_batches + random.uniform(0, 5)
                    logger.info(f"Completed query {i+1}/{total_queries}. Waiting {delay:.1f} seconds before next query...")
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                continue
        
        return collected_docids
    
    def collect_by_doctype_batched(self, doctypes: List[str]) -> List[str]:
        """Collect documents by document type with batching."""
        collected_docids = []
        total_doctypes = len(doctypes)
        
        for i, doctype in enumerate(doctypes):
            logger.info(f"Processing doctype {i+1}/{total_doctypes}: {doctype}")
            
            try:
                # Use safe API call with retry logic
                docids = self._safe_api_call(self.api.download_doctype, doctype)
                collected_docids.extend(docids)
                logger.info(f"Collected {len(docids)} documents of type: {doctype}")
                
                # Delay between doctypes
                if i < total_doctypes - 1:
                    delay = self.delay_between_batches + random.uniform(0, 5)
                    logger.info(f"Waiting {delay:.1f} seconds before next doctype...")
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error collecting doctype '{doctype}': {e}")
                continue
        
        return collected_docids
    
    def search_and_collect(self, queries: List[str], max_pages: int = 5) -> List[str]:
        """Legacy method - now calls the batched version."""
        return self.search_and_collect_batched(queries, max_pages)
    
    def collect_by_doctype(self, doctypes: List[str]) -> List[str]:
        """Legacy method - now calls the batched version."""
        return self.collect_by_doctype_batched(doctypes)
    
    def process_collected_data(self) -> Dict[str, Any]:
        """Process the collected data for RAG system."""
        processed_data = {
            'structure_data': [],
            'content_data': [],
            'metadata': {
                'collection_date': datetime.now().isoformat(),
                'total_documents': 0,
                'data_dir': self.data_dir
            }
        }
        
        # Walk through collected data directory
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            doc_data = json.load(f)
                        
                        # Extract structure data
                        structure_data = self._extract_structure_data(doc_data)
                        if structure_data:
                            processed_data['structure_data'].append(structure_data)
                        
                        # Extract content data
                        content_data = self._extract_content_data(doc_data)
                        if content_data:
                            processed_data['content_data'].append(content_data)
                        
                        processed_data['metadata']['total_documents'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing {filepath}: {e}")
                        continue
        
        return processed_data
    
    def _extract_structure_data(self, doc_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structure-focused data from document."""
        try:
            return {
                'docid': doc_data.get('tid'),
                'title': doc_data.get('title', ''),
                'court': doc_data.get('docsource', ''),
                'date': doc_data.get('publishdate', ''),
                'citations': doc_data.get('citeList', []),
                'cited_by': doc_data.get('citedbyList', []),
                'docsize': doc_data.get('docsize', 0)
            }
        except Exception as e:
            logger.error(f"Error extracting structure data: {e}")
            return None
    
    def _extract_content_data(self, doc_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract content-focused data from document."""
        try:
            content = doc_data.get('doc', '')
            if not content:
                return None
            
            # Extract key sections (this is a simplified version)
            sections = {
                'facts': self._extract_section(content, ['FACTS', 'BACKGROUND']),
                'arguments': self._extract_section(content, ['ARGUMENTS', 'CONTENTIONS']),
                'judgment': self._extract_section(content, ['JUDGMENT', 'HELD', 'CONCLUSION']),
                'relief': self._extract_section(content, ['RELIEF', 'ORDER']),
                'full_content': content[:5000]  # First 5000 chars for context
            }
            
            return {
                'docid': doc_data.get('tid'),
                'title': doc_data.get('title', ''),
                'sections': sections,
                'keywords': self._extract_keywords(content)
            }
        except Exception as e:
            logger.error(f"Error extracting content data: {e}")
            return None
    
    def _extract_section(self, content: str, section_names: List[str]) -> str:
        """Extract a specific section from document content."""
        import re
        for section_name in section_names:
            pattern = rf'{section_name}[:.\s]*(.*?)(?=\n[A-Z][A-Z\s]+:|$)'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        import re
        # Simple keyword extraction - can be enhanced
        words = re.findall(r'\b[A-Z][a-z]+\b', content)
        return list(set(words))[:20]  # Top 20 unique capitalized words
    
    def save_processed_data(self, processed_data: Dict[str, Any], filename: str = None):
        """Save processed data to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"processed_data_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved processed data to: {filepath}")
        return filepath

def main():
    """Main function to run the collector."""
    parser = argparse.ArgumentParser(description='Collect data from Indian Kanoon API')
    parser.add_argument('--token', required=True, help='Indian Kanoon API token')
    parser.add_argument('--data-dir', default='collected_data', help='Data directory')
    parser.add_argument('--queries', nargs='+', help='Search queries')
    parser.add_argument('--doctypes', nargs='+', help='Document types to collect')
    parser.add_argument('--max-pages', type=int, default=5, help='Maximum pages per query')
    parser.add_argument('--batch-size', type=int, default=5, help='Batch size for processing')
    parser.add_argument('--delay-between-batches', type=int, default=10, help='Delay between batches (seconds)')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximum retries for failed API calls')
    
    args = parser.parse_args()
    
    # Initialize collector with batching parameters
    collector = IndianKanoonCollector(
        args.token, 
        args.data_dir,
        batch_size=args.batch_size,
        delay_between_batches=args.delay_between_batches,
        max_retries=args.max_retries
    )
    
    collected_docids = []
    
    # Collect by queries
    if args.queries:
        logger.info(f"Collecting documents for queries: {args.queries}")
        collected_docids.extend(collector.search_and_collect_batched(args.queries, args.max_pages))
    
    # Collect by doctypes
    if args.doctypes:
        logger.info(f"Collecting documents by types: {args.doctypes}")
        collected_docids.extend(collector.collect_by_doctype_batched(args.doctypes))
    
    logger.info(f"Total documents collected: {len(collected_docids)}")
    
    # Process collected data
    if collected_docids:
        logger.info("Processing collected data...")
        processed_data = collector.process_collected_data()
        collector.save_processed_data(processed_data)
        
        logger.info(f"Processing complete. Structure data: {len(processed_data['structure_data'])}, "
                   f"Content data: {len(processed_data['content_data'])}")

if __name__ == "__main__":
    main() 