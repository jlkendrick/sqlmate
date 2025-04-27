# This script is used to create the datasets for the song, album, and artist tables
# from the full, raw dataset. It does all the necessary preprocessing required to
# link the tables together and save them as CSV files.

from typing import Tuple
import pandas as pd
import csv

# Loads the full dataset with all the columns from the CSV file and do some preprocessing
def load_full_df() -> pd.DataFrame:
	df = pd.read_csv('raw/top_10000_1950-now.csv')

	# Drop irrelevant columns
	df = df.drop(columns=['Disc Number', 'Added By', 'Added At', 'Copyrights'])

	# Extract Spotify IDs from URIs and rename columns
	df['Spotify Track ID'] = df['Track URI'].apply(lambda x: x.split(':')[-1] if isinstance(x, str) else None)
	df['Spotify Artist ID(s)'] = df['Artist URI(s)'].apply(lambda x: (', '.join(y.split(':')[-1] for y in x.split(', ')) if ', ' in x else x.split(':')[-1]) if isinstance(x, str) else None)
	df['Spotify Album ID'] = df['Album URI'].apply(lambda x: (x.split(':')[-1]) if isinstance(x, str) else None)
	df['Spotify Album Artist ID(s)'] = df['Album Artist URI(s)'].apply(lambda x: (', '.join(y.split(':')[-1] for y in x.split(', ')) if ', ' in x else x.split(':')[-1]) if isinstance(x, str) else None)

	# Drop rows with missing Spotify IDs or bad values for Key
	df = df.dropna(subset=['Spotify Track ID', 'Spotify Artist ID(s)', 'Spotify Album ID', 'Key', 'Track Name']).reset_index(drop=True)

	return df

# Creates a copy of the full dataframe but with only the relevant columns for the song table
def create_song_df(df: pd.DataFrame) -> pd.DataFrame:
	# These are the relevant columns for the song table
	song_cols = ['Track Name', 'Track Preview URL', 'Track Duration (ms)', 'Explicit', 'Popularity', 'Danceability', 'Energy', 'Key', 'Loudness', 'Mode', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 'Time Signature', 'ISRC', 'Label', 'Spotify Track ID', 'Spotify Artist ID(s)', 'Spotify Album ID']
	df_song = df[song_cols].copy()

	# Assign the primary key/ID
	df_song['Track ID'] = df_song.index
	df_song['Track ID'] = df_song['Track ID'].apply(lambda x: str(x))

	return df_song

# Creates a copy of the full dataframe but with only the relevant columns for the album table
def create_album_df(df: pd.DataFrame) -> pd.DataFrame:
	# These are the relevant columns for the album table
	album_cols = ['Album Name', 'Album Release Date', 'Album Image URL', 'Spotify Album ID', 'Spotify Album Artist ID(s)']
	df_album = df[album_cols].copy()

	# Drop the duplicates because multiple songs can be from the same album
	df_album = df_album.drop_duplicates(subset=['Spotify Album ID']).reset_index(drop=True)

	# Assign the primary key/ID
	df_album['Album ID'] = df_album.index
	df_album['Album ID'] = df_album['Album ID'].apply(lambda x: str(x))

	return df_album

