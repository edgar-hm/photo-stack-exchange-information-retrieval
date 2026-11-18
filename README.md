# Photography Stack Exchange Information Retrieval System

A domain-specific Information Retrieval (IR) engine and Flask web application built on the **Photography Stack Exchange** dataset (~93.8k posts)[cite: 21, 22]. It combines custom photography tokenization, an inverted index, **BM25 ranking**, and **community score-aware thread reconstruction** to retrieve complete Question–Answer threads[cite: 21, 25].

📄 **[Project Report (PDF)](project_report.pdf)** | 📊 **[Project Presentation (PDF)](project_presentation.pdf)** | 📓 **[Exploration & Evaluation Notebook](photo_stack_exchange.ipynb)**

---

## Key Features & Architecture

* **Domain-Specific Preprocessing (`utils.py`):** Extracts optical parameters via regex (apertures, ISOs, focal lengths), standardizes 291 camera models and 90 photography terms/lens mounts, filters stopwords (NLTK, Terrier, ROUGE-1.5.5), and applies WordNet lemmatization[cite: 18, 23, 24].
* **Inverted Index & BM25 Retrieval (`corpus_inverted_index.py`, `utils.py`):** Indexes 72,945 unique tokens across 26,937 questions and 66,908 answers, scoring candidate posts with BM25 ($k_1 = 1.5, b = 0.75$)[cite: 18, 22, 24].
* **Thread-Based Reranking (`utils.py`):** Pairs matched questions with their top-scoring answer (and vice versa) and reranks deduplicated threads using $T = \text{BM25}(D, Q) + \text{sign}(S_Q)\cdot\log(1 + \vert{}S_Q\vert{}) + \text{sign}(S_A)\cdot\log(1 + \vert{}S_A\vert{})$[cite: 18, 25].
* **Flask Web Interface (`app.py`):** Provides an interactive search UI (`templates/index.html`, `templates/results.html`) displaying the top-5 ranked Q&A threads[cite: 19, 25].

---

## Evaluation Results

Evaluated across **15 benchmark photography queries** spanning five topic categories, manually annotated on a graded relevance scale (`0 = Not relevant`, `1 = Somewhat relevant`, `3 = Highly relevant`)[cite: 26]:

| Metric | Score (Top-5 Threads) |
| :--- | :---: |
| **Precision@5 (P@5)** | **0.72**[cite: 21, 26] |
| **Average Information Gain** | **1.55 / 3.00**[cite: 26, 27] |
| **nDCG@5** | **0.84**[cite: 21, 26] |

---

## Dataset Setup

Because `Posts.xml` (~132 MB) and the generated index artifacts (`corpus.json`, `inverted_index_with_ids.json`, `metadata.csv`, `token_to_id.json`, `id_to_token.json`) exceed GitHub's file size limits, they are excluded from this repository[cite: 19, 22]. To reproduce the index and run the search engine locally:

1. Download the **Photography Stack Exchange** archive (`photo.stackexchange.com.7z`) from the Internet Archive: https://archive.org/download/stackexchange[cite: 22]
2. Extract `Posts.xml` and place it inside the `data/` directory (`data/Posts.xml`)[cite: 19].
3. Run `corpus_inverted_index.py` from the repository root to generate the corpus and inverted index files[cite: 19], then start `app.py`[cite: 19, 25].

---

## Repository Structure

```text
├── app.py                          # Flask web application entry point
├── corpus_inverted_index.py        # Corpus tokenization, metadata extraction & inverted index builder
├── data_exploration.py             # Exploratory data analysis of Photography Stack Exchange posts
├── special_tokens.py               # Dictionary builder for camera models and domain terminology
├── utils.py                        # Preprocessing pipeline, Aho-Corasick trie, BM25 & thread reranking
├── photo_stack_exchange.ipynb      # End-to-end experimentation and evaluation notebook
├── project_report.pdf              # Full technical report and evaluation analysis
├── project_presentation.pdf        # Project presentation slides
├── combined_camera_models.txt      # Source list of 291 camera models
├── camera_models_variations.json   # Canonical-to-variant mapping for camera models
├── special_terms.json              # Canonical-to-variant mapping for 90 photography terms
├── terrier.txt                     # Terrier stopword list
├── rouge_155.txt                   # ROUGE-1.5.5 stopword list
├── eval_queries.txt                # Benchmark evaluation queries
├── query_eval.xlsx                 # Manual relevance annotations and metric calculations
├── templates/
│   ├── index.html                  # Search query input UI
│   └── results.html                # Ranked Q&A thread results UI
└── data/
    └── (place Posts.xml here)