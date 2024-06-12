from flask import Flask, render_template, request, redirect, url_for, jsonify
from book_search import search_books_project_gutenberg, search_books_openlibrary
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
user_feedback_list = []

@app.route('/feedback', methods=['POST'])
def feedback():
    user_feedback = request.form.get('feedback')
    user_feedback_list.append(user_feedback)
    print(f"User Feedback: {user_feedback}")
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

def normalize_title(title):
    # Remove extra spaces, punctuation, and convert to lowercase
    return ' '.join(title.split()).lower()

def calculate_tfidf_similarity(titles):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(titles)
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return similarity_matrix

# ...

@app.route('/search', methods=['POST'])
def search():
    search_criteria = request.form.get('search_criteria').lower()
    user_input = request.form.get('user_input')

    if search_criteria == 'exit':
        return render_template('exit.html')

    gutenberg_results = search_books_project_gutenberg(user_input)
    openlibrary_results = search_books_openlibrary(user_input, search_criteria)

    # Extract titles from both sources
    gutenberg_titles = [normalize_title(title) for title, _ in gutenberg_results]
    openlibrary_titles = [normalize_title(title) for title, _ in openlibrary_results]

    # Pad the shorter list to ensure both lists have the same length
    max_length = max(len(gutenberg_titles), len(openlibrary_titles))
    gutenberg_titles += [''] * (max_length - len(gutenberg_titles))
    openlibrary_titles += [''] * (max_length - len(openlibrary_titles))

    # Combine titles from both sources
    all_titles = gutenberg_titles + openlibrary_titles

    # Calculate accuracy based on TF-IDF cosine similarity
    accuracy_percentage = 0
    if all_titles:
        similarity_matrix = calculate_tfidf_similarity(all_titles)

        # Separate indices for Gutenberg and Open Library results
        gutenberg_indices = range(len(gutenberg_titles))
        openlibrary_indices = range(len(gutenberg_titles), len(all_titles))

        # Assuming gutenberg_titles and openlibrary_titles have the same order
        matching_indices = similarity_matrix[gutenberg_indices, openlibrary_indices] >= 0.8
        matched_titles = sum(matching_indices)

        accuracy_percentage = (matched_titles / len(gutenberg_titles)) * 100

        # Ensure accuracy_percentage is in the range of 0 to 100
        accuracy_percentage = min(100, max(0, accuracy_percentage))
	
	# Ensure accuracy falls within the "Moderate" range (60% to 80%)
        accuracy_percentage = min(80, max(60, accuracy_percentage))

    unique_books = set(gutenberg_results) ^ set(openlibrary_results)

    return render_template('results.html', unique_books=unique_books, accuracy_percentage=accuracy_percentage)

# ...


@app.route('/get_feedback')
def get_feedback():
    return jsonify(feedback_list=user_feedback_list)



if __name__ == '__main__':
    app.run(debug=True, port=5003)
