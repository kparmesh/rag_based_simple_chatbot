"""
Web Scraper for RAG-based Application using LangChain and OpenAI
This script scrapes zodiac sign data and prepares it for vector embeddings.
"""

import os
import json
from typing import List, Dict
from datetime import datetime

import requests
import ssl
import urllib.request
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# LangChain imports
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# BeautifulSoup for better parsing
from bs4 import BeautifulSoup



class ZodiacDataScraper:
    """Scrapes zodiac data and prepares it for RAG applications."""
    
    def __init__(self, api_key: str):
        """
        Initialize the scraper.
        
        Args:
            api_key: OpenAI API key for embeddings
        """
        self.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Set user agent to identify requests
        os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        self.embeddings = OpenAIEmbeddings()
        
        # Configure session with retries and SSL handling
        self.session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def scrape_urls(self, urls: List[str]) -> List[Document]:
        """
        Scrape content from URLs using requests and BeautifulSoup.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of Document objects
        """
        print(f"Scraping {len(urls)} URLs...")
        documents = []
        
        for url in urls:
            try:
                print(f"Processing: {url}")
                
                # Make request with SSL verification disabled (use with caution)
                response = self.session.get(url, verify=False, timeout=30)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text(separator=' ', strip=True)
                
                # Extract zodiac sign name from URL
                zodiac_name = url.split('/')[-1]
                
                # Create document
                doc = Document(
                    page_content=text,
                    metadata={
                        'source': url,
                        'scraped_at': datetime.now().isoformat(),
                        'zodiac_sign': zodiac_name,
                        'title': soup.title.string if soup.title else zodiac_name
                    }
                )
                
                documents.append(doc)
                print(f"✓ Successfully scraped: {url} ({len(text)} characters)")
                
            except requests.exceptions.SSLError as e:
                print(f"✗ SSL Error for {url}: {str(e)}")
                print(f"   Trying alternative method...")
                # Alternative: try with urllib
                try:
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    
                    req = urllib.request.Request(
                        url,
                        headers={'User-Agent': self.session.headers['User-Agent']}
                    )
                    
                    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                        html = response.read()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.decompose()
                        
                        text = soup.get_text(separator=' ', strip=True)
                        zodiac_name = url.split('/')[-1]
                        
                        doc = Document(
                            page_content=text,
                            metadata={
                                'source': url,
                                'scraped_at': datetime.now().isoformat(),
                                'zodiac_sign': zodiac_name,
                                'title': soup.title.string if soup.title else zodiac_name
                            }
                        )
                        documents.append(doc)
                        print(f"✓ Successfully scraped with alternative method: {url}")
                        
                except Exception as alt_error:
                    print(f"✗ Alternative method also failed: {str(alt_error)}")
                    
            except Exception as e:
                print(f"✗ Error scraping {url}: {str(e)}")
                
        return documents
    
    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """
        Clean and preprocess documents.
        
        Args:
            documents: Raw documents from scraping
            
        Returns:
            Cleaned documents
        """
        print("\nCleaning documents...")
        cleaned_docs = []
        
        for doc in documents:
            # Remove extra whitespace
            cleaned_text = ' '.join(doc.page_content.split())
            
            # Create new document with cleaned content
            cleaned_doc = Document(
                page_content=cleaned_text,
                metadata=doc.metadata
            )
            cleaned_docs.append(cleaned_doc)
            
        print(f"✓ Cleaned {len(cleaned_docs)} documents")
        return cleaned_docs
    
    def chunk_documents(
        self, 
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Document]:
        """
        Split documents into chunks for better embeddings.
        
        Args:
            documents: Documents to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            Chunked documents
        """
        print(f"\nChunking documents (size={chunk_size}, overlap={chunk_overlap})...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"✓ Created {len(chunks)} chunks from {len(documents)} documents")
        
        return chunks
    
    def save_to_json(self, documents: List[Document], filepath: str = "zodiac_data.json"):
        """
        Save documents to JSON format.
        
        Args:
            documents: Documents to save
            filepath: Output file path
        """
        print(f"\nSaving to JSON: {filepath}...")
        
        data = []
        for doc in documents:
            data.append({
                'content': doc.page_content,
                'metadata': doc.metadata
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Saved {len(data)} documents to {filepath}")
    
    def create_vector_store(
        self, 
        documents: List[Document],
        store_path: str = "zodiac_vectorstore"
    ) -> FAISS:
        """
        Create FAISS vector store from documents.
        
        Args:
            documents: Documents to embed
            store_path: Path to save vector store
            
        Returns:
            FAISS vector store
        """
        print(f"\nCreating vector store with OpenAI embeddings...")
        
        vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        # Save vector store locally
        vectorstore.save_local(store_path)
        print(f"✓ Vector store saved to: {store_path}")
        
        return vectorstore
    
    def load_vector_store(self, store_path: str = "zodiac_vectorstore") -> FAISS:
        """
        Load existing vector store.
        
        Args:
            store_path: Path to vector store
            
        Returns:
            FAISS vector store
        """
        print(f"\nLoading vector store from: {store_path}...")
        vectorstore = FAISS.load_local(
            store_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print("✓ Vector store loaded successfully")
        return vectorstore


def main():
    """Main execution function."""
    
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # URLs to scrape
    urls = [
        "https://vedischeshoroskop.de/zodic/widder",
        "https://vedischeshoroskop.de/zodic/stier",
        "https://vedischeshoroskop.de/zodic/zwillinge",
        "https://vedischeshoroskop.de/zodic/krebs",
        "https://vedischeshoroskop.de/zodic/lowe",
        "https://vedischeshoroskop.de/zodic/jungfrau",
        "https://vedischeshoroskop.de/zodic/waage",
        "https://vedischeshoroskop.de/zodic/skorpion",
        "https://vedischeshoroskop.de/zodic/schutze",
        "https://vedischeshoroskop.de/zodic/steinbock",
        "https://vedischeshoroskop.de/zodic/wassermann",
        "https://vedischeshoroskop.de/zodic/fische"
    ]
    
    # Set your OpenAI API key here
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") # Replace with your actual API key
    
    
    # Initialize scraper
    scraper = ZodiacDataScraper(api_key=OPENAI_API_KEY)
    
    # Step 1: Scrape URLs
    documents = scraper.scrape_urls(urls)
    
    if not documents:
        print("No documents scraped. Exiting.")
        return
    
    print(f"\n✓ Successfully scraped {len(documents)} documents")
    
    # Step 2: Clean documents
    cleaned_docs = scraper.clean_documents(documents)
    
    # Step 3: Chunk documents for better embeddings
    # chunked_docs = scraper.chunk_documents(
    #     cleaned_docs,
    #     chunk_size=1000,
    #     chunk_overlap=200
    # )
    
    # Step 4: Save to JSON (for reference and backup)
    scraper.save_to_json(cleaned_docs, "zodiac_data.json")
    
    # # Step 5: Create and save vector store
    # vectorstore = scraper.create_vector_store(
    #     chunked_docs,
    #     store_path="zodiac_vectorstore"
    # )
    
    # # Example: Test similarity search
    # print("\n" + "="*50)
    # print("Testing similarity search...")
    # print("="*50)
    
    # query = "Tell me about Aries personality"
    # results = vectorstore.similarity_search(query, k=3)
    
    # print(f"\nQuery: {query}")
    # print(f"\nTop {len(results)} results:")
    # for i, doc in enumerate(results, 1):
    #     print(f"\n{i}. Source: {doc.metadata.get('zodiac_sign', 'Unknown')}")
    #     print(f"   Content preview: {doc.page_content[:200]}...")
    
    print("\n✓ Script completed successfully!")
    print(f"✓ Generated files:")
    print(f"   - zodiac_data.json (structured data)")
    print(f"   - zodiac_vectorstore/ (FAISS vector database)")


if __name__ == "__main__":
    main()