from utils import parse_posts, preprocess_text
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns


# Parse posts
posts_xml_path = "data/Posts.xml"
posts_data = parse_posts(posts_xml_path)
posts_df = pd.DataFrame(posts_data)


# Count PostTypeId occurrences
post_type_counts = defaultdict(int)
for post in posts_data:
    post_type_counts[post['PostTypeId']] += 1

# Display counts
print("Post Type Distribution:")
print(f"Questions: {post_type_counts['1']}")
print(f"Answers: {post_type_counts['2']}")

# Visualize post type distribution
labels = ['Questions', 'Answers']
counts = [post_type_counts['1'], post_type_counts['2']]
plt.figure(figsize=(3, 4))
plt.bar(labels, counts, color=['blue', 'green'])
plt.title("Post Type Distribution")
plt.ylabel("Count")
plt.show()


# Filter questions and sort by Score
questions = [post for post in posts_data if post['PostTypeId'] == '1' and post['Score']]
top_scoring_questions = sorted(questions, key=lambda x: int(x['Score']), reverse=True)[:10]

# Display top scoring questions
print("\nTop 10 Highest Scoring Questions:")
for question in top_scoring_questions:
    print(f"Id: {question['Id']}, Title: {question['Title']}, Score: {question['Score']}")

# Filter questions and sort by ViewCount
most_viewed_questions = sorted(questions, key=lambda x: int(x['ViewCount'] or 0), reverse=True)[:10]

# Display most viewed questions
print("\nTop 10 Most Viewed Questions:")
for question in most_viewed_questions:
    print(f"Id: {question['Id']}, Title: {question['Title']}, Views: {question['ViewCount']}")


# Percentage of questions with accepted answers
accepted_answers = [q for q in questions if q['AcceptedAnswerId']]
percentage_accepted = (len(accepted_answers) / len(questions)) * 100
print(f"\nPercentage of Questions with Accepted Answers: {percentage_accepted:.2f}%")


# Analyze answers linked to each question
answer_counts = defaultdict(int)
for post in posts_data:
    if post['PostTypeId'] == '2' and post['ParentId']:
        answer_counts[post['ParentId']] += 1

all_counts = list(answer_counts.values())
average_answers = sum(all_counts) / len(all_counts) if all_counts else 0
median_answers = np.median(all_counts) if all_counts else 0

print(f"\nAverage Number of Answers per Question: {average_answers:.2f}")
print(f"Median Number of Answers per Question: {median_answers}")

# Visualize answer counts distribution
plt.figure(figsize=(8, 4))
plt.hist(all_counts, bins=range(1, 15), color='purple', edgecolor='black', align='left')
plt.title("Distribution of Answer Counts per Question")
plt.xlabel("Number of Answers")
plt.ylabel("Frequency")
plt.xticks(range(1, 15))
plt.show()


# Analyze and count tags
tag_list = []
for post in posts_data:
    if 'Tags' in post and post['Tags']:
        tags = post['Tags'].strip('<>').split('><')
        tag_list.extend(tags)

tag_counts = Counter(tag_list)
top_10_tags = tag_counts.most_common(10)

# Display top tags
print("\nTop 10 Tags:")
for tag, count in top_10_tags:
    print(f"{tag}: {count}")

# Visualize top tags
tags, counts = zip(*top_10_tags)
plt.figure(figsize=(8, 5))
plt.bar(tags, counts, color='orange')
plt.title("Top 10 Tags")
plt.xlabel("Tags")
plt.ylabel("Frequency")
plt.xticks(rotation=90)
plt.show()


# Get accepted answer positions
accepted_answer_positions = []

for question in posts_data:
    if question['PostTypeId'] == "1" and question['AcceptedAnswerId']:
        # Filter answers to this question
        answers = [
            post for post in posts_data
            if post['PostTypeId'] == "2" and post['ParentId'] == question['Id']
        ]
        # Sort answers by CreationDate
        answers = sorted(answers, key=lambda x: x['CreationDate'])
        # Find the position of the accepted answer
        for i, answer in enumerate(answers):
            if answer['Id'] == question['AcceptedAnswerId']:
                accepted_answer_positions.append(i + 1)
                break

# Analyze positions
position_counts = Counter(accepted_answer_positions)
average_position = np.mean(accepted_answer_positions) if accepted_answer_positions else 0

