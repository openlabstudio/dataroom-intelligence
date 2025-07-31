"""
Base Agent Class for DataRoom Intelligence Specialized Agents
Provides common functionality for all specialized agents
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from openai import OpenAI
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseAgent(ABC):
    """Base class for all specialized analysis agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4"
        logger.info(f"🤖 {agent_name} agent initialized")
    
    @abstractmethod
    def analyze(self, processed_documents: List[Dict[str, Any]], 
               document_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specialized analysis - must be implemented by subclasses"""
        pass
    
    def _call_openai(self, system_prompt: str, user_prompt: str, 
                     max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """Common OpenAI API call with error handling"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ {self.agent_name} OpenAI call failed: {e}")
            raise
    
    def _prepare_document_context(self, processed_documents: List[Dict[str, Any]], 
                                 max_content_length: int = 10000) -> str:
        """Prepare document context for analysis"""
        context = ""
        for doc in processed_documents:
            if doc['type'] != 'error' and doc.get('content'):
                context += f"\n\n=== DOCUMENT: {doc['name']} ({doc['type'].upper()}) ===\n"
                # Take first part of content to fit within limits
                content = doc['content'][:max_content_length // len(processed_documents)]
                context += content
        return context
    
    def _extract_json_from_response(self, response_text: str, 
                                   fallback_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON from OpenAI response with fallback"""
        try:
            # Try to find JSON block in response
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Try to parse entire response as JSON
                return json.loads(response_text)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"⚠️ {self.agent_name} failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")
            return fallback_structure
