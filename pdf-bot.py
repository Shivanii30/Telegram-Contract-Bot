import os
import sys
import openai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain


load_dotenv()


def get_pdf_text(pdf_paths):
    text = ""
    for pdf_path in pdf_paths:
        pdf_reader = PdfReader(pdf_path)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key="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")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)
    return conversation_chain


def compare_contract_pdfs(pdf_path1, pdf_path2):
    text1 = get_pdf_text(pdf_path1)
    text2 = get_pdf_text(pdf_path2)

    # Create a prompt by concatenating the texts of both contracts
    comparison_prompt = "Contract 1: {text1}\nContract 2: {text2}"

    # Send the comparison prompt to OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",  # Adjust the model as needed
        prompt=comparison_prompt,
        max_tokens=100,  # Adjust as needed
        temperature=0,
        top_p=1,
        n=1,
        stream=False
    )

    # Extract the generated comparison from the OpenAI response

    comparison_result = response['choices'][0]['text']
    return comparison_result


def handle_userinput(user_question, conversation_chain):
    response = conversation_chain({'question': user_question})
    chat_history = response['chat_history']

    for i, message in enumerate(chat_history):
        if i % 2 == 0:
            print(f"User: {message.content}")
        else:
            print(f"Bot: {message.content}")


def main(pdf_paths):
    # Load environment variables
    load_dotenv()

    # Get user question
    user_question = input("Ask a question about your documents:")

    # get pdf text
    raw_text = get_pdf_text(pdf_paths)

    # get the text chunks
    text_chunks = get_text_chunks(raw_text)

    # create vector store
    vectorstore = get_vectorstore(text_chunks)

    # create conversation chain
    conversation_chain = get_conversation_chain(vectorstore)

    # Handle user input
    if user_question:
        handle_userinput(user_question, conversation_chain)

    comparison_result = compare_contract_pdfs(pdf_paths[0], pdf_paths[1])
    print("Comparison", comparison_result)


if __name__ == '__main__':

    #Check if PDF file paths are provided
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_pdf1> <path_to_pdf2> ...")
        sys.exit(1)

    # Pass PDF file paths to the main function
    main(sys.argv[1:])
