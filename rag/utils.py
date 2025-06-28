"""
Utilities Module for Petition RAG System
=======================================

This module contains utility functions for:
- Logging setup and configuration
- Input validation and sanitization
- File operations and data processing
- Common helper functions
"""

import logging
import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for a module.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def validate_input(text: str, max_length: int = 10000) -> bool:
    """
    Validate input text for safety and length.
    
    Args:
        text: Input text to validate
        max_length: Maximum allowed length
        
    Returns:
        True if valid, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    
    if len(text) > max_length:
        return False
    
    # Check for potentially harmful content
    harmful_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript protocol
        r'data:text/html',           # Data URLs
        r'vbscript:',                # VBScript
        r'on\w+\s*=',                # Event handlers
    ]
    
    for pattern in harmful_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    return True

def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing potentially harmful content.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove potentially harmful patterns
    harmful_patterns = [
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'on\w+\s*=',
    ]
    
    for pattern in harmful_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file with error handling.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Loaded JSON data
    """
    try:
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {file_path}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: str, indent: int = 2) -> bool:
    """
    Save data to JSON file with error handling.
    
    Args:
        data: Data to save
        file_path: Path to save file
        indent: JSON indentation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        
        return True
    except Exception as e:
        logging.error(f"Error saving {file_path}: {e}")
        return False

def format_timestamp(timestamp: Optional[str] = None) -> str:
    """
    Format timestamp in a consistent way.
    
    Args:
        timestamp: Optional timestamp string
        
    Returns:
        Formatted timestamp
    """
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp
    
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_case_type(text: str) -> str:
    """
    Extract case type from text using keywords.
    
    Args:
        text: Text to analyze
        
    Returns:
        Detected case type
    """
    text_lower = text.lower()
    
    case_types = {
        'criminal': ['criminal', 'bail', 'murder', 'theft', 'fraud', 'assault'],
        'civil': ['civil', 'property', 'contract', 'damages', 'injunction'],
        'family': ['family', 'divorce', 'custody', 'maintenance', 'dowry'],
        'constitutional': ['constitutional', 'writ', 'fundamental rights', 'pil'],
        'environmental': ['environmental', 'pollution', 'forest', 'wildlife'],
        'commercial': ['commercial', 'company', 'corporate', 'bankruptcy'],
        'tax': ['tax', 'income tax', 'gst', 'customs'],
        'labor': ['labor', 'employment', 'industrial', 'workman']
    }
    
    for case_type, keywords in case_types.items():
        if any(keyword in text_lower for keyword in keywords):
            return case_type
    
    return 'general'

def extract_court_name(text: str) -> str:
    """
    Extract court name from text using keywords.
    
    Args:
        text: Text to analyze
        
    Returns:
        Detected court name
    """
    text_lower = text.lower()
    
    courts = {
        'Supreme Court': ['supreme court', 'sc'],
        'High Court': ['high court', 'hc'],
        'District Court': ['district court', 'dc'],
        'Magistrate Court': ['magistrate', 'mc'],
        'Consumer Court': ['consumer', 'consumer court'],
        'Family Court': ['family court'],
        'Labor Court': ['labor court', 'industrial tribunal']
    }
    
    for court, keywords in courts.items():
        if any(keyword in text_lower for keyword in keywords):
            return court
    
    return 'High Court'  # Default

def create_petition_filename(case_type: str, court: str, timestamp: Optional[str] = None) -> str:
    """
    Create a standardized filename for petitions.
    
    Args:
        case_type: Type of case
        court: Court name
        timestamp: Optional timestamp
        
    Returns:
        Formatted filename
    """
    if not timestamp:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Clean and format components
    case_type_clean = re.sub(r'[^a-zA-Z0-9]', '_', case_type.lower())
    court_clean = re.sub(r'[^a-zA-Z0-9]', '_', court.lower())
    
    return f"petition_{case_type_clean}_{court_clean}_{timestamp}.txt"

def validate_petition_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean petition data.
    
    Args:
        data: Raw petition data
        
    Returns:
        Validated and cleaned data
    """
    validated = {}
    
    # Required fields
    required_fields = ['case_type', 'court', 'petition_text']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")
        validated[field] = str(data[field]).strip()
    
    # Optional fields with defaults
    optional_fields = {
        'details': '',
        'parties': '',
        'case_number': '',
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    for field, default in optional_fields.items():
        validated[field] = str(data.get(field, default)).strip()
    
    # Validate and sanitize text fields
    text_fields = ['petition_text', 'details', 'parties']
    for field in text_fields:
        if validated[field]:
            validated[field] = sanitize_text(validated[field])
    
    # Extract case type and court if not provided
    if not validated['case_type'] or validated['case_type'] == 'general':
        validated['case_type'] = extract_case_type(validated['petition_text'])
    
    if not validated['court'] or validated['court'] == 'High Court':
        validated['court'] = extract_court_name(validated['petition_text'])
    
    # Add metadata
    validated['generated_at'] = datetime.now().isoformat()
    validated['filename'] = create_petition_filename(
        validated['case_type'], 
        validated['court']
    )
    
    return validated

def format_petition_output(data: Dict[str, Any]) -> str:
    """
    Format petition data for output.
    
    Args:
        data: Petition data
        
    Returns:
        Formatted petition text
    """
    output = []
    
    # Header
    output.append("PETITION")
    output.append("=" * 50)
    output.append(f"Case Type: {data['case_type'].title()}")
    output.append(f"Court: {data['court']}")
    if data.get('case_number'):
        output.append(f"Case Number: {data['case_number']}")
    output.append(f"Date: {data.get('date', '')}")
    output.append("=" * 50)
    output.append("")
    
    # Parties
    if data.get('parties'):
        output.append("PARTIES:")
        output.append(data['parties'])
        output.append("")
    
    # Details
    if data.get('details'):
        output.append("CASE DETAILS:")
        output.append(data['details'])
        output.append("")
    
    # Main petition
    output.append("PETITION:")
    output.append(data['petition_text'])
    output.append("")
    
    # Footer
    output.append("-" * 50)
    output.append(f"Generated: {format_timestamp(data.get('generated_at'))}")
    output.append(f"Model: {data.get('model_used', 'Unknown')}")
    
    return "\n".join(output)

def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging.
    
    Returns:
        System information dictionary
    """
    import platform
    import sys
    
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'current_time': datetime.now().isoformat()
    }

# Example usage
if __name__ == "__main__":
    # Test utilities
    logger = setup_logging("test_utils")
    logger.info("Testing utilities module")
    
    # Test validation
    print(f"Valid input: {validate_input('Hello world')}")
    print(f"Invalid input: {validate_input('')}")
    
    # Test sanitization
    dirty_text = "<script>alert('xss')</script>Hello world"
    clean_text = sanitize_text(dirty_text)
    print(f"Sanitized: {clean_text}")
    
    # Test case type extraction
    text = "This is a criminal case about bail application"
    case_type = extract_case_type(text)
    print(f"Case type: {case_type}")
    
    # Test filename generation
    filename = create_petition_filename("criminal", "High Court")
    print(f"Filename: {filename}") 