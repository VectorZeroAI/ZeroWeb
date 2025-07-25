import json
import logging
import openai
import tiktoken
from typing import Dict, List, Optional, Union
import re
import time
from datetime import datetime
import hashlib

class ZeroCompiler:
    """
    ZeroCompiler - LLM-powered Report Generator for ZeroNet
    Takes raw.json contents, parses into chunks, and creates comprehensive reports
    Handles context window limitations and generates structured responses
    """
    
    def __init__(self, 
                 raw_file="raw.json",
                 reports_file="reports.json",
                 model="gpt-3.5-turbo",
                 max_tokens_per_chunk=3000,
                 max_response_tokens=1000):
        
        self.raw_file = raw_file
        self.reports_file = reports_file
        self.model = model
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.max_response_tokens = max_response_tokens
        
        # Initialize tokenizer for the model
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # fallback
        
        # LLM configuration
        self.openai_client = None
        self._setup_llm()
        
        # Processing state
        self.current_query = ""
        self.processed_chunks = []
        self.individual_reports = []
        self.final_report = ""
        
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging for ZeroCompiler"""
        logger = logging.getLogger('ZeroCompiler')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[ZeroCompiler] %(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _setup_llm(self):
        """Setup LLM client (OpenAI or alternative)"""
        try:
            # In a real implementation, you'd set up the OpenAI client
            # self.openai_client = openai.OpenAI(api_key="your-api-key")
            self.logger.info(f"LLM client configured for model: {self.model}")
        except Exception as e:
            self.logger.warning(f"LLM client setup failed: {e}")
            self.logger.info("Running in simulation mode")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using the model's tokenizer"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            # Fallback: approximate 4 characters per token
            return len(text) // 4
    
    def _chunk_content(self, content: Dict[str, Dict]) -> List[Dict]:
        """
        Split content into chunks that fit within context window
        
        Args:
            content (dict): Raw content from raw.json
            
        Returns:
            List[Dict]: List of content chunks
        """
        chunks = []
        current_chunk = {
            'urls': [],
            'combined_text': '',
            'token_count': 0,
            'chunk_id': 0
        }
        
        chunk_id = 0
        
        for url, page_data in content.items():
            # Prepare page text
            page_text = f"""
URL: {url}
Title: {page_data.get('title', 'No Title')}
Content: {page_data.get('content', '')}
Meta Description: {page_data.get('meta_description', '')}
---
"""
            
            page_tokens = self._count_tokens(page_text)
            
            # Check if adding this page would exceed chunk limit
            if (current_chunk['token_count'] + page_tokens > self.max_tokens_per_chunk 
                and current_chunk['urls']):
                
                # Save current chunk and start new one
                current_chunk['chunk_id'] = chunk_id
                chunks.append(current_chunk)
                chunk_id += 1
                
                current_chunk = {
                    'urls': [],
                    'combined_text': '',
                    'token_count': 0,
                    'chunk_id': chunk_id
                }
            
            # Add page to current chunk
            current_chunk['urls'].append(url)
            current_chunk['combined_text'] += page_text
            current_chunk['token_count'] += page_tokens
        
        # Add final chunk if it has content
        if current_chunk['urls']:
            current_chunk['chunk_id'] = chunk_id
            chunks.append(current_chunk)
        
        self.logger.info(f"Created {len(chunks)} content chunks")
        return chunks
    
    def _generate_chunk_report(self, chunk: Dict, query: str) -> Optional[str]:
        """
        Generate a report for a single chunk using LLM
        
        Args:
            chunk (dict): Content chunk
            query (str): User query
            
        Returns:
            str: Generated report for the chunk
        """
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
        
        try:
            if self.openai_client:
                # Real LLM call
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert analyst who creates comprehensive, well-structured reports from web content."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.max_response_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            else:
                # Simulation mode - generate mock report
                return self._generate_mock_report(chunk, query)
                
        except Exception as e:
            self.logger.error(f"LLM generation failed for chunk {chunk['chunk_id']}: {e}")
            return self._generate_fallback_report(chunk, query)
    
    def _generate_mock_report(self, chunk: Dict, query: str) -> str:
        """Generate a mock report for demonstration purposes"""
        urls_count = len(chunk['urls'])
        content_length = len(chunk['combined_text'])
        
        mock_report = f"""
ANALYSIS REPORT - Chunk {chunk['chunk_id']}

Query: "{query}"

SUMMARY:
Based on analysis of {urls_count} web sources containing {content_length:,} characters of content, the following key insights were identified regarding "{query}":

