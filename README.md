# docsum ![GitHub Actions](https://github.com/yourusername/yourrepo/workflows/Python%20application/badge.svg)

## Overview

`docsum.py` is a Python script that summarizes text from a given file using the Groq API. The script reads the content of the specified file, sends it to the Groq API for summarization, and prints the summarized output in one paragraph, aimed at a 1st-grade reading level.

## Requirements

- Python 3.x
- The Groq API library (you can install it using `pip install groq`)
- A valid Groq API key (stored in the environment variable `GROQ_API_KEY`)

## Usage

To use the script, follow these steps:

1. **Set up the environment variable for the API key**:
    ```bash
    export GROQ_API_KEY=your_api_key_here
    ```

2. **Run the script with a filename as an argument**:
    ```bash
    python docsum.py yourfile.txt
    ```

3. The script will print a summarized version of the file's content.

### Example

If you have a file called `example.txt`, you would run:

```bash
python docsum.py example.txt
```
