import os
import textcortex
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_textcortex_client():
    # Initialize TextCortex client with your API key
    client = os.getenv('TEXTCORTEX_API_KEY')
    return client


def get_conversational_chain():
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=1.0)
    return model


def user_input(user_question, textcortex_client, pdf_texts):
    # Measure similarity between the user question and each PDF text
    similarity_scores = {}
    for i, pdf_text in enumerate(pdf_texts):
        similarity_score = textcortex_client.measure_similarity(user_question, pdf_text)
        similarity_scores[f"Question_PDF_{i + 1}"] = similarity_score

    # Get the PDF with the highest similarity score
    max_similarity_pdf = max(similarity_scores, key=similarity_scores.get)
    max_similarity_pdf_index = int(max_similarity_pdf.split("_")[-1])

    # Get conversational chain model
    chain = get_conversational_chain()

    # Ask the user's question to the selected PDF context
    response = chain(pdf_texts[max_similarity_pdf_index - 1], user_question)
    return response


def main():
    pdf_paths = []
    while True:
        user_response = input("Upload your contracts and Click on Submit and Process (y/n): ")
        if user_response.lower() == "y":
            pdf_path = input("Enter the path to your PDF file: ")
            pdf_paths.append(pdf_path)
        elif user_response.lower() == "n":
            if not pdf_paths:
                print("No PDF files were uploaded.")
            else:
                print("Processing PDF files...")
                break  # Exit the loop if user chooses 'n' and PDF files are uploaded
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    if pdf_paths:
        # Extract text from PDFs
        pdf_texts = [extract_text_from_pdf(pdf_path) for pdf_path in pdf_paths]

        # Initialize TextCortex client
        textcortex_client = get_textcortex_client()

        # Ask user for a question related to contracts
        user_question = input("Ask questions related to your contracts: ")
        if user_question:
            response = user_input(user_question, textcortex_client, pdf_texts)
            print("Response:", response)


if __name__ == "__main__":
    main()
