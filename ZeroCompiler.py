import json
import logging
import requests  # Changed from openai to requests
import tiktoken
from typing import Dict, List, Optional, Union
import re
import time
from datetime import datetime
import hashlib

class ZeroCompiler:
    """
    ZeroCompiler - LLM-powered Report Generator for ZeroNet
    Now using OpenRouter API with meta-llama/llama-4-maverick:free
    """

    def __init__(self, 
                 raw_file="raw.json",
                 reports_file="reports.json",
                 model="meta-llama/llama-4-maverick:free",  # Updated model
                 api_key=None,  # OpenRouter API key
                 max_tokens_per_chunk=3000,
                 max_response_tokens=1000):

        self.raw_file = raw_file
        self.reports_file = reports_file
        self.model = model
        self.api_key = api_key
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.max_response_tokens = max_response_tokens
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Fallback tokenizer
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Processing state
        self.current_query = ""
        self.processed_chunks = []
        self.individual_reports = []
        self.final_report = ""

        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger('ZeroCompiler')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroCompiler] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _count_tokens(self, text: str) -> int:
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            return len(text) // 4

    def _chunk_content(self, content: Dict[str, Dict]) -> List[Dict]:
        # ... (same as before) ...
    
    def _call_openrouter(self, messages: List[Dict], max_tokens: int) -> Optional[str]:
        if not self.api_key:
            self.logger.warning("No API key - running in simulation mode")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            self.logger.error(f"API call failed: {e}")
            return None

    def _generate_chunk_report(self, chunk: Dict, query: str) -> Optional[str]:
        prompt = f"""Based on the following web content, provide a comprehensive analysis that addresses: "{query}"\n\nContent:\n{chunk['combined_text']}"""
        
        messages = [
            {"role": "system", "content": "You are an expert analyst creating reports from web content."},
            {"role": "user", "content": prompt}
        ]
        
        # Try real API first
        response = self._call_openrouter(messages, self.max_response_tokens)
        if response:
            return response
        
        # Fallback to mock
        return self._generate_mock_report(chunk, query)

    def _generate_mock_report(self, chunk: Dict, query: str) -> str:
        # ... (updated to be more generic) ...
        return f"Analysis of {len(chunk['urls'])} sources for '{query}': Found relevant information..."

    def _synthesize_final_report(self, individual_reports: List[str], query: str) -> str:
        combined = "\n\n".join([f"## Report Section {i+1} ##\n{r}" for i, r in enumerate(individual_reports)])
        
        messages = [
            {"role": "system", "content": "Synthesize these reports into a comprehensive final report"},
            {"role": "user", "content": f"Query: {query}\n\nReports:\n{combined}"}
        ]
        
        response = self._call_openrouter(messages, self.max_response_tokens * 2)
        return response or self._generate_mock_synthesis(individual_reports, query)

    # ... (rest of methods same as before with minor tweaks) ...

    def compile_response(self, query: str, raw_file_path: str = None) -> Dict:
        # ... (same as before) ...

# Example usage updated
if __name__ == "__main__":
    compiler = ZeroCompiler(api_key="your_openrouter_api_key")
    
    print("ZeroCompiler using OpenRouter API")
    test_query = "applications of AI in healthcare"
    results = compiler.compile_response(test_query)
    
    # ... (rest same) ...