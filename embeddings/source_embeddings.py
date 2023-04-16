'''
tiktoken is a fast open-source tokenizer by OpenAI. 
https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

Given a text string (e.g., "tiktoken is great!") and an encoding (e.g., "cl100k_base"), 
a tokenizer can split the text string into a list of tokens (e.g., ["t", "ik", "token", " is", " great", "!"]).

Splitting text strings into tokens is useful because GPT models see text in the form of tokens. 
Knowing how many tokens are in a text string can tell you 
(a) whether the string is too long for a text model to process and 
(b) how much an OpenAI API call costs (as usage is priced by token).

A helpful rule of thumb is that one token generally corresponds to ~4 characters of text for common English text.
'''

'''
OpenAI Embeddings
https://platform.openai.com/docs/guides/embeddings
'''

import re
import os
import pandas as pd
import tiktoken
import openai

domain = "example.com"
max_tokens = 10
openai.api_key = os.getenv("POETRY_OPENAI_API_KEY")

# Extra spacing and new lines can clutter the text and complicate the embeddings process.
# The \s (lowercase s) matches a whitespace (blank, tab \t, and newline \r or \n).
def preprocess_text():
    texts = []
    for file in os.listdir("text/" + domain + "/"):
        with open("text/" + domain + "/" + file, "r", encoding="UTF-8") as f:
            text = f.read()
            text_processed = re.sub(r'\s+', ' ', text)
            texts.append((file, text_processed))

    return texts

# splits the input text into tokens by breaking down the sentences and words. 
def add_ntoken(tokenizer, df):

    # Tokenize the text and save the number of tokens to a new column
    df.loc[:, 'n_tokens'] = df.loc[:, 'text'].apply(lambda x: len(tokenizer.encode(x)))

    # Visualize the distribution of the number of tokens per row using a histogram
    df.loc[:, 'n_tokens'].hist()

# Function to split the text into chunks of a maximum number of tokens
# Break text into shortened sentences, whoes length is shorter than the max number of tokens
# No need to create tokenized list in the code, openai's endpoint will do it for us
def split_into_many(tokenizer, text, n_token, max_tokens = max_tokens):
    chunks = []
    counter = 0
    token = tokenizer.encode(text)
    while counter < n_token:
        chunk = tokenizer.decode(token[counter : counter + max_tokens])
        counter += max_tokens
        chunks.append(chunk)

    return chunks

# Note that you may run into rate limit issues depending on how many files you try to embed
# Please check out our rate limit guide to learn more on how to handle this: https://platform.openai.com/docs/guides/rate-limits
def create_embeddings(tokenizer, shortened):
    df = pd.DataFrame(shortened, columns = ['text'])
    df['n_tokens'] = df.loc[:, 'text'].apply(lambda x: len(tokenizer.encode(x)))
    df.n_tokens.hist()

    df['embeddings'] = df.loc[:, 'text'].apply(lambda x: openai.Embedding.create(input=x, engine='text-embedding-ada-002')['data'][0]['embedding'])
    df.to_csv('processed/embeddings.csv')
    df.head()

def main():
    texts = preprocess_text()

    # Create a dataframe from the list of texts
    df = pd.DataFrame(texts, columns = ['fname', 'text'])

    # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
    tokenizer = tiktoken.get_encoding("cl100k_base")

    # Create and Add the number of tokens to the dataframe
    add_ntoken(tokenizer, df)

    texts_shortened = []
    # Iterate over DataFrame rows as (index, Series) pairs.
    for row in df.iterrows():

        # If the text is None, go to the next row
        if row[1]['text'] is None:
            continue

        # If the number of tokens is greater than the max number of tokens, split the text into chunks
        if row[1]['n_tokens'] > max_tokens:
            texts_shortened += split_into_many(tokenizer, row[1]['text'], row[1]['n_tokens'])

        # Otherwise, add the text to the list of shortened texts
        else:
            texts_shortened.append( row[1]['text'] )

    create_embeddings(tokenizer, texts_shortened)

if __name__ == "__main__":
    main()