# Creates a copy of the full dataframe but with only the relevant columns for the artist table, doing some preprocessing as well
def create_artist_df(df: pd.DataFrame) -> pd.DataFrame:
	# These are the relevant columns for the artist table
	artist_cols = ['Artist Name(s)', 'Artist Genres', 'Spotify Artist ID(s)']
	df_artist = df[artist_cols].copy()

	# Drop the duplicates because multiple songs can be from the same artist
	df_artist = df_artist.drop_duplicates(subset=['Spotify Artist ID(s)'])

	df_album = load_full_df()
	df_album = df_album.drop_duplicates(subset=['Spotify Album ID']).reset_index(drop=True)

	# The artists are given as a string with multiple artists separated by ', '
	# but we want individual rows for each artist, so we split them:

	# Used as a heuristic to deduce the genres of an artist we don't have a single row for
	def intersect(a: str, b: str) -> str:
		if not isinstance(a, str) or not isinstance(b, str):
			return None
		return ','.join(list(set(a.split(',')) & set(b.split(','))))
	

	# Idea is that we know rows with only one artist (primary artist) are good
	# and artists that are only mentioned via a song (secondary artist) still need to 
	# be included in the artist table, but we need to deduce their genres since we don't have an explicit row for them
	primary_artist_rows = {}
	secondary_artist_rows = {}
	for _, row in df_artist.iterrows():
		artist_ids = row['Spotify Artist ID(s)']

		# If there are multiple artists
		if ', ' in artist_ids:
			artist_ids = artist_ids.split(', ')
			for i, artist_id in enumerate(artist_ids):
				secondary_artist_rows[artist_id] = {
					'Spotify Artist ID': artist_id,
					'Artist Name': row['Artist Name(s)'].split(', ')[i], # IDs and names are in the same order
					'Artist Genres': row['Artist Genres'] if artist_id not in secondary_artist_rows else intersect(secondary_artist_rows[artist_id]['Artist Genres'], row['Artist Genres'])
				}
		else:
			# Reassignment shouldn't change anything (values should be the same)
			primary_artist_rows[artist_ids] = {
				'Spotify Artist ID': artist_ids,
				'Artist Name': row['Artist Name(s)'],
				'Artist Genres': row['Artist Genres']
			}
	
	# Now we need to repeat the process for artists that are only mentioned in the album table
	for _, row in df_album.iterrows():
		print(f"Processing Album ID: {row['Spotify Album ID']} for Artist IDs: {row['Spotify Album Artist ID(s)']}")
		artist_ids = row['Spotify Album Artist ID(s)']

		# If there are multiple artists
		if ', ' in artist_ids:
			artist_ids = artist_ids.split(', ')
			for i, artist_id in enumerate(artist_ids):
				secondary_artist_rows[artist_id] = {
					'Spotify Artist ID': artist_id,
					'Artist Name': row['Album Artist Name(s)'].split(', ')[i], # IDs and names are in the same order
					'Artist Genres': row['Artist Genres'] if artist_id not in secondary_artist_rows else intersect(secondary_artist_rows[artist_id]['Artist Genres'], row['Artist Genres'])
				}
		else:
			# Reassignment shouldn't change anything (values should be the same)
			primary_artist_rows[artist_ids] = {
				'Spotify Artist ID': artist_ids,
				'Artist Name': row['Artist Name(s)'],
				'Artist Genres': row['Artist Genres']
			}

	# Primaries we keep, but if a secondary is not a primary, we add it with the genres deduced
	for artist_id, artist_info in secondary_artist_rows.items():
		if artist_id not in primary_artist_rows:
			primary_artist_rows[artist_id] = artist_info
	
	# Create the new (expanded) artist dataframe
	df_artist = pd.DataFrame(primary_artist_rows.values())

	# Assign the primary key/ID and reorder the columns
	df_artist['Artist ID'] = df_artist.index
	df_artist['Artist ID'] = df_artist['Artist ID'].apply(lambda x: str(x))
	df_artist = df_artist[['Artist ID', 'Artist Name', 'Artist Genres', 'Spotify Artist ID']]

	return df_artist

