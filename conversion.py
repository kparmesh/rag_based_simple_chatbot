"""
Translate Zodiac Data from German to English using OpenAI
This script translates the scraped German zodiac content to English.
"""

import json
import os
from typing import List, Dict
from openai import OpenAI
import time

class ZodiacTranslator:
    """Translates zodiac data from German to English."""
    
    def __init__(self, api_key: str):
        """
        Initialize the translator.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.zodiac_name_mapping = {
            'widder': 'aries',
            'stier': 'taurus',
            'zwillinge': 'gemini',
            'krebs': 'cancer',
            'lowe': 'leo',
            'jungfrau': 'virgo',
            'waage': 'libra',
            'skorpion': 'scorpio',
            'schutze': 'sagittarius',
            'steinbock': 'capricorn',
            'wassermann': 'aquarius',
            'fische': 'pisces'
        }
    
    def translate_text(self, text: str, max_retries: int = 3) -> str:
        """
        Translate text from German to English using OpenAI.
        
        Args:
            text: German text to translate
            max_retries: Maximum number of retry attempts
            
        Returns:
            Translated English text
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # More cost-effective for translation
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional translator. Translate the following German text about astrology and zodiac signs to English. Maintain the original meaning, tone, and structure. Only provide the translation without any explanations or additional text."
                        },
                        {
                            "role": "user",
                            "content": f"Translate this German text to English:\n\n{text}"
                        }
                    ],
                    temperature=0.3,  # Lower temperature for more consistent translations
                    max_tokens=4000
                )
                
                translated_text = response.choices[0].message.content.strip()
                return translated_text
                
            except Exception as e:
                print(f"   ⚠ Translation attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"   Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"   ✗ Translation failed after {max_retries} attempts")
                    return text  # Return original text if translation fails
    
    def translate_batch(self, texts: List[str], batch_size: int = 5) -> List[str]:
        """
        Translate multiple texts in batches to avoid rate limits.
        
        Args:
            texts: List of German texts to translate
            batch_size: Number of texts to process before a pause
            
        Returns:
            List of translated English texts
        """
        translated_texts = []
        total = len(texts)
        
        for i, text in enumerate(texts, 1):
            print(f"Translating chunk {i}/{total}...")
            
            # Skip if text is too short (likely metadata or empty)
            if len(text.strip()) < 20:
                translated_texts.append(text)
                continue
            
            translated = self.translate_text(text)
            translated_texts.append(translated)
            
            # Add delay between batches to avoid rate limits
            if i % batch_size == 0 and i < total:
                print(f"   Pausing for rate limit management...")
                time.sleep(2)
        
        return translated_texts
    
    def translate_zodiac_data(
        self, 
        input_file: str = "zodiac_data.json",
        output_file: str = "zodiac_data_english.json"
    ) -> Dict:
        """
        Translate entire zodiac data JSON file.
        
        Args:
            input_file: Path to German zodiac data JSON
            output_file: Path to save English zodiac data JSON
            
        Returns:
            Translated data dictionary
        """
        print(f"Loading data from: {input_file}")
        
        # Load German data
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                german_data = json.load(f)
        except FileNotFoundError:
            print(f"✗ Error: File '{input_file}' not found!")
            return None
        
        print(f"✓ Loaded {len(german_data)} documents")
        print(f"\nStarting translation...\n")
        
        translated_data = []
        
        for i, doc in enumerate(german_data, 1):
            print(f"Processing document {i}/{len(german_data)}")
            
            # Translate content
            original_content = doc['content']
            translated_content = self.translate_text(original_content)
            
            # Update metadata
            metadata = doc['metadata'].copy()
            
            # Translate zodiac sign name
            german_sign = metadata.get('zodiac_sign', '')
            if german_sign in self.zodiac_name_mapping:
                metadata['zodiac_sign_english'] = self.zodiac_name_mapping[german_sign]
                metadata['zodiac_sign_german'] = german_sign
            
            # Add translation metadata
            metadata['original_language'] = 'de'
            metadata['translated_language'] = 'en'
            metadata['translated_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Create translated document
            translated_doc = {
                'content': translated_content,
                'content_german': original_content,  # Keep original for reference
                'metadata': metadata
            }
            
            translated_data.append(translated_doc)
            print(f"✓ Document {i} translated successfully\n")
        
        # Save translated data
        print(f"Saving translated data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Translation complete! Saved to {output_file}")
        
        # Print statistics
        total_chars_original = sum(len(doc['content_german']) for doc in translated_data)
        total_chars_translated = sum(len(doc['content']) for doc in translated_data)
        
        print(f"\nTranslation Statistics:")
        print(f"  - Total documents: {len(translated_data)}")
        print(f"  - Original characters: {total_chars_original:,}")
        print(f"  - Translated characters: {total_chars_translated:,}")
        print(f"  - Average document length: {total_chars_translated // len(translated_data):,} chars")
        
        return translated_data
    
    def create_english_only_version(
        self,
        translated_file: str = "zodiac_data_english.json",
        output_file: str = "zodiac_data_english_only.json"
    ):
        """
        Create a version with only English content (no German).
        
        Args:
            translated_file: Path to translated data with both languages
            output_file: Path to save English-only version
        """
        print(f"\nCreating English-only version...")
        
        with open(translated_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        english_only = []
        for doc in data:
            # Remove German content, keep only English
            english_doc = {
                'content': doc['content'],
                'metadata': doc['metadata']
            }
            english_only.append(english_doc)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(english_only, f, ensure_ascii=False, indent=2)
        
        print(f"✓ English-only version saved to: {output_file}")


from backend.core.config import settings

def main():
    """Main execution function."""
    
    # Set your OpenAI API key
    OPENAI_API_KEY = settings.openai_api_key  # Replace with your actual API key

    print(OPENAI_API_KEY)

    # Initialize translator
    translator = ZodiacTranslator(api_key=OPENAI_API_KEY)
    
    # Translate the zodiac data
    translated_data = translator.translate_zodiac_data(
        input_file="zodiac_data.json",
        output_file="zodiac_data_english.json"
    )
    
    if translated_data:
        # Create English-only version (without German text)
        translator.create_english_only_version(
            translated_file="zodiac_data_english.json",
            output_file="zodiac_data_english_only.json"
        )
        
        print("\n" + "="*50)
        print("Translation Complete!")
        print("="*50)
        print("\nGenerated files:")
        print("  1. zodiac_data_english.json - Full translation with German backup")
        print("  2. zodiac_data_english_only.json - English only (for RAG use)")
        print("\nYou can now use the English version for your RAG application!")


if __name__ == "__main__":
    main()