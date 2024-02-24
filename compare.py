from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Define conversation states
COUNT, HANDLE_FILE = range(2)


# Function to handle the compare command
def compare(update, context):
    update.message.reply_text("How many PDF files would you like to compare? Please enter a number.")
    return COUNT


def count(update, context):
    try:
        count = int(update.message.text)
        if count < 2:
            update.message.reply_text("Please enter a valid number greater than 1.")
            return COUNT
        else:
            context.user_data['compare_document_count'] = count
            update.message.reply_text(f"Great! Please upload {count} PDF file(s) one by one for comparison.")
            return HANDLE_FILE
    except ValueError:
        update.message.reply_text("Please enter a valid number.")
        return COUNT


def handle_file(update, context):
    user_id = update.message.from_user.id
    document = update.message.document
    file_id = document.file_id
    file_name = document.file_name
    file_path = f"downloads/{user_id}_{file_name}"

    if 'documents' not in context.user_data:
        context.user_data['documents'] = []

    # Download the file
    file = context.bot.getFile(file_id)
    file.download(file_path)

    # Add file path to the list of documents
    context.user_data['documents'].append(file_path)

    # Check if all files have been uploaded
    if len(context.user_data['documents']) == context.user_data['compare_document_count']:
        # Compare the documents
        comparison_output = ""
        for i in range(len(context.user_data['documents'])):
            for j in range(i + 1, len(context.user_data['documents'])):
                comparison_output += compare_documents(context.user_data['documents'][i],
                                                       context.user_data['documents'][j])

        # Send the comparison output to the user
        update.message.reply_text(comparison_output)

        # Clear user data
        context.user_data.clear()

    return HANDLE_FILE


# Add compare command handler
dispatcher.add_handler(CommandHandler("compare", compare))

# Conversation handler for handling the number of documents to compare
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('compare', compare)],
    states={
        COUNT: [MessageHandler(Filters.text & ~Filters.command, count)],
        HANDLE_FILE: [MessageHandler(Filters.document & ~Filters.command, handle_file)]
    },
    fallbacks=[],
    allow_reentry=True
)
dispatcher.add_handler(conv_handler)
