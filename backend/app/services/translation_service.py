# backend/app/services/translation_service.py
import os
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
import re
from app.core.config import settings

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for text translation using LibreTranslate with fallback"""
    
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
        Translate text to target language with fallback
        """
        try:
            logger.info(f"Translating text to {target_language}")
            logger.info(f"Text length: {len(text)} characters")
            
            if not text or not text.strip():
                raise ValueError("Text to translate is empty")
            
            # Clean and prepare text
            cleaned_text = self._preprocess_text(text)
            
            # Try LibreTranslate first
            try:
                translated = await self._translate_with_libretranslate(cleaned_text, target_language, source_language)
                logger.info("Translation completed successfully with LibreTranslate")
                return translated
            except Exception as e:
                logger.warning(f"LibreTranslate failed: {str(e)}")
                
                # Fallback to simple translation
                translated = await self._translate_with_fallback(cleaned_text, target_language, source_language)
                logger.info("Translation completed with fallback method")
                return translated
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            raise Exception(f"Failed to translate text: {str(e)}")
    
    async def _translate_with_libretranslate(self, text: str, target_language: str, source_language: str) -> str:
        """
        Translate using LibreTranslate
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
                
        except Exception as e:
            logger.error(f"LibreTranslate translation failed: {str(e)}")
            raise e
    
    async def _translate_with_fallback(self, text: str, target_language: str, source_language: str) -> str:
        """
        Fallback translation using simple word replacement
        """
        try:
            logger.info("Using fallback translation method")
            
            # Simple English to Thai translation dictionary
            en_to_th = {
                "hello": "สวัสดี",
                "hi": "สวัสดี",
                "goodbye": "ลาก่อน",
                "thank you": "ขอบคุณ",
                "thanks": "ขอบคุณ",
                "please": "กรุณา",
                "yes": "ใช่",
                "no": "ไม่",
                "ok": "ตกลง",
                "okay": "ตกลง",
                "good": "ดี",
                "bad": "ไม่ดี",
                "big": "ใหญ่",
                "small": "เล็ก",
                "new": "ใหม่",
                "old": "เก่า",
                "time": "เวลา",
                "day": "วัน",
                "night": "คืน",
                "morning": "เช้า",
                "afternoon": "บ่าย",
                "evening": "เย็น",
                "today": "วันนี้",
                "tomorrow": "พรุ่งนี้",
                "yesterday": "เมื่อวาน",
                "now": "ตอนนี้",
                "here": "ที่นี่",
                "there": "ที่นั่น",
                "this": "นี่",
                "that": "นั่น",
                "what": "อะไร",
                "where": "ที่ไหน",
                "when": "เมื่อไหร่",
                "why": "ทำไม",
                "how": "อย่างไร",
                "who": "ใคร",
                "which": "อันไหน",
                "name": "ชื่อ",
                "work": "งาน",
                "home": "บ้าน",
                "family": "ครอบครัว",
                "friend": "เพื่อน",
                "love": "รัก",
                "like": "ชอบ",
                "want": "ต้องการ",
                "need": "ต้องการ",
                "can": "สามารถ",
                "will": "จะ",
                "should": "ควร",
                "must": "ต้อง",
                "may": "อาจ",
                "might": "อาจ",
                "could": "สามารถ",
                "would": "จะ",
                "do": "ทำ",
                "make": "ทำ",
                "go": "ไป",
                "come": "มา",
                "see": "เห็น",
                "look": "ดู",
                "watch": "ดู",
                "listen": "ฟัง",
                "hear": "ได้ยิน",
                "speak": "พูด",
                "talk": "พูด",
                "say": "พูด",
                "tell": "บอก",
                "ask": "ถาม",
                "answer": "ตอบ",
                "read": "อ่าน",
                "write": "เขียน",
                "learn": "เรียนรู้",
                "study": "เรียน",
                "teach": "สอน",
                "help": "ช่วย",
                "give": "ให้",
                "take": "เอา",
                "get": "ได้",
                "have": "มี",
                "be": "เป็น",
                "is": "เป็น",
                "are": "เป็น",
                "was": "เป็น",
                "were": "เป็น",
                "am": "เป็น",
                "been": "เป็น",
                "being": "เป็น",
                "the": "",
                "a": "",
                "an": "",
                "and": "และ",
                "or": "หรือ",
                "but": "แต่",
                "if": "ถ้า",
                "then": "แล้ว",
                "else": "อื่น",
                "because": "เพราะ",
                "so": "ดังนั้น",
                "very": "มาก",
                "much": "มาก",
                "many": "มาก",
                "few": "น้อย",
                "little": "น้อย",
                "more": "มากขึ้น",
                "less": "น้อยลง",
                "most": "มากที่สุด",
                "least": "น้อยที่สุด",
                "all": "ทั้งหมด",
                "some": "บาง",
                "any": "ใด",
                "none": "ไม่มี",
                "every": "ทุก",
                "each": "แต่ละ",
                "other": "อื่น",
                "another": "อีก",
                "same": "เหมือน",
                "different": "ต่าง",
                "same": "เหมือน",
                "first": "แรก",
                "last": "สุดท้าย",
                "next": "ถัดไป",
                "previous": "ก่อนหน้า",
                "before": "ก่อน",
                "after": "หลัง",
                "during": "ระหว่าง",
                "while": "ขณะที่",
                "since": "ตั้งแต่",
                "until": "จนกระทั่ง",
                "for": "สำหรับ",
                "from": "จาก",
                "to": "ถึง",
                "in": "ใน",
                "on": "บน",
                "at": "ที่",
                "by": "โดย",
                "with": "กับ",
                "without": "โดยไม่มี",
                "about": "เกี่ยวกับ",
                "against": "ต่อต้าน",
                "between": "ระหว่าง",
                "among": "ในหมู่",
                "through": "ผ่าน",
                "across": "ข้าม",
                "into": "เข้าไปใน",
                "onto": "ขึ้นไปบน",
                "upon": "บน",
                "within": "ภายใน",
                "without": "โดยไม่มี",
                "behind": "ข้างหลัง",
                "below": "ข้างล่าง",
                "beneath": "ใต้",
                "beside": "ข้าง",
                "beyond": "เกิน",
                "inside": "ข้างใน",
                "outside": "ข้างนอก",
                "over": "เหนือ",
                "under": "ใต้",
                "above": "เหนือ",
                "below": "ใต้",
                "up": "ขึ้น",
                "down": "ลง",
                "left": "ซ้าย",
                "right": "ขวา",
                "front": "หน้า",
                "back": "หลัง",
                "top": "บน",
                "bottom": "ล่าง",
                "center": "กลาง",
                "middle": "กลาง",
                "side": "ด้าน",
                "end": "จบ",
                "begin": "เริ่ม",
                "start": "เริ่ม",
                "stop": "หยุด",
                "finish": "เสร็จ",
                "complete": "เสร็จสิ้น",
                "continue": "ต่อ",
                "begin": "เริ่ม",
                "start": "เริ่ม",
                "end": "จบ",
                "finish": "เสร็จ",
                "complete": "เสร็จสิ้น",
                "continue": "ต่อ",
                "begin": "เริ่ม",
                "start": "เริ่ม",
                "end": "จบ",
                "finish": "เสร็จ",
                "complete": "เสร็จสิ้น",
                "continue": "ต่อ"
            }
            
            # Simple translation logic
            if target_language == "th" and source_language in ["en", "auto"]:
                # Convert to lowercase for matching
                text_lower = text.lower()
                
                # Replace known words
                translated_text = text
                for en_word, th_word in en_to_th.items():
                    # Use word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(en_word) + r'\b'
                    translated_text = re.sub(pattern, th_word, translated_text, flags=re.IGNORECASE)
                
                # If no translation found, return original with note
                if translated_text == text:
                    logger.warning("No translation found in fallback dictionary")
                    return f"[แปลไม่ได้] {text}"
                
                return translated_text
            else:
                # For other languages, return original with note
                logger.warning(f"Fallback translation not supported for {source_language} to {target_language}")
                return f"[แปลไม่ได้] {text}"
                
        except Exception as e:
            logger.error(f"Fallback translation failed: {str(e)}")
            return f"[แปลไม่ได้] {text}"
    
    async def _translate_long_text(self, text: str, target_language: str, source_language: str) -> str:
        """
        Translate long text by splitting into chunks
        """
        try:
            # Split text into chunks
            chunks = self._split_text_intelligently(text)
            translated_chunks = []
            
            for chunk in chunks:
                if len(chunk) > 5000:
                    # For very long chunks, use fallback
                    translated = await self._translate_with_fallback(chunk, target_language, source_language)
                else:
                    # Try LibreTranslate first, then fallback
                    try:
                        translated = await self._translate_with_libretranslate(chunk, target_language, source_language)
                    except:
                        translated = await self._translate_with_fallback(chunk, target_language, source_language)
                
                translated_chunks.append(translated)
            
            # Join translated chunks
            return " ".join(translated_chunks)
            
        except Exception as e:
            logger.error(f"Long text translation failed: {str(e)}")
            raise e
    
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
        
        # Remove common transcription artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove [speaker], [music], etc.
        text = re.sub(r'\(.*?\)', '', text)  # Remove parenthetical notes
        
        # Clean up punctuation for better translation
        text = re.sub(r'\.{2,}', '.', text)  # Multiple periods
        text = re.sub(r'!{2,}', '!', text)   # Multiple exclamations
        text = re.sub(r'\?{2,}', '?', text)  # Multiple questions
        
        # Ensure proper sentence ending
        text = text.strip()
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text
    
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