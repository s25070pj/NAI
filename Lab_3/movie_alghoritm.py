import sys
import pandas as pd
from sklearn.cluster import KMeans
import requests


# to jest z gita a nie chat

def load_data():
    """Load CSV data into Pandas objects"""
    movies_df = pd.read_csv('movies.csv')
    users_df = pd.read_csv('users.csv')
    ratings_df = pd.read_csv('ratings.csv')
    return movies_df, users_df, ratings_df


def create_user_movie_matrix(ratings_df):
    """Create user-movie matrix.
    :param ratings_df: Pandas dataframe object, returned by load_data() function
    """
    ratings_matrix = ratings_df.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
    return ratings_matrix


def cluster_users(ratings_matrix, n_clusters=5):
    """Cluster users based on movie rating.
    :param ratings_matrix: ratings matrix returned by function create_user_movie_matrix
    :param n_clusters: number of clusters
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = kmeans.fit_predict(ratings_matrix)
    ratings_matrix['cluster'] = clusters
    return ratings_matrix, clusters


def get_recommendations_for_user(user_id, ratings_df, movies_df, clustered_ratings_matrix, n_recommendations=5):
    """Find n-recommendations for a user from a pool of movies not watched by the user.
    :param user_id: user id
    :param ratings_df: Pandas dataframe object, returned by load_data() function
    :param movies_df: Pandas dataframe object, returned by create_user_movie_matrix() function
    :param clustered_ratings_matrix: clustered ratings matrix
    :param n_recommendations: number of recommendations
    """
    user_cluster = clustered_ratings_matrix.loc[user_id, 'cluster']
    user_rated_movies = set(ratings_df[ratings_df['user_id'] == user_id]['movie_id'])

    cluster_users_ids = clustered_ratings_matrix[clustered_ratings_matrix['cluster'] == user_cluster].index
    cluster_movies = ratings_df[ratings_df['user_id'].isin(cluster_users_ids)]
    cluster_movies = cluster_movies[~cluster_movies['movie_id'].isin(user_rated_movies)]

    recommended_movies = cluster_movies.groupby('movie_id')['rating'].mean().sort_values(ascending=False).head(
        n_recommendations)

    recommended_movie_titles = []
    for id in recommended_movies.axes[0].values:
        recommended_movie_titles.append(movies_df.loc[id, 'title'])

    return recommended_movie_titles


def get_antirecommendations_for_user(user_id, ratings_df, movies_df, clustered_ratings_matrix, n_antirecommendations=5):
    """Find n-lowest_rated_movies for a user from a pool of movies not watched by the user.
        :param user_id: user id
        :param ratings_df: Pandas dataframe object, returned by load_data() function
        :param movies_df: Pandas dataframe object, returned by create_user_movie_matrix() function
        :param clustered_ratings_matrix: clustered ratings matrix
        :param n_antirecommendations: number of antirecommendations
        """
    user_cluster = clustered_ratings_matrix.loc[user_id, 'cluster']
    user_rated_movies = set(ratings_df[ratings_df['user_id'] == user_id]['movie_id'])

    cluster_users_ids = clustered_ratings_matrix[clustered_ratings_matrix['cluster'] == user_cluster].index
    cluster_movies = ratings_df[ratings_df['user_id'].isin(cluster_users_ids)]
    cluster_movies = cluster_movies[~cluster_movies['movie_id'].isin(user_rated_movies)]

    lowest_rated_movies = cluster_movies.groupby('movie_id')['rating'].mean().sort_values().head(n_antirecommendations)

    antirecommended_movie_titles = []
    for movie_id in lowest_rated_movies.index:
        title = movies_df.loc[movie_id, 'title']
        antirecommended_movie_titles.append(title)

    return antirecommended_movie_titles


def get_movie_info(movie_title):
    """Fetch additional movie details from external API.
    :param movie_title: movie title
    """
    api_key = "b3ccb2b7"
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"Error": "Unable to fetch movie details"}


movies_df, users_df, ratings_df = load_data()
ratings_matrix = create_user_movie_matrix(ratings_df)

n_clusters = 5
clustered_ratings_matrix, clusters = cluster_users(ratings_matrix, n_clusters)

user_id = int(sys.argv[1])

recommendations = get_recommendations_for_user(user_id, ratings_df, movies_df, clustered_ratings_matrix)
print(f"Rekomendowane filmy dla użytkownika {user_id}:")
for title in recommendations:
    movie_info = get_movie_info(title)
    print(f"- {title} ({movie_info.get('Year', 'N/A')}) - {movie_info.get('Plot', 'No details available')}")


antirecommendations = get_antirecommendations_for_user(user_id, ratings_df, movies_df, clustered_ratings_matrix)
print(f"\nAntyrekomendacje dla użytkownika {user_id}:")
for title in antirecommendations:
    movie_info = get_movie_info(title)
    print(f"- {title} ({movie_info.get('Year', 'N/A')}) - {movie_info.get('Plot', 'No details available')}")


