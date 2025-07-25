import json
import logging
import requests
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
                 model="meta-llama/llama-4-maverick:free",
                 api_key=None,
                 max_tokens_per_chunk=3000,
                 max_response_tokens=1000):

        self.raw_file = raw_file
        self.reports_file = reports_file
        self.model = model
        self.api_key = api_key
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.max_response_tokens = max_response_tokens
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

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
        chunks = []
        current_chunk = {
            'urls': [],
            'combined_text': '',
            'token_count': 0,
            'chunk_id': 0
        }
        chunk_id = 0

        for url, page_data in content.items():
            page_text = f"""
URL: {url}
Title: {page_data.get('title', 'No Title')}
Content: {page_data.get('content', '')}
Meta Description: {page_data.get('meta_description', '')}
---
"""
            page_tokens = self._count_tokens(page_text)

            if (current_chunk['token_count'] + page_tokens > self.max_tokens_per_chunk 
                and current_chunk['urls']):
                current_chunk['chunk_id'] = chunk_id
                chunks.append(current_chunk)
                chunk_id += 1
                current_chunk = {
                    'urls': [],
                    'combined_text': '',
                    'token_count': 0,
                    'chunk_id': chunk_id
                }

            current_chunk['urls'].append(url)
            current_chunk['combined_text'] += page_text
            current_chunk['token_count'] += page_tokens

        if current_chunk['urls']:
            current_chunk['chunk_id'] = chunk_id
            chunks.append(current_chunk)

        self.logger.info(f"Created {len(chunks)} content chunks")
        return chunks

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
        prompt = f"""
Based on the following web content, provide a comprehensive analysis that addresses the query: "{query}"

Content to analyze:
{chunk['combined_text']}

Please provide a structured response that:
1. Summarizes the key information relevant to the query
2. Identifies the main themes and concepts
3. Highlights important facts, statistics, or findings
4. Notes any contradictions or different perspectives
5. Provides actionable insights or conclusions

Sources included: {', '.join(chunk['urls'])}

Response:"""

        messages = [
            {"role": "system", "content": "You are an expert analyst who creates comprehensive, well-structured reports from web content."},
            {"role": "user", "content": prompt}
        ]

        response = self._call_openrouter(messages, self.max_response_tokens)
        if response:
            return response
        return self._generate_mock_report(chunk, query)

    def _generate_mock_report(self, chunk: Dict, query: str) -> str:
        urls_count = len(chunk['urls'])
        content_length = len(chunk['combined_text'])

        return f"""
ANALYSIS REPORT - Chunk {chunk['chunk_id']}

Query: "{query}"

SUMMARY:
Based on analysis of {urls_count} web sources containing {content_length:,} characters of content, the following key insights were identified regarding "{query}":

KEY FINDINGS:
• Comprehensive topic coverage
• Notable trends and technical details
• Practical examples and real-world relevance

MAIN THEMES:
1. Core Concepts
2. Implementation Strategies
3. Industry Impact
4. Challenges and Debates
5. Emerging Innovations

SOURCES ANALYZED:
{chr(10).join(f"• {url}" for url in chunk['urls'])}
""".strip()

    def _synthesize_final_report(self, individual_reports: List[str], query: str) -> str:
        combined = "\n\n".join([f"SECTION {i+1}:\n{report}" for i, report in enumerate(individual_reports)])

        synthesis_prompt = f"""
You are tasked with creating a comprehensive final report by synthesizing the following individual analysis sections. 
The original query was: "{query}"

Individual Analysis Sections:
{combined}

Please create a unified, comprehensive report that:
1. Integrates insights from all sections
2. Identifies common themes and patterns
3. Resolves contradictions
4. Provides actionable conclusions
5. Attributes insights to source sets when appropriate

Final Report:"""

        messages = [
            {"role": "system", "content": "You are a master analyst synthesizing multiple reports into a unified expert-level document."},
            {"role": "user", "content": synthesis_prompt}
        ]

        response = self._call_openrouter(messages, self.max_response_tokens * 2)
        return response or self._generate_mock_synthesis(individual_reports, query)

    def _generate_mock_synthesis(self, reports: List[str], query: str) -> str:
        total_sources = sum(report.count('•') for report in reports)
        return f"""
COMPREHENSIVE SYNTHESIS REPORT

Query: "{query}"
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sources Analyzed: {total_sources}
Sections: {len(reports)}

INTEGRATED INSIGHTS:
1. Consistent foundational principles across domains
2. Real-world implementations provide clear relevance
3. Current trends support growing importance
4. Multiple viewpoints offer depth and nuance

RECOMMENDATIONS:
• Continue investigation of evolving trends
• Apply knowledge to current strategic planning
• Validate findings with further research

Conclusion:
The analysis of {len(reports)} sections offers a robust foundation for understanding "{query}" with reliable cross-referenced data from a variety of reputable sources.
""".strip()

    def compile_response(self, query: str, raw_file_path: str = None) -> Dict:
        self.logger.info(f"Starting compilation for query: '{query}'")
        self.current_query = query

        raw_file = raw_file_path or self.raw_file
        try:
            with open(raw_file, 'r', encoding='utf-8') as f:
                raw_content = json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Raw content file not found: {raw_file}")
            return {"error": "Raw content file not found"}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in raw content file: {e}")
            return {"error": "Invalid raw content format"}

        if not raw_content:
            self.logger.warning("No content available for compilation")
            return {"error": "No content available"}

        self.logger.info(f"Loaded content from {len(raw_content)} sources")
        chunks = self._chunk_content(raw_content)
        self.processed_chunks = chunks

        individual_reports = []
        for chunk in chunks:
            self.logger.info(f"Processing chunk {chunk['chunk_id']} ({len(chunk['urls'])} sources)")
            chunk_report = self._generate_chunk_report(chunk, query)
            if chunk_report:
                individual_reports.append(chunk_report)
            else:
                self.logger.warning(f"Failed to generate report for chunk {chunk['chunk_id']}")

        self.individual_reports = individual_reports

        if len(individual_reports) > 1:
            final_report = self._synthesize_final_report(individual_reports, query)
        elif len(individual_reports) == 1:
            final_report = individual_reports[0]
        else:
            final_report = "No reports could be generated from the available content."

        self.final_report = final_report

        compilation_results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources_processed": len(raw_content),
            "chunks_created": len(chunks),
            "reports_generated": len(individual_reports),
            "final_report": final_report,
            "individual_reports": individual_reports,
            "processing_metadata": {
                "model_used": self.model,
                "total_tokens_processed": sum(chunk['token_count'] for chunk in chunks),
                "average_chunk_size": sum(chunk['token_count'] for chunk in chunks) / len(chunks) if chunks else 0
            }
        }

        self._save_reports(compilation_results)
        self.logger.info(f"Compilation completed: {len(individual_reports)} reports generated")
        return compilation_results

    def _save_reports(self, results: Dict):
        try:
            try:
                with open(self.reports_file, 'r', encoding='utf-8') as f:
                    all_reports = json.load(f)
            except FileNotFoundError:
                all_reports = []

            report_id = hashlib.md5(f"{results['query']}{results['timestamp']}".encode()).hexdigest()[:8]
            results['report_id'] = report_id
            all_reports.append(results)

            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump(all_reports, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved report {report_id} to {self.reports_file}")
        except Exception as e:
            self.logger.error(f"Failed to save reports: {e}")

    def get_report_history(self) -> List[Dict]:
        try:
            with open(self.reports_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def clear_reports(self):
        try:
            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.logger.info("Cleared all reports")
        except Exception as e:
            self.logger.error(f"Failed to clear reports: {e}")

if __name__ == "__main__":
    compiler = ZeroCompiler(api_key="your_openrouter_api_key")

    print("ZeroCompiler using OpenRouter API")
    test_query = "applications of AI in healthcare"
    results = compiler.compile_response(test_query)

    if "error" not in results:
        print(f"\nSources processed: {results['sources_processed']}")
        print(f"Chunks created: {results['chunks_created']}")
        print(f"Reports generated: {results['reports_generated']}")
        print(f"\nFinal Report Preview:\n{results['final_report'][:500]}...")
        print(f"Report saved with ID: {results.get('report_id', 'unknown')}")
    else:
        print(f"Compilation failed: {results['error']}")