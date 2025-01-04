import os
import streamlit as st
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from dotenv import load_dotenv
load_dotenv()
# Set your OpenAI API key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Streamlit UI
st.title("PDF RAG Chatbot with FAISS")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Processing the PDF..."):
        # Load PDF and split into pages
        loader = PyPDFLoader(uploaded_file)
        pages = loader.load()

        # Generate embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

        # Create FAISS vector store
        vector_store = FAISS.from_documents(pages, embeddings)

        # Create Conversational Retrieval Chain
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        qa_chain = ConversationalRetrievalChain.from_llm(OpenAI(openai_api_key=openai.api_key), retriever)

    st.success("PDF processed. Start asking questions!")
    chat_history = []

    # Chat loop
    user_input = st.text_input("Ask a question:")
    if user_input:
        with st.spinner("Generating response..."):
            response = qa_chain({"question": user_input, "chat_history": chat_history})
            chat_history.append((user_input, response["answer"]))
            st.write(f"**Q:** {user_input}")
            st.write(f"**A:** {response['answer']}")
