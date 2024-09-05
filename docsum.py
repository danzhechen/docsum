def split_document_into_chunks(text):
    r'''
    Split the input text into smaller chunks so that an LLM can process those chunks individually.

    >>> split_document_into_chunks('This is a sentence.\n\nThis is another paragraph.')
    ['This is a sentence.', 'This is another paragraph.']
    >>> split_document_into_chunks('This is a sentence.\n\nThis is another paragraph.\n\nThis is a third paragraph.')
    ['This is a sentence.', 'This is another paragraph.', 'This is a third paragraph.']
    >>> split_document_into_chunks('This is a sentence.')
    ['This is a sentence.']
    >>> split_document_into_chunks('')
    []
    >>> split_document_into_chunks('This is a sentence.\n')
    ['This is a sentence.']
    >>> split_document_into_chunks('This is a sentence.\n\n')
    ['This is a sentence.']
    >>> split_document_into_chunks('This is a sentence.\n\nThis is another paragraph.\n\n')
    ['This is a sentence.', 'This is another paragraph.']

    '''

    # Split text by double newline and strip whitespace
    paragraphs = text.split('\n\n')
    
    # Filter out empty strings and strip extra newlines or spaces
    paragraphs = [para.strip() for para in paragraphs if para.strip()]
    
    return paragraphs

if __name__ == '__main__':

    import os
    from groq import Groq
    import fulltext
    # parse command line args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

# line 7+8 => args.filename will contain the first string after program name on command line

    client = Groq(
        # This is the default and can be omitted
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    try:
        text = fulltext.get(args.filename)
    except Exception as e:
        print(f"Error reading the file: {e}")
        exit(1)
    
    # Call the split_document_into_chunks function on the input text
    chunks = split_document_into_chunks(text)

    # Create a list to store summaries of each chunk
    summaries = []

    # Summarize each chunk using the LLM
    for chunk in chunks:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    'role': 'system',
                    'content': 'Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade reading level.',
                },
                {
                    "role": "user",
                    "content": chunk,
                }
            ],
            model="llama3-8b-8192",
        )
        # Append the summary to the summaries list
        summaries.append(chat_completion.choices[0].message.content)

    # Concatenate the summaries into a smaller document
    smaller_document = ' '.join(summaries)

    # Summarize the smaller document using the LLM
    final_summary = client.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': 'Summarize the input text below. Limit the summary to 1 paragraph and use a 1st grade reading level.',
            },
            {
                "role": "user",
                "content": smaller_document,
            }
        ],
        model="llama3-8b-8192",
    )

    # Print the final summary
    print(final_summary.choices[0].message.content)