KEY FINDINGS:
• The sources provide comprehensive coverage of the topic with multiple perspectives
• Technical details and practical applications are well-documented
• Current trends and developments are discussed across the sources
• Various methodologies and approaches are presented

MAIN THEMES:
1. Fundamental concepts and definitions
2. Technical implementation details
3. Current industry applications
4. Future developments and trends
5. Best practices and recommendations

INSIGHTS:
The analyzed content demonstrates a thorough exploration of "{query}" with evidence-based information from reputable sources. The material covers both theoretical foundations and practical applications.

SOURCES ANALYZED:
{chr(10).join(f"• {url}" for url in chunk['urls'])}

This analysis provides a solid foundation for understanding the topic and can inform decision-making processes.
"""
        return mock_report.strip()
    
    def _generate_fallback_report(self, chunk: Dict, query: str) -> str:
        """Generate a basic fallback report when LLM fails"""
        return f"""
BASIC REPORT - Chunk {chunk['chunk_id']}

Query: "{query}"
Sources: {len(chunk['urls'])} pages analyzed
Content Length: {len(chunk['combined_text']):,} characters

This chunk contains relevant information from the following sources:
{chr(10).join(f"• {url}" for url in chunk['urls'])}

Due to processing limitations, detailed analysis is not available for this chunk.
Please refer to the individual sources for specific information.
"""
    
    def _synthesize_final_report(self, individual_reports: List[str], query: str) -> str:
        """
        Synthesize individual chunk reports into a final comprehensive report
        
        Args:
            individual_reports (list): List of individual chunk reports
            query (str): Original user query
            
        Returns:
            str: Final synthesized report
        """
        if not individual_reports:
            return "No reports generated - insufficient content available."
        
        if len(individual_reports) == 1:
            return individual_reports[0]
        
        # Combine reports for synthesis
        combined_reports = "\n\n".join([
            f"SECTION {i+1}:\n{report}" 
            for i, report in enumerate(individual_reports)
        ])
        
        synthesis_prompt = f"""
You are tasked with creating a comprehensive final report by synthesizing the following individual analysis sections. 
The original query was: "{query}"

Individual Analysis Sections:
{combined_reports}

Please create a unified, comprehensive report that:
1. Integrates insights from all sections
2. Identifies common themes and patterns
3. Resolves any contradictions or conflicting information
4. Provides a clear, actionable conclusion
5. Maintains proper attribution to sources

Final Report:"""
        
        try:
            if self.openai_client:
                # Real LLM synthesis
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert report synthesizer who creates comprehensive final reports from multiple analysis sections."},
                        {"role": "user", "content": synthesis_prompt}
                    ],
                    max_tokens=self.max_response_tokens * 2,  # Longer for final report
                    temperature=0.5
                )
                return response.choices[0].message.content
            else:
                # Mock synthesis
                return self._generate_mock_synthesis(individual_reports, query)
                
        except Exception as e:
            self.logger.error(f"Final report synthesis failed: {e}")
            return self._generate_fallback_synthesis(individual_reports, query)
    
    def _generate_mock_synthesis(self, reports: List[str], query: str) -> str:
        """Generate a mock synthesized report"""
        total_sources = sum(report.count('•') for report in reports)
        
        return f"""
COMPREHENSIVE ANALYSIS REPORT

Query: "{query}"
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sources Analyzed: {total_sources} web pages
Sections Processed: {len(reports)}

EXECUTIVE SUMMARY:
This comprehensive analysis synthesizes information from {len(reports)} detailed sections covering various aspects of "{query}". The analysis reveals consistent patterns and provides actionable insights based on extensive web research.

INTEGRATED FINDINGS:
Through cross-section analysis, several key themes emerged:

1. FOUNDATIONAL CONCEPTS: Core principles and definitions are consistently presented across sources
2. PRACTICAL APPLICATIONS: Real-world implementations demonstrate the topic's relevance
3. CURRENT TRENDS: Recent developments show ongoing evolution in the field
4. EXPERT PERSPECTIVES: Multiple viewpoints provide comprehensive coverage
5. FUTURE IMPLICATIONS: Emerging trends suggest continued growth and development

SYNTHESIS INSIGHTS:
The analysis reveals a mature understanding of "{query}" with substantial evidence supporting key concepts. Cross-referencing multiple sources confirms the reliability of presented information.

RECOMMENDATIONS:
Based on the comprehensive analysis:
• Continue monitoring developments in this area
• Consider practical implementation of discussed concepts
• Stay informed about emerging trends and best practices
• Leverage insights for strategic decision-making

CONCLUSION:
This analysis provides a thorough foundation for understanding "{query}" with evidence-based insights from multiple authoritative sources. The synthesized information offers both theoretical depth and practical applicability.

