# Import libraries
import xml.etree.ElementTree as ET

import re
import json

from bs4 import BeautifulSoup

# import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('wordnet')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

import ahocorasick
from collections import defaultdict
import pandas as pd
import math

# Define a function to parse the XML and extract relevant fields
def parse_posts(file_path):
    posts_data = []

    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Iterate through each row in the XML file
    for row in root.findall("row"):
        post = {
            "Id": row.attrib.get("Id"),
            "PostTypeId": row.attrib.get("PostTypeId"),
            "ParentId": row.attrib.get("ParentId"),
            "AcceptedAnswerId": row.attrib.get("AcceptedAnswerId"),
            "Score": row.attrib.get("Score"),
            "ViewCount": row.attrib.get("ViewCount"),
            "Tags": row.attrib.get("Tags"),
            "Title": row.attrib.get("Title"),
            "CreationDate": row.attrib.get("CreationDate"),
            "AnswerCount": row.attrib.get("AnswerCount"),
            "Body": row.attrib.get("Body"), 
        }
        posts_data.append(post)

    return posts_data

# Build trie from camera models dictionary
def build_trie(camera_models_dict):
    trie = ahocorasick.Automaton()
    for standardized, variations in camera_models_dict.items():
        for variation in variations:
            trie.add_word(variation, standardized)  # Map each variation to the standardized name
    trie.make_automaton()
    return trie

# Load the special terms dictionary
with open("special_terms.json", "r") as file:
    special_terms = json.load(file)

# Load the camera models dictionary
with open("camera_models_variations.json", "r") as file:
    camera_models_dict = json.load(file)

# Build the trie
camera_trie = build_trie(camera_models_dict)

# Preprocessing function (tokenizer)
def preprocess_text(text):
    # Remove HTML tags
    text = BeautifulSoup(text, 'html.parser').get_text()
    normalized_text = text.lower()

    # Remove URLs (e.g., https://example.com)
    normalized_text = re.sub(r"https?://\S+|www\.\S+", " ", normalized_text)

    # Identify and normalize aperture values
    aperture_pattern = r"(?<!\w)f\s?/?\d+(\.\d+)?(?:\s?-\s?/?\d+(\.\d+)?)?(?!\w)"  # Match f1.4, f/1.4, f1.4-2.8, f/1.4-2.8
    normalized_apertures = [match.group().replace(" ", "").replace("/", "").lower() for match in re.finditer(aperture_pattern, normalized_text)]
    normalized_text = re.sub(aperture_pattern, " ", normalized_text)

    # Identify and normalize ISO values
    iso_pattern = r"(?<!\w)iso-?\s?\d+(?!\w)"
    normalized_isos = [match.group().replace("-", "").replace(" ", "") for match in re.finditer(iso_pattern, normalized_text)]
    normalized_text = re.sub(iso_pattern, " ", normalized_text)

    # Identify and normalize focal lengths
    focal_length_pattern = r"(?<!\w)\d+\s?(?:-\s?\d+)?\s?mm(?!\w)"
    normalized_focal_lengths = [match.group().replace(" ", "").lower() for match in re.finditer(focal_length_pattern, normalized_text)]
    normalized_text = re.sub(focal_length_pattern, " ", normalized_text)

    # Normalize special photography terms    
    normalized_special_terms = []
    for term, normalized in special_terms.items():
        # Replace both forms in the text
        hyphenated_term = term.replace(" ", "-")
        for variation in [term, hyphenated_term]:
            if re.search(rf"\b{re.escape(variation)}\b", normalized_text):
                normalized_special_terms.append(normalized)
                normalized_text = re.sub(rf"\b{re.escape(variation)}\b", " ", normalized_text)

    # Tokenize camera model names using the trie
    normalized_camera_models = []
    processed_text = list(normalized_text)  # Use a list of characters to safely modify text
    for end_index, standardized in camera_trie.iter(normalized_text):
        start_index = end_index - len(standardized) + 1
        # Check for valid word boundaries around the match
        if (
            (start_index == 0 or not normalized_text[start_index - 1].isalnum()) and
            (end_index + 1 == len(normalized_text) or not normalized_text[end_index + 1].isalnum())
        ):
            normalized_camera_models.append(standardized)
            # Replace matched variation with spaces in processed_text
            for i in range(start_index, end_index + 1):
                processed_text[i] = " "
    normalized_text = "".join(processed_text)

    # Remove non-alphanumeric characters except for apertures, ISO values, and focal lengths
    normalized_text = re.sub(r"[^a-zA-Z0-9\s]", " ", normalized_text)

    # Tokenize text
    tokens = word_tokenize(normalized_text)

    # Add normalized terms directly to tokens
    tokens += normalized_apertures + normalized_isos + normalized_focal_lengths + normalized_special_terms + normalized_camera_models

    # Remove standalone `f`, `iso`, and numbers not part of relevant tokens
    tokens = [t for t in tokens if t not in {'f', 'iso'} and not (t.isdigit() and t not in normalized_apertures + normalized_isos + normalized_focal_lengths + normalized_camera_models)]

    # Remove stopwords
    nltk_stop_words = set(stopwords.words('english'))
    with open('terrier.txt', 'r') as file:
        terrier_stop_words = set(file.read().splitlines())
    with open('rouge_155.txt', 'r') as file:
        rouge_stop_words = set(file.read().splitlines())
    combined_stop_words = nltk_stop_words.union(terrier_stop_words).union(rouge_stop_words)
    tokens = [t for t in tokens if t not in combined_stop_words]

    # Lemmatize tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]

    return tokens

