import os
import io
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
import streamlit as st
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
from transformers import GPT2Tokenizer
from PIL import Image
import pytesseract
import cv2
import numpy as np
import tempfile
import sys
import warnings
import traceback
import logging
import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable Chroma telemetry
client = chromadb.Client(Settings(anonymized_telemetry=False))

# Load environment variables
load_dotenv()

# Check Tesseract availability and configure it
TESSERACT_AVAILABLE = False
try:
    if sys.platform.startswith('win'):
        # Try to find Tesseract in common installation paths
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                TESSERACT_AVAILABLE = True
                break
    else:
        # On Unix-like systems, try to use system installation
        import shutil

        if shutil.which('tesseract'):
            TESSERACT_AVAILABLE = True
except Exception as e:
    st.warning("Tesseract OCR is not available. Image text extraction will be disabled.")

# Suppress specific warnings
warnings.filterwarnings('ignore', message='`resume_download` is deprecated')

# Initialize tokenizer and constants
tokenizer = GPT2Tokenizer.from_pretrained("gpt2", force_download=False)
MAX_TOKENS = 512  # Reduced from 1024 to ensure we stay well under limits
CHUNK_SIZE = 256  # Reduced chunk size for better handling


def safe_encode(text: str) -> List[int]:
    """Safely encode text, handling potential encoding errors"""
    try:
        return tokenizer.encode(text, truncation=True, max_length=MAX_TOKENS)
    except Exception:
        # If encoding fails, try with a clean version of the text
        clean_text = ' '.join(text.split())  # Remove extra whitespace
        return tokenizer.encode(clean_text, truncation=True, max_length=MAX_TOKENS)


def truncate_text(text: str, max_tokens: int = MAX_TOKENS) -> str:
    """Truncate text to fit within token limit"""
    if not text:
        return ""
    try:
        tokens = safe_encode(text)
        if len(tokens) <= max_tokens:
            return text
        return tokenizer.decode(tokens[:max_tokens], skip_special_tokens=True)
    except Exception as e:
        st.warning(f"Warning: Error during text truncation. Using fallback method.")
        # Fallback: truncate by characters
        return text[:max_tokens * 4]  # Approximate 4 characters per token