print("\nPosition of Accepted Answers:")
for position, count in sorted(position_counts.items()):
    print(f"Position {position}: {count} times")
print(f"Average Position of Accepted Answers: {average_position:.2f}")

# Visualize positions
plt.figure(figsize=(8, 5))
plt.bar(position_counts.keys(), position_counts.values(), color='skyblue', edgecolor='black')
plt.title("Position of Accepted Answers")
plt.xlabel("Answer Position")
plt.ylabel("Frequency")
plt.xticks(range(1, max(position_counts.keys()) + 1))
plt.show()


# Scores of Accepted vs. Non-Accepted Answers
accepted_scores = []
non_accepted_scores = []

for question in posts_data:
    if question['PostTypeId'] == "1" and question['AcceptedAnswerId']:
        # Filter answers to this question
        answers = [
            post for post in posts_data
            if post['PostTypeId'] == "2" and post['ParentId'] == question['Id']
        ]
        for answer in answers:
            if answer['Id'] == question['AcceptedAnswerId']:
                accepted_scores.append(int(answer['Score'] or 0))
            else:
                non_accepted_scores.append(int(answer['Score'] or 0))

# Display statistics
print(f"\nAverage Score of Accepted Answers: {np.mean(accepted_scores):.2f}")
print(f"Average Score of Non-Accepted Answers: {np.mean(non_accepted_scores):.2f}")
print(f"\nMedian Score of Accepted Answers: {np.median(accepted_scores):.2f}")
print(f"Median Score of Non-Accepted Answers: {np.median(non_accepted_scores):.2f}")

data = pd.DataFrame({
    'Score': accepted_scores + non_accepted_scores,
    'Type': ['Accepted'] * len(accepted_scores) + ['Non-Accepted'] * len(non_accepted_scores)
})

# Violin plot with updated syntax
plt.figure(figsize=(10, 6))
sns.violinplot(
    data=data,
    x='Type',
    y='Score',
    hue='Type',
    inner='quartile',
    cut=0,
    palette='muted',
    dodge=False,  # Disable split/dodge since `Type` is already used for x-axis
    legend=False  # No need for a redundant legend here
)
plt.title("Score Distribution: Accepted vs Non-Accepted Answers")
plt.xlabel("Answer Type")
plt.ylabel("Score")
plt.ylim(-10, 100)  # Adjust range to exclude extreme outliers
plt.show()


# Count answers per tag
tag_answer_counts = defaultdict(int)

for post in posts_data:
    if post['PostTypeId'] == "1" and post['Tags']:
        tags = post['Tags'].strip('|').split('|')
        answer_count = int(post['AnswerCount'] or 0)
        for tag in tags:
            tag_answer_counts[tag] += answer_count

# Top tags by answer count
top_tags_by_answers = sorted(tag_answer_counts.items(), key=lambda x: x[1], reverse=True)[:10]

# Display and visualize
print("\nTop Tags by Total Answers:")
for tag, count in top_tags_by_answers:
    print(f"{tag}: {count}")

tags, counts = zip(*top_tags_by_answers)
plt.figure(figsize=(10, 5))
plt.bar(tags, counts, color='limegreen', edgecolor='black')
plt.title("Top Tags by Total Answers")
plt.xlabel("Tags")
plt.ylabel("Total Answers")
plt.xticks(rotation=45)
plt.show()


# Extract views and scores
view_scores = [
    (int(post['ViewCount'] or 0), int(post['Score'] or 0))
    for post in posts_data
    if post['PostTypeId'] == "1" and post['ViewCount'] and post['Score']
]

views, scores = zip(*view_scores)
correlation = np.corrcoef(views, scores)[0, 1]

print(f"\nCorrelation Between View Count and Score: {correlation:.2f}")

# Scatter plot
plt.figure(figsize=(8, 5))
plt.scatter(views, scores, alpha=0.5, color='teal', edgecolor='black')
plt.title("View Count vs. Score")
plt.xlabel("View Count")
plt.ylabel("Score")
plt.show()


# Length of Questions and Answers
question_lengths = [
    len(post['Body'].split()) for post in posts_data
    if post['PostTypeId'] == "1" and post['Body']
]

