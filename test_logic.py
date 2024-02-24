import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")  # folder created locally

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context,make sure to provide all the details,if the \n
    Context:\n{context}?\n
    Question: \n{question}\n 

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=1.0)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question}
        , return_only_outputs=True)

    return response["output_text"]


def main():
    pdf_docs = []
    while True:
        user_response = input("Upload your contracts and Click on Submit and Process (y/n): ")
        if user_response.lower() == "y":
            pdf_docs = [input("Enter the path to your PDF file: ")]
            break
        elif user_response.lower() == "n":
            print("Exiting the program.")
            return
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    if pdf_docs:
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        get_vector_store(text_chunks)

        user_question = input("Ask questions related to your contracts: ")
        if user_question:
            response = user_input(user_question)
            print(response)


if __name__ == "__main__":
    main()