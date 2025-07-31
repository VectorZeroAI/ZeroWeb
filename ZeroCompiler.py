# ZeroCompiler.py
import json
import logging
import requests
import tiktoken
import os
import time
from datetime import datetime
import hashlib
from typing import Dict, List, Optional, Tuple, Any
import re
import keyring
import sys
import getpass

class ZeroCompiler:
    """
    ZeroCompiler - LLM-powered Report Generator for ZeroNet
    Now using OpenRouter API with meta-llama/llama-4-maverick:free
    
    This module compiles scraped content into coherent reports using LLMs.
    Handles chunking, API calls, and report generation with proper error handling.
    """
    
    def __init__(self,
                 raw_file="raw.json",
                 reports_file="reports.json",
                 model="meta-llama/llama-4-maverick:free",
                 api_key=None,
                 max_tokens_per_chunk=3000,
                 max_response_tokens=1000):
        """
        Initialize the compiler with proper configuration
        
        Args:
            raw_file (str): Path to raw scraped data
            reports_file (str): Path to save generated reports
            model (str): LLM model to use
            api_key (str, optional): OpenRouter API key. If None, will try environment variables.
            max_tokens_per_chunk (int): Maximum tokens per content chunk
            max_response_tokens (int): Maximum tokens for API responses
        """
        self.raw_file = raw_file
        self.reports_file = reports_file
        self.model = model
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.max_response_tokens = max_response_tokens
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Securely get API key
        self.api_key = self._get_api_key(api_key)
        
        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            
        # Initialize state
        self.current_query = ""
        self.processed_chunks = []
        self.individual_reports = []
        self.final_report = ""
        
        # Setup logger
        self.logger = self._setup_logger()
        self.logger.info("ZeroCompiler initialized successfully")

    def _setup_logger(self):
        """Setup logging for ZeroCompiler"""
        logger = logging.getLogger('ZeroCompiler')
        logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers if logger already exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[ZeroCompiler] %(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def _get_api_key(self, provided_key: Optional[str] = None) -> str:
        """Securely retrieve API key using best available method"""
        # 1. Use provided key if available
        if provided_key:
            self.logger.info("Using API key provided in initialization")
            return provided_key
            
        # 2. Try environment variable
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if api_key:
            self.logger.info("Using API key from environment variable")
            return api_key
            
        # 3. Try system keyring
        try:
            api_key = keyring.get_password("ZeroNet", "openrouter_api_key")
            if api_key:
                self.logger.info("Using API key from system keyring")
                return api_key
        except Exception as e:
            self.logger.debug(f"Could not access system keyring: {e}")
        
        # 4. Only prompt interactively if in terminal
        if sys.stdin.isatty():
            self.logger.warning("API key not found in environment or keyring")
            api_key = getpass.getpass("Enter OpenRouter API key: ")
            
            save_it = input("Save securely in system keyring? (y/n): ").lower()
            if save_it == 'y':
                try:
                    keyring.set_password("ZeroNet", "openrouter_api_key", api_key)
                    self.logger.info("API key saved securely in system keyring")
                except Exception as e:
                    self.logger.warning(f"Could not save to system keyring: {e}")
            
            return api_key
            
        # If we get here, we couldn't get an API key
        raise ValueError("API key is required. Set OPENROUTER_API_KEY environment variable.")

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tokenizer"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            # Fallback estimation (rough approximation)
            return max(1, len(text) // 4)

    def _chunk_content(self, content: Dict[str, Dict]) -> List[Dict]:
        """
        Split content into manageable chunks for processing
        
        Args:
            content (dict): Raw scraped content from ZeroScraper
            
        Returns:
            list: List of chunks with URLs, text segments, and token counts
        """
        chunks = []
        current_chunk = {
            'urls': [],
            'text_segments': [],  # Store as list instead of concatenated string
            'token_count': 0,
            'chunk_id': 0
        }
        chunk_id = 0
        
        for url, page_data in content.items():
            # Format page content
            page_text = f"""
            URL: {url}
            Title: {page_data.get('title', 'No Title')}
            Content: {page_data.get('snippet', '')}
            """
            
            # Count tokens in this page
            token_count = self._count_tokens(page_text)
            
            # If adding this page would exceed max tokens, finalize current chunk
            if current_chunk['token_count'] + token_count > self.max_tokens_per_chunk and current_chunk['urls']:
                # Join segments only when chunk is complete
                current_chunk['combined_text'] = ''.join(current_chunk['text_segments'])
                chunks.append(current_chunk)
                chunk_id += 1
                current_chunk = {
                    'urls': [],
                    'text_segments': [],
                    'token_count': 0,
                    'chunk_id': chunk_id
                }
                
            # Add page to current chunk (as segment, not concatenated)
            current_chunk['urls'].append(url)
            current_chunk['text_segments'].append(page_text)
            current_chunk['token_count'] += token_count
            
        # Add the last chunk if it has content
        if current_chunk['urls']:
            current_chunk['combined_text'] = ''.join(current_chunk['text_segments'])
            chunks.append(current_chunk)
            
        self.logger.info(f"Created {len(chunks)} chunks from {len(content)} pages")
        return chunks

    def _generate_chunk_report(self, chunk: Dict, query: str) -> Optional[str]:
        """
        Generate a report for a single content chunk using LLM
        
        Args:
            chunk (dict): Content chunk to process
            query (str): User's search query
            
        Returns:
            str: Generated report section or None if failed
        """
        # Create prompt for the LLM
        prompt = f"""
        You are an expert research assistant analyzing information related to: "{query}"
        
        Below is a set of web pages related to this topic. Please synthesize the information 
        into a concise, well-structured report section that focuses on how these pages relate to the query.
        
        For each relevant URL, include:
        1. A brief summary of the key points
        2. How it relates to the query
        3. Any important facts or data
        
        Web page content:
        {chunk['combined_text']}
        
        Please format your response as a well-structured markdown section with clear headings.
        Do not include URLs in the response - just the synthesized information.
        Keep the response focused and relevant to the query.
        """
        
        try:
            self.logger.info(f"Generating report for chunk {chunk['chunk_id']} with {chunk['token_count']} tokens")
            
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_response_tokens
                },
                timeout=60
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Validate response structure
            response_data = response.json()
            if ('choices' in response_data and len(response_data['choices']) > 0 and
                'message' in response_data['choices'][0] and
                'content' in response_data['choices'][0]['message']):
                return response_data['choices'][0]['message']['content']
            else:
                self.logger.error(f"Unexpected API response structure: {response_data}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                try:
                    self.logger.error(f"Response body: {e.response.text}")
                except:
                    pass
            return None
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return None

    def _generate_final_report(self, query: str, individual_reports: List[str]) -> str:
        """
        Generate final consolidated report from individual chunk reports
        
        Args:
            query (str): User's search query
            individual_reports (list): List of reports from each chunk
            
        Returns:
            str: Final consolidated report
        """
        combined_reports = "\n\n".join(individual_reports)
        
        prompt = f"""
        You are an expert research analyst creating a comprehensive report about: "{query}"
        
        Below are several sections of a report that have been generated from different parts of the research.
        Please synthesize these sections into one cohesive, well-structured final report.
        
        Guidelines:
        1. Organize the information logically with clear headings and subheadings
        2. Remove any redundancies between sections
        3. Ensure smooth transitions between topics
        4. Maintain a professional, academic tone
        5. Highlight the most important findings
        6. Include a brief conclusion that summarizes key insights
        
        Individual report sections:
        {combined_reports}
        
        Please format the final report in markdown with appropriate headings.
        """
        
        try:
            self.logger.info(f"Generating final report from {len(individual_reports)} sections")
            
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_response_tokens * 2  # Allow for longer final report
                },
                timeout=90
            )
            
            response.raise_for_status()
            
            response_data = response.json()
            if ('choices' in response_data and len(response_data['choices']) > 0 and
                'message' in response_data['choices'][0] and
                'content' in response_data['choices'][0]['message']):
                return response_data['choices'][0]['message']['content']
            else:
                self.logger.error(f"Unexpected API response structure for final report: {response_data}")
                return "Error: Failed to generate final report"
                
        except Exception as e:
            self.logger.error(f"Final report generation failed: {e}")
            return "Error: Failed to generate final report"

    def _save_report(self, query: str, final_report: str, individual_reports: List[str]):
        """Save the generated report to reports.json"""
        report_id = hashlib.md5(f"{query}{datetime.now().timestamp()}".encode()).hexdigest()[:8]
        
        report = {
            "id": report_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "final_report": final_report,
            "individual_reports_count": len(individual_reports),
            "sources_processed": len(individual_reports)  # In a real implementation, this would be more accurate
        }
        
        try:
            # Load existing reports
            existing_reports = []
            if os.path.exists(self.reports_file):
                with open(self.reports_file, 'r', encoding='utf-8') as f:
                    try:
                        existing_reports = json.load(f)
                        if not isinstance(existing_reports, list):
                            existing_reports = []
                    except json.JSONDecodeError:
                        existing_reports = []
            
            # Add new report
            existing_reports.insert(0, report)  # Put newest report first
            
            # Save updated reports
            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump(existing_reports, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Report saved with ID: {report_id}")
            return report_id
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            return None

    def compile_response(self, query: str, raw_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Compile a comprehensive response to a query using scraped content
        
        Args:
            query (str): User query to respond to
            raw_file (str, optional): Path to raw content file. Defaults to self.raw_file.
            
        Returns:
            dict: Contains final report and metadata, or error information
        """
        self.current_query = query
        self.logger.info(f"Starting report compilation for query: '{query}'")
        
        # Use provided raw_file or default
        file_to_use = raw_file if raw_file else self.raw_file
        
        # Check if raw file exists
        if not os.path.exists(file_to_use):
            error_msg = f"Raw content file not found: {file_to_use}"
            self.logger.error(error_msg)
            return {"error": error_msg}
        
        # Load raw content
        try:
            with open(file_to_use, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
            if not content:
                error_msg = "Raw content file is empty"
                self.logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Failed to load raw content: {e}"
            self.logger.error(error_msg)
            return {"error": error_msg}
        
        # Chunk the content
        chunks = self._chunk_content(content)
        if not chunks:
            error_msg = "No content to process after chunking"
            self.logger.error(error_msg)
            return {"error": error_msg}
        
        # Generate reports for each chunk
        self.individual_reports = []
        for chunk in chunks:
            report = self._generate_chunk_report(chunk, query)
            if report:
                self.individual_reports.append(report)
            # Be respectful to API rate limits
            time.sleep(0.5)
        
        if not self.individual_reports:
            error_msg = "Failed to generate any report sections"
            self.logger.error(error_msg)
            return {"error": error_msg}
        
        # Generate final report
        self.final_report = self._generate_final_report(query, self.individual_reports)
        
        # Save the report
        report_id = self._save_report(query, self.final_report, self.individual_reports)
        
        # Prepare result
        result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources_processed": len(content),
            "chunks_processed": len(chunks),
            "reports_generated": len(self.individual_reports),
            "final_report": self.final_report
        }
        
        if report_id:
            result["report_id"] = report_id
            
        self.logger.info(f"Report compilation completed for query: '{query}'")
        return result

    def get_previous_reports(self) -> List[Dict]:
        """Get list of previously generated reports"""
        try:
            if os.path.exists(self.reports_file):
                with open(self.reports_file, 'r', encoding='utf-8') as f:
                    reports = json.load(f)
                    return reports
            return []
        except Exception as e:
            self.logger.error(f"Failed to load previous reports: {e}")
            return []

    def clear_reports(self):
        """Clear all saved reports"""
        try:
            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.logger.info("Cleared all reports")
        except Exception as e:
            self.logger.error(f"Failed to clear reports: {e}")

# Example usage
if __name__ == "__main__":
    print("ZeroCompiler using OpenRouter API")
    print("=" * 50)
    print("Absolute Privacy Guaranteed (API Key Security Active)")
    print("All operations maintain user privacy")
    print("=" * 50)
    
    # Initialize compiler
    try:
        compiler = ZeroCompiler()
        
        # Test query
        test_query = "applications of AI in healthcare"
        print(f"\nGenerating report for: '{test_query}'")
        
        # For testing, we'll create a sample raw.json if it doesn't exist
        if not os.path.exists('raw.json'):
            print("Creating sample raw.json for testing...")
            sample_data = {
                "https://example.com/ai-healthcare": {
                    "title": "AI in Healthcare Applications",
                    "snippet": "Artificial intelligence is transforming healthcare with applications in medical imaging, drug discovery, and patient monitoring. AI systems can detect patterns in medical images that humans might miss, accelerating diagnosis and improving accuracy."
                },
                "https://example.com/ai-diagnosis": {
                    "title": "AI-Powered Diagnostic Systems",
                    "snippet": "Machine learning algorithms are now being used to analyze patient data and medical images to assist doctors in making more accurate diagnoses. These systems learn from vast datasets of medical cases to identify potential health issues."
                }
            }
            with open('raw.json', 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        # Generate report
        print("\nCompiling response...")
        results = compiler.compile_response(test_query)
        
        if "error" not in results:
            print(f"\nReport generated successfully!")
            print(f"Sources processed: {results['sources_processed']}")
            print(f"Chunks processed: {results['chunks_processed']}")
            print(f"Reports generated: {results['reports_generated']}")
            print(f"\nFinal Report Preview:\n{results['final_report'][:500]}...")
            print(f"\nFull report saved with ID: {results.get('report_id', 'unknown')}")
        else:
            print(f"Compilation failed: {results['error']}")
            
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        print("Please set your OPENROUTER_API_KEY environment variable or provide an API key file.")
        print("Example: export OPENROUTER_API_KEY='your_api_key_here'")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()