answer_lengths = [
    len(post['Body'].split()) for post in posts_data
    if post['PostTypeId'] == "2" and post['Body']
]

print(f"\nAverage Length of Questions: {np.mean(question_lengths):.2f} words")
print(f"Median Length of Questions: {np.median(question_lengths):.2f} words")
print(f"Average Length of Answers: {np.mean(answer_lengths):.2f} words")
print(f"Median Length of Answers: {np.median(answer_lengths):.2f} words")

# Visualize length distributions
plt.figure(figsize=(10, 5))
plt.hist(answer_lengths, bins=range(0, 150, 10), alpha=0.7, label="Answers", color='orange', edgecolor='black')
plt.hist(question_lengths, bins=range(0, 150, 10), alpha=0.7, label="Questions", color='blue', edgecolor='black')
plt.title("Length Distribution of Questions and Answers")
plt.xlabel("Length (in words)")
plt.ylabel("Frequency")
plt.legend()
plt.show()


# Filter unanswered questions
unanswered_questions = [
    post for post in posts_data
    if post['PostTypeId'] == "1" and int(post.get('AnswerCount', 0)) == 0
]

# Display unanswered question statistics
print(f"\nTotal Unanswered Questions: {len(unanswered_questions)}")
unanswered_percentage = (len(unanswered_questions) / len([q for q in posts_data if q['PostTypeId'] == "1"])) * 100
print(f"Percentage of Unanswered Questions: {unanswered_percentage:.2f}%")

# Tags associated with unanswered questions
tag_counts_unanswered = Counter()
for question in unanswered_questions:
    if question['Tags']:
        tags = question['Tags'].strip('|').split('|')
        tag_counts_unanswered.update(tags)

# Top 10 tags in unanswered questions
top_tags_unanswered = tag_counts_unanswered.most_common(10)

print("\nTop Tags in Unanswered Questions:")
for tag, count in top_tags_unanswered:
    print(f"{tag}: {count}")

# Visualize tags in unanswered questions
tags, counts = zip(*top_tags_unanswered)
plt.figure(figsize=(10, 5))
plt.bar(tags, counts, color='salmon', edgecolor='black')
plt.title("Top Tags in Unanswered Questions")
plt.xlabel("Tags")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.show()


# Count tag co-occurrences
tag_cooccurrence = defaultdict(int)

for post in posts_data:
    if post['PostTypeId'] == "1" and post['Tags']:
        tags = post['Tags'].strip('|').split('|')
        # Generate all pairs of tags
        for tag_pair in combinations(sorted(tags), 2):
            tag_cooccurrence[tag_pair] += 1

# Sort co-occurrences by count
sorted_cooccurrences = sorted(tag_cooccurrence.items(), key=lambda x: x[1], reverse=True)[:10]

# Display and visualize top tag co-occurrences
print("\nTop Tag Co-Occurrences:")
for pair, count in sorted_cooccurrences:
    print(f"{pair}: {count}")

pairs, counts = zip(*sorted_cooccurrences)
pairs = [' & '.join(pair) for pair in pairs]

plt.figure(figsize=(10, 5))
plt.bar(pairs, counts, color='lightblue', edgecolor='black')
plt.title("Top Tag Co-Occurrences")
plt.xlabel("Tag Pairs")
plt.ylabel("Count")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# Top 50 frequent words
# Preprocess text for Title and Body fields
for post in posts_data:
    post['Preprocessed_Body'] = preprocess_text(post['Body'] or "")
    post['Preprocessed_Title'] = preprocess_text(post['Title'] or "")

# Combine all preprocessed text into a single list
all_tokens = []
for post in posts_data:
    all_tokens.extend(post['Preprocessed_Body'])
    all_tokens.extend(post['Preprocessed_Title'])

# Count word frequencies
word_counts = Counter(all_tokens)
top_50_words = word_counts.most_common(50)

# Print top 50 frequent words
print("Top 50 Frequent Words:")
for word, count in top_50_words:
    print(f"{word}: {count}")

# Visualize the top 50 words
words, counts = zip(*top_50_words)
plt.figure(figsize=(10, 5))
plt.bar(words, counts, color='skyblue')
plt.xticks(rotation=90)
plt.title("Top 50 Frequent Words")
plt.xlabel("Words")
plt.ylabel("Frequency")
plt.show()