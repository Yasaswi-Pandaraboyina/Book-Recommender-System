import pandas as pd
from collections import defaultdict

# Loading the dataset
ratings_df = pd.read_csv('Ratings.csv', sep=';', names=['User-ID', 'ISBN', 'Rating'], skiprows=1)

# Mapping each unique User-ID and ISBN starting from 1
user_to_index = {user: i + 1 for i, user in enumerate(ratings_df['User-ID'].unique())}
isbn_to_index = {isbn: i + 1 for i, isbn in enumerate(ratings_df['ISBN'].unique())}

# Dictionary to store each user's ratings, {isbn_index: rating}
user_ratings = defaultdict(dict)
# Populate the user_ratings dictionary with sequential user and ISBN indices
for _, row in ratings_df.iterrows():
    user_idx = user_to_index[row['User-ID']]  
    isbn_idx = isbn_to_index[row['ISBN']]     
    user_ratings[user_idx][isbn_idx] = row['Rating']  
# Write the LIBSVM formatted output to a file, without user ID
with open('user_booklibsvmnew.libsvm', 'w') as f:
    for user_idx in sorted(user_ratings):
        ratings = [f'{isbn_idx}:{rating}' for isbn_idx, rating in sorted(user_ratings[user_idx].items())]
        line = ' '.join(ratings) + '\n'  
        f.write(line)
print("LIBSVM file has been created.")