# Link the songs, albums, and artists together by their IDs, using the Spotify IDs as identifiers
def link_dfs(df_song: pd.DataFrame, df_album: pd.DataFrame, df_artist: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
	# Create mappings from Spotify IDs to the primary keys
	artist_spotify_id_to_artist_id = {row['Spotify Artist ID']: row['Artist ID'] for _, row in df_artist.iterrows()}
	album_spotify_id_to_album_id = {row['Spotify Album ID']: row['Album ID'] for _, row in df_album.iterrows()}

	# Helpers to look up the primary keys
	def lookup_artist_id(artist_ids: str) -> str:
		if not isinstance(artist_ids, str):
			return "" # We can change these, just did this to fix int conversion error
		
		# If there are multiple artists, we need to look up each one and build a new string
		if ', ' in artist_ids:
			res = []
			for artist_id in artist_ids.split(', '):
				# If the artist is not in the mapping, we can't link it because they don't have an ID
				if artist_id not in artist_spotify_id_to_artist_id:
					res.append('')
				else:
					res.append(artist_spotify_id_to_artist_id[artist_id])
			return ', '.join(res)
		
		# If there is only one artist, just do a lookup
		else:
			if artist_ids not in artist_spotify_id_to_artist_id:
				return ""
			return str(artist_spotify_id_to_artist_id[artist_ids])
		
	def lookup_album_id(album_id: str) -> str:
		if not isinstance(album_id, str):
			return ""
		if album_id not in album_spotify_id_to_album_id:
			return ""
		return str(album_spotify_id_to_album_id[album_id])
	
	# Apply the lookups to the song dataframe.
	# Songs belong to an album and an artist, so we need to link them together
	# Albums belong to an artist, so we need to link them together
	# Artists don't belong to anything, so we don't need to link them
	df_song['Artist ID(s)'] = df_song['Spotify Artist ID(s)'].apply(lookup_artist_id)
	df_song['Album ID'] = df_song['Spotify Album ID'].apply(lookup_album_id)
	df_album['Artist ID(s)'] = df_album['Spotify Album Artist ID(s)'].apply(lookup_artist_id)

	# Do some final cleanup (rename columns and drop the old ones, type conversion)
	df_song = df_song[['Track ID', 'Track Name', 'Album ID', 'Artist ID(s)', 'Track Duration (ms)', 'Track Preview URL', 'Explicit', 'Popularity', 'Danceability', 'Energy', 'Key', 'Loudness', 'Mode', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence', 'Tempo', 'Time Signature', 'ISRC', 'Label', 'Spotify Track ID']]
	df_song = df_song.rename(columns={'Spotify Track ID': 'Spotify ID'})
	df_song['Track ID'] = df_song['Track ID'].astype(str)
	df_song['Explicit'] = df_song['Explicit'].astype(bool)
	df_song['Track Duration (ms)'] = df_song['Track Duration (ms)'].astype(int)
	df_song['Popularity'] = df_song['Popularity'].astype(int)
	df_song['Danceability'] = df_song['Danceability'].astype(float)
	df_song['Energy'] = df_song['Energy'].astype(float)
	df_song['Key'] = df_song['Key'].astype(int)
	df_song['Loudness'] = df_song['Loudness'].astype(float)
	df_song['Mode'] = df_song['Mode'].astype(int)
	df_song['Speechiness'] = df_song['Speechiness'].astype(float)
	df_song['Acousticness'] = df_song['Acousticness'].astype(float)
	df_song['Instrumentalness'] = df_song['Instrumentalness'].astype(float)
	df_song['Liveness'] = df_song['Liveness'].astype(float)
	df_song['Valence'] = df_song['Valence'].astype(float)
	df_song['Tempo'] = df_song['Tempo'].astype(float)
	df_song['Time Signature'] = df_song['Time Signature'].astype(int)

	df_album = df_album[['Album ID', 'Album Name', 'Artist ID(s)', 'Album Release Date', 'Album Image URL', 'Spotify Album ID']]
	df_album['Album ID'] = df_album['Album ID'].astype(str)
	df_album = df_album.rename(columns={'Spotify Album ID': 'Spotify ID'})

	df_artist.rename(columns={'Spotify Artist ID': 'Spotify ID'}, inplace=True)
	df_artist['Artist ID'] = df_artist['Artist ID'].astype(str)

	return df_song, df_album, df_artist

# Save the dataframes to CSV files
def save_dfs(df_song: pd.DataFrame, df_album: pd.DataFrame, df_artist: pd.DataFrame) -> None:
	df_song.to_csv('processed/track.csv', index=False, quoting=csv.QUOTE_ALL)
	df_album.to_csv('processed/album.csv', index=False, quoting=csv.QUOTE_ALL)
	df_artist.to_csv('processed/artist.csv', index=False, quoting=csv.QUOTE_ALL)

	return

def main():
	df = load_full_df()
	df_song = create_song_df(df)
	df_album = create_album_df(df)
	df_artist = create_artist_df(df)
	df_song, df_album, df_artist = link_dfs(df_song, df_album, df_artist)
	save_dfs(df_song, df_album, df_artist)

if __name__ == '__main__':
	main()