import pandas as pd
import numpy as np
import openai
import os
from openai.embeddings_utils import distances_from_embeddings

openai.api_key = os.getenv("POETRY_OPENAI_API_KEY")

# Function to create a context for a question, it retrieves chunks of texts that are semantically related to the question, 
# so they might contain the answer, but there's no guarantee of it. 
# The chance of finding an answer can be further increased by returning the top 5 most likely results.
# 1. Convert the question to an embedding
# 2. find the distances between question and embeddings, 
#       by comparing the the vector of numbers (which was the conversion of the raw text) using cosine distance
#       The vectors are likely related and might be the answer to the question if they are close in cosine distance
# 3. Sort the embeddings by distance
# 4. Return the most similar context
def create_context( question, df, max_len=1800, size="ada"):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']

    # Get the distances from the embeddings
    df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')


    returns = []
    cur_len = 0

    # The text was broken up into smaller sets of tokens, Sort by distance and add the text to the context until the context is too long
    # The max_len can also be modified to something smaller, if more content than desired is returned.
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        
        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4
        
        # If the context is too long, break
        if cur_len > max_len:
            break
        
        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)

# To formulate a coherent answer. If there is no relevant answer, the prompt will return “I don’t know”.
# A realistic sounding answer to the question can be created with the completion endpoint using text-davinci-003.
def answer_question(
    df,
    model="text-davinci-003",
    question="Am I allowed to publish model outputs to Twitter, without a human review?",
    max_len=1800,
    size="ada",
    debug=False,
    max_tokens=150,
    stop_sequence=None
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )

    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        # Create a completions using the questin and context
        response = openai.Completion.create(
            prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\nContext: {context}\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print(e)
        return ""

def main():
    df=pd.read_csv('processed/embeddings.csv', index_col=0)

    # Convert the embeddings column to a list of numpy arrays
    # the build-in eval() function is used to convert the string representation of a list to a python list
    # df['embeddings'] = "[-0.0027, 0.0118, ...]" to df['embeddings'] = [-0.0027, 0.0118, ...]
    # the numpy.array() function is used to convert the python list to a numpy array 
    # , which provides more flexibility given NumPy arrays have many functions. It will also flatten the dimension to 1-D
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)


    #print(answer_question(df, question="What day is it?", debug=False))
    #print(answer_question(df, question="What is our newest embeddings model?"))
    #print(answer_question(df, question="Why do I need this domain?"))
    print(answer_question(df, question="Can I use this domain without asking for permission first?"))

if __name__ == "__main__":
    main()