import streamlit as st
import openai
# import os
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
# import redis
import pysqlite3

# Initialize a Redis client (replace with your own configuration)
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
# from dotenv import load_dotenv
# load_dotenv()
# Set up OpenAI API key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to create a vector database
def create_vector_database(text):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
    vectordb = Chroma.from_texts(chunks, embeddings)
    return vectordb

# Function to perform RAG-based retrieval and generation
def get_rag_response(user_query, vectordb):
    docs = vectordb.similarity_search(user_query, k=3)  # Retrieve top-3 relevant chunks
    context = "\n".join([doc.page_content for doc in docs])

    prompt = (
        f"You are a helpful assistant. Use the following context to answer the question:\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {user_query}\n"
        f"Answer:"
    )
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=200,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error: {e}"

# Streamlit app
st.title("PDF Chatbot with RAG")
st.write("Upload a PDF file and ask questions about its content.")

# PDF upload
pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
if pdf_file:
    st.session_state["pdf_text"] = extract_text_from_pdf(pdf_file)
    st.success("PDF uploaded and processed!")

# Initialize vector database
if "pdf_text" in st.session_state:
    vectordb = create_vector_database(st.session_state["pdf_text"])

# Chat interface
if "pdf_text" in st.session_state:
    user_query = st.text_input("Ask a question about the PDF:")
    if st.button("Submit"):
        if user_query:
            response = get_rag_response(user_query, vectordb)
            st.write(f"**Answer:** {response}")