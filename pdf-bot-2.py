import pdfplumber
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Define functions to extract text from PDFs, convert to chunks, and generate embeddings
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text, chunk_size=1000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks


def get_openai_embeddings(text_chunks):
    embeddings = []
    for chunk in text_chunks:
        # Generate embeddings for each chunk using OpenAI API
        # You need to replace 'YOUR_OPENAI_API_KEY' with your actual API key
        openai.api_key = 'YOUR_OPENAI_API_KEY'
        response = openai.Embed(
            input_text=chunk,
            model="text-davinci-002"  # Adjust the model as needed
        )
        embeddings.append(response['embedding'])
    return embeddings


def compare_contracts(embeddings_contract1, embeddings_contract2):
    similarity_scores = []
    for emb1, emb2 in zip(embeddings_contract1, embeddings_contract2):
        # Calculate cosine similarity between embeddings
        similarity_matrix = cosine_similarity([emb1], [emb2])
        similarity_score = similarity_matrix[0][0]
        similarity_scores.append(similarity_score)

    # Calculate the average similarity score
    avg_similarity_score = np.mean(similarity_scores)
    return avg_similarity_score


# Main function to compare two contract PDFs
def compare_contract_pdfs(pdf_path1, pdf_path2):
    text1 = extract_text_from_pdf(pdf_path1)
    text2 = extract_text_from_pdf(pdf_path2)

    chunks1 = get_text_chunks(text1)
    chunks2 = get_text_chunks(text2)

    embeddings1 = get_openai_embeddings(chunks1)
    embeddings2 = get_openai_embeddings(chunks2)

    similarity_score = compare_contracts(embeddings1, embeddings2)

    return similarity_score


# Example usage:
pdf_path1 = "file_0.pdf"
pdf_path2 = "file_2.pdf"
similarity_score = compare_contract_pdfs(pdf_path1, pdf_path2)
print("Similarity Score:", similarity_score)
