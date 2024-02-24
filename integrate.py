import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("token")


def read_pdf(file_path):
    with PdfReader(file_path) as pdf:
        text=""
        for page in pdf.pages:
            text+=page.extract_text()
    return text


def extract_date_and_summary(text):
    date = ""
    summary = ""

    for line in text.splitlines():
        if "Date:" in line:
            date+= line + "\n"
        elif line.strip():
            summary += line + "\n"
    return date, summary


def compare_documents(doc1_path, doc2_path):
    content1 = read_pdf(doc1_path)
    content2 = read_pdf(doc2_path)

    date1, summary1 = extract_date_and_summary(content1)
    date2, summary2 = extract_date_and_summary(content2)

    print(f"\nDate of Document 1:\n{date1}")
    print(f"\nSummary of Document 1:\n{summary1}")

    print(f"\nDate of Document 2:\n{date2}")
    print(f"\nSummary of Document 2:\n{summary2}")


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
    conversation_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(),
                                                               memory=memory)
    return conversation_chain



def compare_documents(doc1_path, doc2_path):
    content1 = read_pdf(doc1_path)
    content2 = read_pdf(doc2_path)

    date1, summary1 = extract_date_and_summary(content1)
    date2, summary2 = extract_date_and_summary(content2)

    comparison_output = (
        f"\nDate of Document 1:\n{date1}\n"
        f"\nSummary of Document 1:\n{summary1}\n"
        f"\nDate of Document 2:\n{date2}\n"
        f"\nSummary of Document 2:\n{summary2}\n"
    )

    return comparison_output


def handle_userinput(update, context, conversation_chain):
    user_question = update.message.text
    response = conversation_chain({'question': user_question})
    bot_response = response['chat_history'][-1].content
    update.message.reply_text(bot_response)


def handle_document(update, context):
    if 'document1' not in context.user_data:
        context.user_data['document1'] = update.message.document
        update.message.reply_text("Please upload the second contract file")
    else:
        document1 = context.user_data['document1']
        document2 = update.message.document
        file1 = context.bot.getFile(document1.file_id)
        file2 = context.bot.getFile(document2.file_id)
        file_path1= f"downloads/{document1.file_name}"
        file_path2= f"downloads/{document2.file_name}"
        file1.download(file_path1)
        file2.download(file_path2)

        comparison_output = compare_documents(file_path1, file_path2)
        update.message.reply_text(comparison_output)
        context.user_data.clear()

    pdf_file = context.bot.getFile(update.message.document.file_id)
    file_path = f"downloads/{update.message.document.file_name}"
    pdf_file.download(file_path)

    # Extract text from PDF
    pdf_text = get_pdf_text([file_path])

    # Get text chunks
    text_chunks = get_text_chunks(pdf_text)

    # Create vector store
    vectorstore = get_vectorstore(text_chunks)

    # Create conversation chain
    conversation_chain = get_conversation_chain(vectorstore)

    update.message.reply_text("I'm here to assist you with the contract")

    # Pass the conversation chain to the message handler
    context.user_data['conversation_chain'] = conversation_chain


def start(update, context):
    update.message.reply_text("Hi! Please upload your contract.")


def compare_documents_command(update, context):
    update.message.reply_text("Please upload contracts you'd like to compare")


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Handler for start command
    dispatcher.add_handler(CommandHandler("start", start))

    # Handler for comparing documents
    dispatcher.add_handler(CommandHandler("compare", compare_documents_command))

    # Handler for document uploads
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

    # Handler for text messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command,
                                          lambda update, context: handle_userinput(update, context, context.user_data[
                                              'conversation_chain'])))


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