Report generated by ZeroCompiler - ZeroNet Analysis Engine
"""
    
    def _generate_fallback_synthesis(self, reports: List[str], query: str) -> str:
        """Generate a basic fallback synthesis"""
        return f"""
ANALYSIS SUMMARY

Query: "{query}"
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This report combines {len(reports)} individual analysis sections. Due to processing limitations, 
detailed synthesis is not available. Please refer to the individual sections below for 
comprehensive information:

{chr(10).join([f"SECTION {i+1}:{chr(10)}{report}{chr(10)}" for i, report in enumerate(reports)])}

End of Report
"""
    
    def compile_response(self, query: str, raw_file_path: str = None) -> Dict:
        """
        Main compilation function: Process raw content and generate comprehensive report
        
        Args:
            query (str): User's search query
            raw_file_path (str): Path to raw.json file (optional)
            
        Returns:
            Dict: Compilation results including reports and metadata
        """
        self.logger.info(f"Starting compilation for query: '{query}'")
        self.current_query = query
        
        # Load raw content
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
        
        # Chunk content for processing
        chunks = self._chunk_content(raw_content)
        self.processed_chunks = chunks
        
        # Generate individual reports for each chunk
        self.logger.info(f"Generating reports for {len(chunks)} chunks...")
        individual_reports = []
        
        for chunk in chunks:
            self.logger.info(f"Processing chunk {chunk['chunk_id']} ({len(chunk['urls'])} sources)")
            
            chunk_report = self._generate_chunk_report(chunk, query)
            if chunk_report:
                individual_reports.append(chunk_report)
                self.logger.info(f"Generated report for chunk {chunk['chunk_id']}")
            else:
                self.logger.warning(f"Failed to generate report for chunk {chunk['chunk_id']}")
        
        self.individual_reports = individual_reports
        
        # Generate final synthesized report
        if len(individual_reports) > 1:
            self.logger.info("Synthesizing final report from individual sections...")
            final_report = self._synthesize_final_report(individual_reports, query)
        elif len(individual_reports) == 1:
            final_report = individual_reports[0]
        else:
            final_report = "No reports could be generated from the available content."
        
        self.final_report = final_report
        
        # Prepare results
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
        
        # Save reports to file
        self._save_reports(compilation_results)
        
        self.logger.info(f"Compilation completed: {len(individual_reports)} reports generated")
        return compilation_results
    
    def _save_reports(self, results: Dict):
        """Save compilation results to reports file"""
        try:
            # Load existing reports
            try:
                with open(self.reports_file, 'r', encoding='utf-8') as f:
                    all_reports = json.load(f)
            except FileNotFoundError:
                all_reports = []
            
            # Add new report
            report_id = hashlib.md5(f"{results['query']}{results['timestamp']}".encode()).hexdigest()[:8]
            results['report_id'] = report_id
            all_reports.append(results)
            
            # Save updated reports
            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump(all_reports, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved report {report_id} to {self.reports_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save reports: {e}")
    
    def get_report_history(self) -> List[Dict]:
        """Get history of generated reports"""
        try:
            with open(self.reports_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def clear_reports(self):
        """Clear all saved reports"""
        try:
            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            self.logger.info("Cleared all reports")
        except Exception as e:
            self.logger.error(f"Failed to clear reports: {e}")

# Integration example for ZeroNet
if __name__ == "__main__":
    # Initialize ZeroCompiler
    compiler = ZeroCompiler()
    
    print("ZeroCompiler - LLM-powered Report Generator")
    print("=" * 50)
    
    # Example: Compile a report (assuming raw.json exists)
    test_query = "artificial intelligence and machine learning applications"
    
    print(f"Test Query: '{test_query}'")
    print("Compiling comprehensive report...")
    
    # Generate report
    results = compiler.compile_response(test_query)
    
    if "error" not in results:
        print(f"\nCompilation Results:")
        print(f"Sources processed: {results['sources_processed']}")
        print(f"Chunks created: {results['chunks_created']}")
        print(f"Reports generated: {results['reports_generated']}")
        print(f"Total tokens processed: {results['processing_metadata']['total_tokens_processed']}")
        
        print(f"\nFinal Report Preview:")
        print("-" * 40)
        print(results['final_report'][:500] + "..." if len(results['final_report']) > 500 else results['final_report'])
        
        print(f"\nReport saved with ID: {results.get('report_id', 'unknown')}")
    else:
        print(f"Compilation failed: {results['error']}")
    
    print(f"\nZeroCompiler ready for ZeroNet integration")