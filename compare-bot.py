import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv("token")


def read_pdf(file_path):
    with PdfReader(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


def extract_date_and_summary(text):
    date = ""
    summary = ""

    # Find lines containing specific keywords for date and summary
    for line in text.splitlines():
        if "Date" in line:
            date += line + "\n"
        elif line.strip():  # If the line is not empty, consider it part of the document summary
            summary += line + "\n"

    return date, summary


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


def handle_document(update, context):
    # Get file paths of the uploaded documents
    doc1_file = context.bot.getFile(update.message.document.file_id)
    doc2_file = context.bot.getFile(update.message.document.file_id)
    doc1_path = f"downloads/{update.message.document.file_name}"
    doc2_path = f"downloads/{update.message.document.file_name}_2"

    # Download the documents
    doc1_file.download(doc1_path)
    doc2_file.download(doc2_path)

    # Compare the documents
    comparison_output = compare_documents(doc1_path, doc2_path)

    # Send the comparison output to the user
    update.message.reply_text(comparison_output)


def start(update, context):
    update.message.reply_text("Hi! Please upload two PDF documents for comparison.")


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Handler for start command
    dispatcher.add_handler(CommandHandler("start", start))

    # Handler for document uploads
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