def chunk_content(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """Split content into smaller chunks while preserving meaning"""
    if not text:
        return []

    try:
        tokens = safe_encode(text)
        chunks = []

        for i in range(0, len(tokens), chunk_size):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            if chunk_text.strip():
                chunks.append(chunk_text)

        return chunks
    except Exception as e:
        st.warning(f"Warning: Error during content chunking. Using fallback method.")
        # Fallback: split by sentences
        sentences = text.split('.')
        current_chunk = ""
        chunks = []

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size * 4:
                current_chunk += sentence + "."
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + "."

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


class BlogScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.site_metadata = {}
        if not TESSERACT_AVAILABLE:
            st.info(
                "📝 Note: Tesseract OCR is not installed. Only image descriptions will be processed. To enable text extraction from images, please install Tesseract OCR.")

    def process_image(self, img_url: str) -> str:
        """Process an image and extract text using OCR if available"""
        try:
            # Download image
            response = requests.get(img_url)
            if response.status_code != 200:
                return ""

            # Convert to PIL Image
            img = Image.open(io.BytesIO(response.content))

            if not TESSERACT_AVAILABLE:
                return ""  # Skip OCR if Tesseract is not available

            # Convert to OpenCV format for preprocessing
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            # Preprocess image
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Perform OCR
            text = pytesseract.image_to_string(gray)
            return text.strip()
        except Exception as e:
            if TESSERACT_AVAILABLE:
                st.error(f"Error processing image {img_url}: {str(e)}")
            return ""

    def extract_images_and_text(self, soup) -> List[Tuple[str, str]]:
        """Extract images and their alt text from HTML"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src and not src.endswith(('.ico', '.svg')):  # Exclude icons and SVGs
                if not src.startswith(('http://', 'https://')):
                    src = self.base_url.rstrip('/') + '/' + src.lstrip('/')
                if alt.strip():  # Only include images with alt text if Tesseract is not available
                    images.append((src, alt))
                elif TESSERACT_AVAILABLE:
                    images.append((src, alt))
        return images

    def extract_social_links(self, soup) -> Dict[str, str]:
        """Extract social media links from the blog"""
        social_links = {}

        # Common patterns for social links
        social_patterns = {
            'github': ['github.com', 'github.io'],
            'linkedin': ['linkedin.com'],
            'twitter': ['twitter.com', 'x.com'],
            'instagram': ['instagram.com'],
            'facebook': ['facebook.com']
        }

        # Look for social links in common locations
        potential_link_containers = soup.select(
            '.social, .social-links, .footer, .header, .sidebar, nav, .follow-by-email-inner')

        for container in potential_link_containers:
            links = container.find_all('a', href=True)
            for link in links:
                href = link.get('href', '').lower()
                for platform, domains in social_patterns.items():
                    if any(domain in href for domain in domains):
                        social_links[platform] = href

        # Also look for any link with these domains anywhere in the page
        if not social_links:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '').lower()
                for platform, domains in social_patterns.items():
                    if any(domain in href for domain in domains):
                        social_links[platform] = href

        return social_links

    def extract_site_metadata(self, soup) -> Dict[str, str]:
        """Extract general site metadata"""
        metadata = {}

        # Try to find site description
        description_tags = soup.select('meta[name="description"], meta[property="og:description"]')
        if description_tags:
            metadata['site_description'] = description_tags[0].get('content', '')

        # Try to find site title
        title_tags = soup.select('meta[property="og:title"], title')
        if title_tags:
            metadata['site_title'] = title_tags[0].get('content', '') or title_tags[0].string

        return metadata

    def process_content(self, content: str) -> str:
        """Process and clean content to fit within token limits"""
        if not content:
            return ""

        # Clean the content first
        content = ' '.join(content.split())  # Remove extra whitespace

        try:
            # If content is within limits, return as is
            if len(safe_encode(content)) <= MAX_TOKENS:
                return content

            # Split into chunks and take the most relevant part
            chunks = chunk_content(content)
            if chunks:
                # Take first chunk and ensure it's within limits
                return truncate_text(chunks[0])

            # Fallback to simple truncation
            return truncate_text(content)
        except Exception as e:
            st.warning(f"Warning: Error during content processing. Using basic truncation.")
            return content[:MAX_TOKENS * 4]  # Fallback to character-based truncation

    def get_blog_posts(self) -> List[Dict[str, str]]:
        """Scrape blog posts and site metadata from the website"""
        try:
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract social links and metadata first
            social_links = self.extract_social_links(soup)
            site_metadata = self.extract_site_metadata(soup)

            # Create a special "About" document with metadata
            about_content = []
            if site_metadata:
                about_content.append("Site Information:")
                for key, value in site_metadata.items():
                    about_content.append(f"{key}: {value}")

            if social_links:
                about_content.append("\nSocial Links and Profiles:")
                for platform, url in social_links.items():
                    about_content.append(f"{platform.title()} Profile: {url}")

            blog_posts = []

            # Add the about/metadata content as a special document
            if about_content:
                blog_posts.append({
                    'title': 'About TeachLea and Social Links',
                    'content': '\n'.join(about_content),
                    'url': self.base_url
                })

            # Find all blog post links
            posts_container = soup.find('div', class_='blog-posts hfeed container index-post-wrap')

            if posts_container:
                posts = posts_container.find_all('div', class_='blog-post hentry index-post')

                for post in posts:
                    try:
                        # Get post info container
                        post_info = post.find('div', class_='post-info')

                        if post_info:
                            # Get title
                            title_elem = post_info.find('h2', class_='post-title')

                            # Get content (snippet)
                            content_elem = post_info.find('p', class_='post-snippet')

                            # Get URL
                            url = ''
                            if title_elem and title_elem.find('a'):
                                url = title_elem.find('a').get('href', '')

                            if title_elem and content_elem:
                                title = title_elem.get_text().strip()
                                content = content_elem.get_text().strip()

                                # Get full post content if available
                                if url:
                                    try:
                                        full_post_response = requests.get(url)
                                        full_post_soup = BeautifulSoup(full_post_response.text, 'html.parser')

                                        # Try to find the main content area
                                        content_selectors = [
                                            'div.post-body.entry-content',
                                            'div.entry-content',
                                            'article',
                                            'div.post-content'
                                        ]

                                        full_content_elem = None
                                        for selector in content_selectors:
                                            full_content_elem = full_post_soup.select_one(selector)
                                            if full_content_elem:
                                                break

                                        if full_content_elem:
                                            # Get text content and clean it
                                            content = ' '.join(full_content_elem.get_text().split())
                                            # Process content to fit within token limits
                                            content = self.process_content(content)

                                            # Extract links with length checking
                                            content_links = full_content_elem.find_all('a', href=True)
                                            if content_links:
                                                links_text = "\n\nRelevant Links:\n"
                                                for link in content_links[:5]:  # Limit to top 5 links
                                                    link_text = link.get_text().strip()
                                                    link_url = link.get('href')
                                                    if link_url and link_text:
                                                        links_text += f"{link_text}: {link_url}\n"

                                                # Only add links if total content stays within limits
                                                if len(safe_encode(content + links_text)) <= MAX_TOKENS:
                                                    content = content + links_text

                                            # Process images with strict limits
                                            images = self.extract_images_and_text(full_content_elem)
                                            image_texts = []

                                            for img_url, alt_text in images[:3]:  # Limit to top 3 images
                                                ocr_text = self.process_image(img_url)
                                                if ocr_text or alt_text:
                                                    image_text = "Image Content:\n"
                                                    if alt_text:
                                                        image_text += f"Description: {alt_text}\n"
                                                    if ocr_text:
                                                        image_text += f"Text from image: {ocr_text}\n"
                                                    image_texts.append(image_text)

                                            # Add image content while respecting token limits
                                            if image_texts:
                                                combined_text = content + "\n\n" + "\n\n".join(image_texts)
                                                if len(safe_encode(combined_text)) <= MAX_TOKENS:
                                                    content = combined_text
                                                else:
                                                    # If too long, just keep the main content
                                                    content = self.process_content(content)
                                    except Exception as e:
                                        # If we can't get the full post, use the snippet
                                        pass

                                blog_posts.append({
                                    'title': title,
                                    'content': content,
                                    'url': url if url.startswith('http') else (
                                            self.base_url.rstrip('/') + '/' + url.lstrip('/'))
                                })
                    except Exception as e:
                        continue

            if not blog_posts or len(blog_posts) == 1:  # Only the About document
                # Try finding links that look like blog posts
                all_links = soup.find_all('a', href=True)
                blog_post_links = [
                    link for link in all_links
                    if any(pattern in link.get('href', '').lower()
                           for pattern in ['/blog/', '/post/', '/article/', '.html'])
                ]

                for link in blog_post_links:
                    try:
                        url = link.get('href')
                        if not url.startswith(('http://', 'https://')):
                            url = self.base_url.rstrip('/') + '/' + url.lstrip('/')

                        try:
                            post_response = requests.get(url)
                            post_soup = BeautifulSoup(post_response.text, 'html.parser')

                            # Try to find title
                            title_elem = (
                                    post_soup.find(['h1', 'h2'], class_=['post-title', 'entry-title']) or
                                    post_soup.find(['h1', 'h2'])
                            )

                            if title_elem:
                                title = title_elem.get_text().strip()

                                # Try different content selectors
                                content_selectors = [
                                    'div.post-body',
                                    'div.entry-content',
                                    'article',
                                    'div.post-content',
                                    'div.article-content',
                                    'div.content'
                                ]

                                full_content_elem = None
                                for selector in content_selectors:
                                    elements = post_soup.select(selector)
                                    if elements:
                                        # Use the largest content block found
                                        full_content_elem = max(elements, key=lambda e: len(e.get_text()))
                                        break

                                if full_content_elem:
                                    content = ' '.join(full_content_elem.get_text().split())
                                    # Process content to fit within token limits
                                    content = self.process_content(content)

                                    # Extract links with length checking
                                    content_links = full_content_elem.find_all('a', href=True)
                                    if content_links:
                                        links_text = "\n\nRelevant Links:\n"
                                        for link in content_links[:5]:  # Limit to top 5 links
                                            link_text = link.get_text().strip()
                                            link_url = link.get('href')
                                            if link_url and link_text:
                                                links_text += f"{link_text}: {link_url}\n"

                                        # Only add links if total content stays within limits
                                        if len(safe_encode(content + links_text)) <= MAX_TOKENS:
                                            content = content + links_text

                                    # Process images with strict limits
                                    images = self.extract_images_and_text(full_content_elem)
                                    image_texts = []

                                    for img_url, alt_text in images[:3]:  # Limit to top 3 images
                                        ocr_text = self.process_image(img_url)
                                        if ocr_text or alt_text:
                                            image_text = "Image Content:\n"
                                            if alt_text:
                                                image_text += f"Description: {alt_text}\n"
                                            if ocr_text:
                                                image_text += f"Text from image: {ocr_text}\n"
                                            image_texts.append(image_text)

                                    # Add image content while respecting token limits
                                    if image_texts:
                                        combined_text = content + "\n\n" + "\n\n".join(image_texts)
                                        if len(safe_encode(combined_text)) <= MAX_TOKENS:
                                            content = combined_text
                                        else:
                                            # If too long, just keep the main content
                                            content = self.process_content(content)

                                    blog_posts.append({
                                        'title': title,
                                        'content': content,
                                        'url': url
                                    })
                        except Exception as e:
                            continue
                    except Exception as e:
                        continue

            return blog_posts

        except Exception as e:
            return []


class TeachleaBot:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")

        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vector_store = None
        self.chat_model = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            openai_api_key=self.openai_api_key
        )

    def create_vector_store(self, blog_posts: List[Dict[str, str]]):
        """Create vector store from blog posts"""
        try:
            st.info("Creating vector store...")
            documents = []
            for post in blog_posts:
                # Process content to fit within token limits
                content = self.process_content(post['content'])

                doc = Document(
                    page_content=f"Title: {post['title']}\n\nContent: {content}",
                    metadata={"source": post['url'], "title": post['title']}
                )
                documents.append(doc)

            # Create a temporary directory for the vector store
            persist_directory = os.path.join(tempfile.gettempdir(), "chroma_db")
            os.makedirs(persist_directory, exist_ok=True)

            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=persist_directory,
                client_settings=Settings(
                    anonymized_telemetry=False,
                    is_persistent=True
                )
            )
            st.success("Vector store created successfully!")

        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            logger.error(f"Vector store creation error: {traceback.format_exc()}")
            raise

    def setup_retrieval_chain(self):
        """Set up the conversational retrieval chain"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")

        return ConversationalRetrievalChain.from_llm(
            llm=self.chat_model,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True
        )

    def process_content(self, content: str) -> str:
        """Process content to fit within token limits"""
        return truncate_text(content)


