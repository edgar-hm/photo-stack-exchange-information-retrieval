from flask import Flask, request, jsonify, render_template
import pandas as pd
import json
from utils import parse_posts, bm25_search, refine_bm25_results, precompute_bm25_values, clean_html_content

app = Flask(__name__)

# Load required data
metadata_path = "metadata.csv"
posts_xml_path = "data/Posts.xml"
with open("token_to_id.json", "r") as f:
    token_to_id = json.load(f)
with open("inverted_index_with_ids.json", "r") as f:
    inverted_index = json.load(f)
with open("corpus.json", "r") as f:
    corpus = json.load(f)

# Parse XML to get titles and bodies
posts_data = parse_posts(posts_xml_path)
posts_df = pd.DataFrame(posts_data)

# Precompute BM25 values
total_docs = len(corpus)
doc_lengths, doc_frequencies, avgdl = precompute_bm25_values(inverted_index, total_docs)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    if not query:
        return jsonify({"error": "Query is required."})

    # Perform BM25 search
    bm25_results = bm25_search(query, token_to_id, inverted_index, doc_lengths, doc_frequencies, avgdl, total_docs)

    # Filter and refine results
    refined_results = refine_bm25_results(bm25_results, metadata_path)

    # Enhance results with titles and cleaned bodies
    enhanced_results = []
    for thread in refined_results:
        question = posts_df.loc[posts_df["Id"] == str(thread["question_id"])]
        answer = posts_df.loc[posts_df["Id"] == str(thread["answer_id"])] if thread["answer_id"] else None

        # Clean HTML content for better readability
        question_body_cleaned = clean_html_content(question["Body"].values[0]) if not question.empty else "N/A"
        answer_body_cleaned = clean_html_content(answer["Body"].values[0]) if answer is not None and not answer.empty else "N/A"

        enhanced_results.append({
            "thread_score": thread["thread_score"],
            "question_id": thread["question_id"],
            "question_title": question["Title"].values[0] if not question.empty else "N/A",
            "question_body": question_body_cleaned,
            "answer_id": thread["answer_id"],
            "answer_body": answer_body_cleaned,
            "bm25_score": thread["bm25_score"],
            "question_score": thread["question_score"],
            "answer_score": thread["answer_score"]
        })

    return render_template("results.html", query=query, results=enhanced_results)

if __name__ == "__main__":
    app.run(debug=True)
