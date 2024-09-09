import os
from groq import Groq, RateLimitError
import fulltext
import time
import argparse
import chardet
import re

# Define the chunk size limit (adjust this value as needed)
CHUNK_SIZE_LIMIT = 7000  # Maximum number of words per chunk
MAX_CHAR_LIMIT = 30000  # Maximum number of characters for the final summary

def split_document_into_chunks(text, chunk_size=CHUNK_SIZE_LIMIT):
    """
    Split the input text into smaller chunks so that an LLM can process those chunks without exceeding the token limit.
    This function splits the text into chunks of up to 'chunk_size' words.
    """
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def summarize_text(client, chunk):
    """
    Function to summarize a chunk of text using the LLM API.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Summarize the input text below. Limit the summary to 1 sentence and use a 1st grade reading level.",
            },
            {
                "role": "user",
                "content": chunk,
            }
        ],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content

def clean_final_summary(summary):
    """
    Function to remove any sentence starting with 'Here is a summary of the text'
    or any variation of this sentence.
    """
    # Remove any sentence starting with "Here is a summary of the text..."
    summary = re.sub(r"(?i)here is a summary of the.*?:", "", summary)

    # Return the cleaned summary
    return summary.strip()

def evaluate_and_summarize(client, summary, max_char_limit=MAX_CHAR_LIMIT):
    """
    Evaluate if the summary is greater than the max_char_limit.
    If so, summarize the final summary repeatedly until it is under the limit.
    """
    while len(summary) > max_char_limit:
        print(f"Summary length is {len(summary)} characters, summarizing again...")
        summary = summarize_text(client, summary)
        summary = clean_final_summary(summary)
    
    return summary

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

# line 7+8 => args.filename will contain the first string after program name on command line

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    # Try to extract text using fulltext
    try:
        text = fulltext.get(args.filename)
    except Exception as e:
        print(f"Fulltext extraction failed: {e}. Attempting to read the file with detected encoding.")
        # Detect the file's encoding and read it
        try:
            with open(args.filename, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                file_encoding = result['encoding']
            
            # Now read the file using the detected encoding without replacing errors
            with open(args.filename, 'r', encoding=file_encoding) as f:
                text = f.read()

        except Exception as e:
            print(f"Error reading the file: {e}")
            exit(1)
 
    chunks = split_document_into_chunks(text)

    # Create a list to store summaries of each chunk
    summaries = []

    # Summarize each chunk using the LLM, applying retries
    for chunk in chunks:
        summary = summarize_text(client, chunk)
        summaries.append(summary)

    # After all chunks are summarized, join them into one final summary
    final_summary = f"This is a summary of the file '{args.filename}': " + " ".join(summaries)

    # Clean the final summary to remove unwanted phrases
    final_summary = clean_final_summary(final_summary)

    # If the final summary exceeds the max character limit, keep summarizing it until it is under the limit
    # final_summary = evaluate_and_summarize(client, final_summary, MAX_CHAR_LIMIT)

    # Print the final summary
    print(final_summary)
