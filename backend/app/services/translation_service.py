# backend/app/services/translation_service.py
import os
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
import re
from core.config import settings

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for text translation using LibreTranslate"""
    
    def __init__(self):
        self.base_url = settings.TRANSLATION_SERVICE_URL
        self.api_key = settings.TRANSLATION_API_KEY
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def translate(self, text: str, target_language: str = "th", source_language: str = "auto") -> str:
        """
        Translate text to target language
        """
        try:
            logger.info(f"Translating text to {target_language}")
            logger.info(f"Text length: {len(text)} characters")
            
            if not text or not text.strip():
                raise ValueError("Text to translate is empty")
            
            # Clean and prepare text
            cleaned_text = self._preprocess_text(text)
            
            # Split long text into chunks if necessary
            if len(cleaned_text) > 5000:
                return await self._translate_long_text(cleaned_text, target_language, source_language)
            
            # Translate single chunk
            translated = await self._translate_chunk(cleaned_text, target_language, source_language)
            
            # Post-process translation
            final_translation = self._postprocess_translation(translated, target_language)
            
            logger.info(f"Translation completed successfully")
            logger.info(f"Translated text length: {len(final_translation)} characters")
            
            return final_translation
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise Exception(f"Failed to translate text: {str(e)}")
    
    async def _translate_chunk(self, text: str, target_language: str, source_language: str) -> str:
        """
        Translate a single chunk of text
        """
        try:
            session = await self._get_session()
            
            # Prepare request data
            data = {
                "q": text,
                "source": source_language,
                "target": target_language,
                "format": "text"
            }
            
            # Add API key if available
            if self.api_key:
                data["api_key"] = self.api_key
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make translation request
            async with session.post(
                f"{self.base_url}/translate",
                json=data,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Translation API error {response.status}: {error_text}")
                
                result = await response.json()
                
                if "translatedText" not in result:
                    raise Exception("Invalid response from translation service")
                
                return result["translatedText"]
                
        except asyncio.TimeoutError:
            raise Exception("Translation request timed out")
        except Exception as e:
            logger.error(f"Translation chunk failed: {str(e)}")
            raise
    
    async def _translate_long_text(self, text: str, target_language: str, source_language: str) -> str:
        """
        Translate long text by splitting into chunks
        """
        try:
            logger.info("Translating long text in chunks")
            
            # Split text into sentences/paragraphs
            chunks = self._split_text_intelligently(text)
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    logger.info(f"Translating chunk {i+1}/{len(chunks)}")
                    translated_chunk = await self._translate_chunk(chunk, target_language, source_language)
                    translated_chunks.append(translated_chunk)
                    
                    # Small delay to avoid overwhelming the API
                    await asyncio.sleep(0.5)
            
            # Join translated chunks
            return " ".join(translated_chunks)
            
        except Exception as e:
            logger.error(f"Long text translation failed: {str(e)}")
            raise
    
    def _split_text_intelligently(self, text: str, max_chunk_size: int = 4000) -> list:
        """
        Split text into chunks at sentence boundaries
        """
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Sentence is too long, split by words
                    words = sentence.split()
                    for word in words:
                        if len(current_chunk) + len(word) > max_chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                                current_chunk = word
                            else:
                                chunks.append(word)
                        else:
                            current_chunk += " " + word
            else:
                current_chunk += " " + sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _preprocess_text(self, text: str) -> str:
        """
        Clean and prepare text for translation
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove or replace problematic characters
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')
        text = text.replace('\t', ' ')
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _postprocess_translation(self, text: str, target_language: str) -> str:
        """
        Post-process translated text
        """
        # Clean up the translation
        text = text.strip()
        
        # Language-specific post-processing
        if target_language == "th":
            # Thai-specific cleaning
            text = self._clean_thai_text(text)
        
        return text
    
    def _clean_thai_text(self, text: str) -> str:
        """
        Clean Thai text translation
        """
        # Remove extra spaces around Thai text
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common Thai translation issues
        replacements = {
            ' ๆ': 'ๆ',
            ' ฯ': 'ฯ',
            ' ์': '์',
            ' ็': '็',
            ' ่': '่',
            ' ้': '้',
            ' ๊': '๊',
            ' ๋': '๋'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    async def detect_language(self, text: str) -> str:
        """
        Detect the language of input text
        """
        try:
            session = await self._get_session()
            
            data = {
                "q": text[:1000]  # Use first 1000 chars for detection
            }
            
            if self.api_key:
                data["api_key"] = self.api_key
            
            async with session.post(
                f"{self.base_url}/detect",
                json=data,
                timeout=10
            ) as response:
                
                if response.status != 200:
                    logger.warning("Language detection failed, using 'auto'")
                    return "auto"
                
                result = await response.json()
                detected_lang = result[0]["language"] if result else "auto"
                
                logger.info(f"Detected language: {detected_lang}")
                return detected_lang
                
        except Exception as e:
            logger.warning(f"Language detection failed: {str(e)}")
            return "auto"
    
    async def get_supported_languages(self) -> Dict[str, str]:
        """
        Get list of supported languages
        """
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/languages") as response:
                if response.status == 200:
                    languages = await response.json()
                    return {lang["code"]: lang["name"] for lang in languages}
                else:
                    # Return default supported languages
                    return settings.SUPPORTED_LANGUAGES
                    
        except Exception as e:
            logger.warning(f"Could not fetch supported languages: {str(e)}")
            return settings.SUPPORTED_LANGUAGES
    
    async def translate_with_context(self, text: str, context: str, target_language: str = "th") -> str:
        """
        Translate text with additional context for better accuracy
        """
        try:
            # Prepare context-aware prompt
            contextual_text = f"Context: {context}\n\nText to translate: {text}"
            
            # Use regular translation but with context
            result = await self.translate(contextual_text, target_language)
            
            # Extract just the translated part (remove context if it was translated too)
            lines = result.split('\n')
            if len(lines) > 1:
                # Try to find the actual translation
                for line in lines:
                    if line.strip() and not line.lower().startswith('context'):
                        return line.strip()
            
            return result
            
        except Exception as e:
            logger.warning(f"Context-aware translation failed, using regular translation: {str(e)}")
            return await self.translate(text, target_language)
    
    async def close(self):
        """
        Close the aiohttp session
        """
        if self.session and not self.session.closed:
            await self.session.close()