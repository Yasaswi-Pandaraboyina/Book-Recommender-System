import math
from collections import defaultdict

def read_library_data():
    """Load and preprocess library data"""
    print("Loading library catalog...")
    book_titles = {}
    catalog_mapping = {}
    
    with open('Books.csv', 'r', encoding='utf-8') as file:
        next(file)  # Skip header
        for index, line in enumerate(file, start=1):
            try:
                content = line.strip().split(';')
                book_id = content[0].strip()
                book_name = content[1].strip()
                book_titles[book_id] = book_name
                catalog_mapping[index] = book_id
            except:
                continue

    print("Processing user reading history...")
    reading_history = defaultdict(dict)
    with open('user_booklibsvmnew.libsvm', 'r') as file:
        for reader_id, line in enumerate(file, start=1):
            entries = line.strip().split()
            for entry in entries:
                book_idx, preference = map(float, entry.split(':'))
                reading_history[reader_id][int(book_idx)] = preference

    print("Computing reader preference patterns...")
    preference_vectors = {
        reader: math.sqrt(sum(pref * pref for pref in preferences.values()))
        for reader, preferences in reading_history.items()
        if sum(pref * pref for pref in preferences.values()) > 0
    }

    return reading_history, book_titles, preference_vectors, catalog_mapping

def calculate_reader_similarity(reader1, reader2, history, vectors):
    """Calculate similarity between readers"""
    if reader1 not in vectors or reader2 not in vectors:
        return 0.0
    
    common_books = set(history[reader1]) & set(history[reader2])
    if not common_books:
        return 0.0
    
    similarity_score = sum(history[reader1][book] * history[reader2][book] for book in common_books)
    magnitude = vectors[reader1] * vectors[reader2]
    
    return similarity_score / magnitude if magnitude > 0 else 0.0

def generate_book_suggestions(target_reader, history, vectors, neighbor_count=10):
    """Generate personalized book suggestions"""
    reader_similarities = []
    for other_reader in history:
        if other_reader != target_reader:
            similarity = calculate_reader_similarity(target_reader, other_reader, history, vectors)
            if similarity > 0:
                reader_similarities.append((other_reader, similarity))
    
    nearest_neighbors = sorted(reader_similarities, key=lambda x: x[1], reverse=True)[:neighbor_count]
    if not nearest_neighbors:
        return []
    
    current_books = set(history[target_reader])
    suggestion_scores = defaultdict(float)
    
    for similar_reader, similarity in nearest_neighbors:
        for book, rating in history[similar_reader].items():
            if book not in current_books:
                suggestion_scores[book] += rating * similarity
    
    return sorted(suggestion_scores.items(), key=lambda x: x[1], reverse=True)[:5]

def create_recommendation_file():
    history, titles, vectors, catalog = read_library_data()
    
    print("Creating personalized recommendations...")
    with open('library_suggestions.csv', 'w', encoding='utf-8') as file:
        file.write('User_ID,Book_ID,Book_Title,Recommendation_Score\n')
        
        for reader in history.keys():
            suggestions = generate_book_suggestions(reader, history, vectors)
            
            for book_id, confidence in suggestions:
                book_identifier = catalog.get(book_id, str(book_id))
                book_name = titles.get(book_identifier, f"Book_{book_id}")
                weighted_score = min(max(confidence * 5, 1), 10)
                file.write(f'{reader},{book_id},"{book_name}",{weighted_score}\n')
    
    print("Library recommendations generated successfully!")

if __name__ == "__main__":
    create_recommendation_file()