def precompute_bm25_values(inverted_index, total_docs):
    """
    Precompute document lengths, term frequencies, and average document length (avgdl) for BM25.
    
    Args:
        inverted_index (dict): Inverted index with token IDs.
        total_docs (int): Total number of documents.
    
    Returns:
        tuple: Document lengths, document frequencies, and average document length.
    """
    doc_lengths = defaultdict(int)
    doc_frequencies = defaultdict(int)

    for token_id, postings in inverted_index.items():
        doc_frequencies[token_id] = len(postings)  # Number of documents containing the token
        for doc_id, data in postings.items():
            doc_lengths[doc_id] += data['tf']  # Sum term frequencies for the document

    avgdl = sum(doc_lengths.values()) / total_docs  # Calculate average document length
    return doc_lengths, doc_frequencies, avgdl

def bm25_score(query_tokens, inverted_index, doc_lengths, doc_frequencies, avgdl, total_docs, k1=1.5, b=0.75):
    """
    Compute BM25 scores for documents based on a query.
    
    Args:
        query_tokens (list): List of token IDs from the query.
        inverted_index (dict): Inverted index with token IDs.
        doc_lengths (dict): Document lengths.
        doc_frequencies (dict): Document frequencies of terms.
        avgdl (float): Average document length.
        total_docs (int): Total number of documents.
        k1 (float): BM25 hyperparameter for term frequency saturation.
        b (float): BM25 hyperparameter for length normalization.
    
    Returns:
        list: Sorted list of (doc_id, score) tuples.
    """
    scores = defaultdict(float)

    for token_id in query_tokens:
        if str(token_id) not in inverted_index:
            continue

        postings = inverted_index[str(token_id)]
        idf = math.log((total_docs - doc_frequencies[token_id] + 0.5) / (doc_frequencies[token_id] + 0.5) + 1)

        for doc_id, data in postings.items():
            f = data['tf']  # Term frequency in the document
            d = doc_lengths[doc_id]  # Document length
            denom = f + k1 * (1 - b + b * (d / avgdl))
            scores[doc_id] += idf * (f * (k1 + 1)) / denom

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def bm25_search(query, token_to_id, inverted_index, doc_lengths, doc_frequencies, avgdl, total_docs):
    """
    Perform a BM25 search with token IDs.
    
    Args:
        query (str): User query string.
        token_to_id (dict): Mapping from tokens to token IDs.
        inverted_index (dict): Inverted index with token IDs.
        doc_lengths (dict): Document lengths.
        doc_frequencies (dict): Document frequencies.
        avgdl (float): Average document length.
        total_docs (int): Total number of documents.
    
    Returns:
        list: Sorted list of (doc_id, score) tuples.
    """
    # Preprocess the query
    query_tokens = preprocess_text(query)

    # Convert tokens to token IDs
    query_token_ids = [token_to_id[token] for token in query_tokens if token in token_to_id]

    # Calculate BM25 scores
    results = bm25_score(query_token_ids, inverted_index, doc_lengths, doc_frequencies, avgdl, total_docs)
    return results

