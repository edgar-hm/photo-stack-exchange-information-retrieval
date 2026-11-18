from utils import parse_posts, preprocess_text
import pandas as pd
import json


# Parse posts
posts_xml_path = "data/Posts.xml"
posts_data = parse_posts(posts_xml_path)
posts_df = pd.DataFrame(posts_data)


# Create corpus json and metadata df
def create_corpus_and_metadata(posts_data, preprocess_func):
    """
    Create a tokenized corpus and a metadata DataFrame from posts data.

    Args:
        posts_data (list): List of parsed posts from the XML file.
        preprocess_func (function): Function to preprocess text.

    Returns:
        tuple: (corpus, metadata_df)
            - corpus: Dictionary mapping docID to tokenized content.
            - metadata_df: DataFrame containing post metadata.
    """
    corpus = {}
    metadata = []

    for post in posts_data:
        doc_id = post["Id"]

        # Preprocess title and body
        tokenized_title = preprocess_func(post["Title"] or "")
        tokenized_body = preprocess_func(post["Body"] or "")

        # Combine title and body tokens
        corpus[doc_id] = tokenized_title + tokenized_body

        # Collect metadata
        metadata.append({
            "docID": doc_id,
            "PostType": post["PostTypeId"],
            "ParentID": post["ParentId"],
            "AcceptedAnswer": bool(post.get("AcceptedAnswerId")),
            "Score": int(post["Score"] or 0),
            "ViewCount": int(post["ViewCount"] or 0),
            "Tags": post.get("Tags", "")
        })

    # Convert metadata to a DataFrame
    metadata_df = pd.DataFrame(metadata)

    return corpus, metadata_df

# Generate corpus and metadata
corpus, metadata_df = create_corpus_and_metadata(posts_data, preprocess_text)

# Save the corpus to a JSON file
with open("corpus.json", "w") as file:
    json.dump(corpus, file, indent=1)

# Save the metadata DataFrame to a CSV file
metadata_df.to_csv("metadata.csv", index=False)

print("Corpus and metadata saved to 'corpus.json' and 'metadata.csv'")


# Generate token-to-ID and ID-to-token mappings
def generate_token_id_mapping(corpus):
    token_to_id = {}
    id_to_token = {}
    current_id = 1

    for doc_id, tokens in corpus.items():
        for token in tokens:
            if token not in token_to_id:
                token_to_id[token] = current_id
                id_to_token[current_id] = token
                current_id += 1

    return token_to_id, id_to_token

# Load the corpus
with open("corpus.json", "r") as file:
    corpus = json.load(file)

# Create mappings
token_to_id, id_to_token = generate_token_id_mapping(corpus)

# Save mappings for later use
with open("token_to_id.json", "w") as file:
    json.dump(token_to_id, file, indent=1)
with open("id_to_token.json", "w") as file:
    json.dump(id_to_token, file, indent=1)

print("Token-to-ID mapping created!")


# Generate an inverted index with token IDs
def generate_inverted_index_with_ids(corpus, token_to_id):
    inverted_index = {}

    for doc_id, tokens in corpus.items():
        for position, token in enumerate(tokens):
            token_id = token_to_id[token]
            if token_id not in inverted_index:
                inverted_index[token_id] = {}
            if doc_id not in inverted_index[token_id]:
                inverted_index[token_id][doc_id] = {"tf": 0, "positions": []}
            inverted_index[token_id][doc_id]["tf"] += 1
            inverted_index[token_id][doc_id]["positions"].append(position)

    return inverted_index

# Create the inverted index with token IDs
inverted_index_with_ids = generate_inverted_index_with_ids(corpus, token_to_id)

# Save the updated inverted index
with open("inverted_index_with_ids.json", "w") as file:
    json.dump(inverted_index_with_ids, file, indent=1)

print("Inverted index with token IDs created!")