def initialize_app():
    """Initialize the application with proper error handling"""
    try:
        st.info("🚀 Starting application initialization...")

        # Check OpenAI API key
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            st.error("❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            return None

        # Initialize bot
        st.info("📚 Initializing TeachLea Bot...")
        bot = TeachleaBot()

        # Initialize scraper and get blog posts
        st.info("🔍 Fetching blog content...")
        scraper = BlogScraper("https://www.teachlea.com")
        blog_posts = scraper.get_blog_posts()

        if not blog_posts:
            st.error("❌ No blog posts found. Please check the website URL and try again.")
            return None

        st.info(f"📝 Found {len(blog_posts)} blog posts. Creating vector store...")
        try:
            bot.create_vector_store(blog_posts)
        except Exception as e:
            st.error(f"❌ Error creating vector store: {str(e)}")
            return None

        st.info("⚙️ Setting up retrieval chain...")
        try:
            chain = bot.setup_retrieval_chain()
        except Exception as e:
            st.error(f"❌ Error setting up retrieval chain: {str(e)}")
            return None

        st.success("✅ Application initialized successfully!")
        return bot, chain

    except Exception as e:
        st.error(f"❌ Error during initialization: {str(e)}")
        logger.error(f"Initialization error: {traceback.format_exc()}")
        return None


def main():
    # Set page config
    st.set_page_config(
        page_title="TeachLea Blog Assistant",
        page_icon="🤖",
        layout="wide"
    )

    # Custom CSS for better UI
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .chat-message {
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .user-message {
            background-color: #e6f3ff;
            border-left: 4px solid #2196F3;
        }
        .bot-message {
            background-color: #f0f2f6;
            border-left: 4px solid #4CAF50;
        }
        .message-content {
            margin-top: 0.5rem;
            line-height: 1.5;
        }
        .main-title {
            text-align: center;
            color: #1E88E5;
            margin-bottom: 2rem;
            font-size: 2rem;
            font-weight: 600;
        }
        .error-message {
            color: #f44336;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #ffebee;
            margin: 1rem 0;
        }
        .info-message {
            color: #1976D2;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #e3f2fd;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

    # Main title with custom styling
    st.markdown("<h1 class='main-title'>TeachLea Blog Assistant 🤖</h1>", unsafe_allow_html=True)

    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.chat_history = []
        st.session_state.question_key = 0
        st.session_state.bot = None
        st.session_state.chain = None

    # Initialize the application if not already done
    if not st.session_state.initialized:
        with st.spinner('Initializing application...'):
            result = initialize_app()
            if result:
                st.session_state.bot, st.session_state.chain = result
                st.session_state.initialized = True
            else:
                st.error("❌ Failed to initialize application. Please check the logs and try again.")
                return

    # Create two columns for better layout
    col1, col2 = st.columns([3, 1])

    with col1:
        # Chat interface with auto-clearing
        user_question = st.text_input(
            "Ask a question about TeachLea blog content:",
            key=f"question_{st.session_state.question_key}"
        )

    with col2:
        # Clear chat button
        if st.button("Clear Chat History 🗑️"):
            st.session_state.chat_history = []
            st.session_state.question_key += 1
            st.experimental_rerun()

    if user_question:
        try:
            # Show spinner while processing
            with st.spinner('Processing your question...'):
                response = st.session_state.chain(
                    {"question": user_question,
                     "chat_history": st.session_state.chat_history}
                )

            # Update chat history
            st.session_state.chat_history.append({
                'question': user_question,
                'answer': response['answer'],
                'sources': [
                    {'title': doc.metadata.get('title', ''),
                     'url': doc.metadata.get('source', '')}
                    for doc in response.get('source_documents', [])
                ]
            })

            # Increment question key to clear input
            st.session_state.question_key += 1

        except Exception as e:
            st.error(f"❌ Error processing question: {str(e)}")
            logger.error(f"Question processing error: {traceback.format_exc()}")

    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            # User message
            st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong>
                    <div class="message-content">{message['question']}</div>
                </div>
            """, unsafe_allow_html=True)

            # Bot message
            st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>Assistant:</strong>
                    <div class="message-content">{message['answer']}</div>
                </div>
            """, unsafe_allow_html=True)

            # Display sources if available
            if message['sources']:
                with st.expander("📚 View Sources", expanded=True):
                    st.markdown("""
                    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1E88E5;'>
                        <h4 style='color: #1E88E5; margin-top: 0;'>Referenced Articles</h4>
                    </div>
                    """, unsafe_allow_html=True)

                    # Use a set to store unique URLs
                    seen_urls = set()
                    for idx, source in enumerate(message['sources'], 1):
                        url = source['url']
                        if url not in seen_urls:
                            seen_urls.add(url)
                            st.markdown(
                                f"{idx}. [{source['title']}]({url})",
                                unsafe_allow_html=False
                            )
                    st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("---")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        logger.error(f"Application error: {traceback.format_exc()}")