def refine_bm25_results(results, metadata_path, top_n=5):
    """
    Refine BM25 results by combining questions with their best answers.

    Args:
        results (list): List of (docID, score) tuples from BM25 search.
        metadata_path (str): Path to the metadata CSV file.
        top_n (int): Number of top results to return.

    Returns:
        list: Refined list of question-answer thread results.
    """
    # Load metadata
    metadata = pd.read_csv(metadata_path)

    # Prepare a dictionary to store question threads
    thread_scores = []

    alpha = 1 # weight for posts scores

    for doc_id, bm25_score in results[:top_n]:
        # Convert doc_id to string to match metadata
        doc_id = int(doc_id)

        # Retrieve metadata for the current post
        post_data = metadata[metadata['docID'] == doc_id]

        post_data = post_data.iloc[0]  # Access the first (and only) row

        # If it's a question, find the best answer
        if post_data['PostType'] == 1:  # Question
            question_score = post_data['Score']

            # Find the best answer (accepted or highest-scoring)
            answers = metadata[metadata['ParentID'] == doc_id].reset_index()  # Find answers linked to this question
            if answers.empty:
                continue            
            else:
                best_answer = answers.iloc[answers['Score'].idxmax()]
                best_answer_score = best_answer['Score']
                best_answer_id = best_answer['docID']

            thread_score = (
                bm25_score
                + alpha * math.copysign(math.log(1 + abs(question_score)), question_score)
                + alpha * math.copysign(math.log(1 + abs(best_answer_score)), best_answer_score)
            )
            
            thread_scores.append({
                'thread_score': thread_score,
                'question_id': doc_id,
                'answer_id': best_answer_id,
                'bm25_score': bm25_score,
                'question_score': question_score,
                'answer_score': best_answer_score
            })
        # If it's an answer, find the corresponding question
        elif post_data['PostType'] == 2: # Answer
            answer_score = post_data['Score']

            # Find corresponding question
            question = metadata[metadata['docID'] == post_data['ParentID']]
            question = question.iloc[0]
            question_score = question['Score']
            question_id = question['docID']

            thread_score = (
                bm25_score
                + alpha * math.copysign(math.log(1 + abs(question_score)), question_score)
                + alpha * math.copysign(math.log(1 + abs(answer_score)), answer_score)
            )

            thread_scores.append({
                'thread_score': thread_score,
                'question_id': question_id,
                'answer_id': doc_id,
                'bm25_score': bm25_score,
                'question_score': question_score,
                'answer_score': answer_score
            })

    # Remove duplicates by focusing on unique questions
    unique_threads = {}
    for thread in thread_scores:
        question_id = thread['question_id']
        if question_id not in unique_threads or thread['thread_score'] > unique_threads[question_id]['thread_score']:
            unique_threads[question_id] = thread  # Keep the thread with the highest score for the question

    # Rerank threads by combined scores
    ranked_threads = sorted(unique_threads.values(), key=lambda x: x['thread_score'], reverse=True)

    return ranked_threads[:top_n]

def clean_html_content(html_content):
    """
    Cleans and formats HTML content for user-readable output.
    
    Args:
        html_content (str): Raw HTML content.
    
    Returns:
        str: Cleaned and formatted content.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Process links (<a> tags): keep the text and add the link in parentheses
    for a_tag in soup.find_all("a", href=True):
        link_text = a_tag.get_text(strip=True)
        url = a_tag["href"]
        a_tag.replace_with(f"{link_text} ({url})")
    
    # Extract plain text while preserving line breaks
    text = soup.get_text(separator="\n")
    
    # Remove excessive whitespace
    cleaned_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    
    return cleaned_text
