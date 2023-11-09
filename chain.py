import time
import sys
import os
from os import listdir
from os.path import isfile, join
import langchain
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceHubEmbeddings, OpenAIEmbeddings
from langchain.llms import HuggingFaceHub, OpenAI
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings

VECTOR_STORE_DIR = "./vector_db"
DOC_PATH = "./documents/"

embedding_function = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

def load_documents(doc_path):
    documents = []
    if os.path.isdir(doc_path):
        for root, dirs, files in os.walk(doc_path):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_path = os.path.join(root, file)
                    loader = PyPDFLoader(pdf_path)
                    documents.extend(loader.load())
                elif file.endswith('.docx'):
                    docx_path = os.path.join(root, file)
                    loader = Docx2txtLoader(docx_path)
                    documents.extend(loader.load())
                elif file.endswith('.txt'):
                    text_path = os.path.join(root, file)
                    loader = TextLoader(text_path)
                    documents.extend(loader.load())
    return documents

def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    print(chunks)
    return chunks

def load_vectordb():
    vectordb = None
    if os.path.isdir(VECTOR_STORE_DIR):
        try:
            vectordb = Chroma(
                persist_directory=VECTOR_STORE_DIR,
                collection_name="demo1",
                embedding_function=embedding_function
            )
        except FileNotFoundError:
            print("Vectordb not found!")
            vectordb = None
    return vectordb

def add_vectordb(documents, vectordb):
    # embeddings = OpenAIEmbeddings()
 
    if vectordb is None:
        vectordb = Chroma.from_documents(
            documents,
            embedding=embedding_function,
            collection_name="demo1",
            persist_directory=VECTOR_STORE_DIR)
    else:
        vectordb.add_documents(
            documents, 
            collection_name="demo1",
            embeddings=embedding_function)
    
    vectordb.persist()
    return vectordb


def get_conversation_chain(vectordb):
    # llm = HuggingFaceHub(
    #     repo_id="google/flan-t5-xxl",
    #     model_kwargs={"temperature":0.7, "max_length":512}
    # )
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        input_key='question',
        output_key='answer',
        return_messages=True)
    
    system_template = """
    Strictly Use ONLY the following pieces of context to answer the question at the end. Think step-by-step and then answer.

    Do not try to make up an answer:
    - If the answer to the question cannot be determined from the context alone, say "I cannot determine the answer to that."
    - If the context is empty, just say "I do not know the answer to that."

    -------------------
    
    {context}
    """
    
    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}")]
    prompt = ChatPromptTemplate.from_messages(messages)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectordb.as_retriever(
            search_kwargs={'fetch_k': 4, 'k': 3}, search_type='mmr'),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return conversation_chain

def create_chain():
    load_dotenv()
    vectordb = load_vectordb()
    pdf_qa = get_conversation_chain(vectordb)
    return pdf_qa

def get_response(chain, question: str):
    response = chain({"question": question})
    return response

def main():
    load_dotenv()

    vectordb = load_vectordb()
    #Load docs
    # documents = load_documents(DOC_PATH)
    # text_chunks = split_documents(documents)
    # vectordb = add_vectordb(text_chunks, vectordb)

    pdf_qa = get_conversation_chain(vectordb)

    yellow = "\033[0;33m"
    green = "\033[0;32m"
    white = "\033[0;39m"

    # chat_history = []
    print(f"{yellow}---------------------------------------------------------------------------------")
    print('Welcome to the DocBot. You are now ready to start interacting with your documents')
    print('---------------------------------------------------------------------------------')
    while True:
        query = input(f"{green}Prompt: ")
        if query == "exit" or query == "quit" or query == "q" or query == "f":
            print('Exiting')
            sys.exit()
        if query == '':
            continue
        start_time = time.time()
        result = pdf_qa({"question": query})
        print(f"{white}Answer: " + result["answer"])
        end_time = time.time()
        print("Time taken:", round(end_time - start_time, 2), 'secs')
        # chat_history.append((query, result["answer"]))

if __name__ == '__main__':
    main()

#What are the key points of the Rich Dad Poor Dad book?
#Give a summary of the Rich Dad Poor Dad book?