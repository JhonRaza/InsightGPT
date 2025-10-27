"""
OpenAI integration utilities for InsightGPT
Handles summarization, entity extraction, and question answering
"""
from typing import List, Dict, Optional
import openai
import streamlit as st
from config import Config
import tiktoken


class OpenAIHelper:
    """Helper class for OpenAI API interactions"""
    
    def __init__(self, api_key: str, model: str = None):
        """
        Initialize OpenAI helper
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default from config)
        """
        self.config = Config()
        self.api_key = api_key
        self.model = model or self.config.DEFAULT_MODEL
        openai.api_key = api_key
        
        # Initialize tiktoken for token counting
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        """
        Generate a comprehensive summary of the text
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary in words
            
        Returns:
            Summary text or None if failed
        """
        try:
            # Check token count and truncate if necessary
            token_count = self.count_tokens(text)
            max_tokens = 8000 if self.model == "gpt-4" else 3000
            
            if token_count > max_tokens:
                # Truncate text
                tokens = self.encoding.encode(text)[:max_tokens]
                text = self.encoding.decode(tokens)
                st.warning(f"Text was truncated to fit model limits ({max_tokens} tokens)")
            
            prompt = f"""Analyze the following document and provide a comprehensive, well-structured summary.
            
The summary should:
- Capture the main ideas, key points, and important details
- Be approximately {max_length} words
- Be organized in clear paragraphs
- Maintain the core message and context of the original

Document:
{text}

Summary:"""
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing and summarizing documents. Provide clear, concise, and comprehensive summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.TEMPERATURE_SUMMARY,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error generating summary: {str(e)}")
            return None
    
    def extract_insights(self, text: str) -> Optional[Dict[str, List[str]]]:
        """
        Extract key insights from text: entities, themes, and action items
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with extracted insights or None if failed
        """
        try:
            # Check token count and truncate if necessary
            token_count = self.count_tokens(text)
            max_tokens = 8000 if self.model == "gpt-4" else 3000
            
            if token_count > max_tokens:
                tokens = self.encoding.encode(text)[:max_tokens]
                text = self.encoding.decode(tokens)
            
            prompt = f"""Analyze the following document and extract key insights in a structured format.

Document:
{text}

Please provide:
1. KEY ENTITIES: Important people, organizations, places, or concepts mentioned
2. MAIN THEMES: Core topics, ideas, or subjects discussed
3. ACTION ITEMS: Any tasks, recommendations, or next steps mentioned

Format your response exactly as follows:
KEY ENTITIES:
- Entity 1
- Entity 2
...

MAIN THEMES:
- Theme 1
- Theme 2
...

ACTION ITEMS:
- Action 1
- Action 2
...

(If a category has no items, write "None identified")"""
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing documents and extracting structured insights. Be precise and thorough."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.TEMPERATURE_EXTRACTION,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the structured response
            insights = self._parse_insights(content)
            return insights
            
        except Exception as e:
            st.error(f"Error extracting insights: {str(e)}")
            return None
    
    def _parse_insights(self, content: str) -> Dict[str, List[str]]:
        """Parse structured insights from GPT response"""
        insights = {
            "entities": [],
            "themes": [],
            "action_items": []
        }
        
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if "KEY ENTITIES:" in line:
                current_section = "entities"
            elif "MAIN THEMES:" in line:
                current_section = "themes"
            elif "ACTION ITEMS:" in line:
                current_section = "action_items"
            elif line.startswith('- ') and current_section:
                item = line[2:].strip()
                if item and item.lower() != "none identified":
                    insights[current_section].append(item)
        
        return insights
    
    def answer_question(self, question: str, context_chunks: List[str], 
                       chat_history: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Answer a question based on document context
        
        Args:
            question: User's question
            context_chunks: Relevant text chunks from the document
            chat_history: Previous chat messages for context
            
        Returns:
            Answer text or None if failed
        """
        try:
            # Combine context chunks
            context = "\n\n---\n\n".join(context_chunks)
            
            # Build messages
            messages = [
                {"role": "system", "content": """You are an intelligent assistant helping users understand documents. 
                
Your task is to answer questions based on the provided document context. 

Guidelines:
- Answer based ONLY on the information in the provided context
- If the answer is not in the context, say "I cannot find that information in the document"
- Be clear, concise, and helpful
- Cite specific parts of the document when relevant
- If the question is ambiguous, ask for clarification"""}
            ]
            
            # Add chat history if available
            if chat_history:
                for msg in chat_history[-4:]:  # Last 4 messages for context
                    messages.append(msg)
            
            # Add current question with context
            user_message = f"""Context from document:
{context}

Question: {question}"""
            
            messages.append({"role": "user", "content": user_message})
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config.TEMPERATURE_QA,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"Error answering question: {str(e)}")
            return None
    
    def generate_keywords(self, text: str, max_keywords: int = 10) -> Optional[List[str]]:
        """
        Extract key keywords/phrases from text
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to extract
            
        Returns:
            List of keywords or None if failed
        """
        try:
            token_count = self.count_tokens(text)
            max_tokens = 6000 if self.model == "gpt-4" else 2500
            
            if token_count > max_tokens:
                tokens = self.encoding.encode(text)[:max_tokens]
                text = self.encoding.decode(tokens)
            
            prompt = f"""Extract the {max_keywords} most important keywords or key phrases from this document.
            
Document:
{text}

Provide only the keywords/phrases, one per line, without numbers or bullets:"""
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying key terms and concepts in documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            keywords = [line.strip() for line in content.split('\n') if line.strip()]
            
            return keywords[:max_keywords]
            
        except Exception as e:
            st.error(f"Error generating keywords: {str(e)}")
            return None
