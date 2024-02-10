# %%
import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
import os
import time
import regex as re
from dotenv import load_dotenv

print("jobs done")

# %%
## Load Track List JSON File
with open('purified_radio_track_lists_not_flattened.json', 'r') as file:
    track_list = json.load(file)

#print(track_list[0][0]['track_number'])
    
## Load Environment Variables
load_dotenv(r'C:\path\to\my\directory\Python311\Scripts\Python Projects\YT_Purified_Radio\util\.env')

# %%
def get_spotify_client():
    try:
        with open('token_info.json', 'r') as file:
            token_info = json.load(file)
        return spotipy.Spotify(auth=token_info['access_token'])
    
    except Exception as e:
        print(f"Error getting Spotify client: {e}")
        return None

def save_state(current_index, confirmed_tracks, tracks_not_found):
    with open('state.json', 'w') as file:
        json.dump({'current_index': current_index, 'confirmed_tracks': confirmed_tracks, 'tracks_not_found': tracks_not_found}, file, indent=2)

def load_state():
    try:
        with open('state.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'current_index': 0, 'confirmed_tracks': [], 'tracks_not_found':[]}

# %%
def format_track_data():
    #Create variable for saved JSON with purified track information extracted earlier
    purified_videos = track_list['purifiedRadioTracks']['videos']

    #Initialize an empty list to store track and artist info
    list = []
    for video in purified_videos:
         video_name = video['videoName']
         for track in video['tracks']:
             track_data = {
                 'video_name': video_name,
                 'track_name': track['trackName'],
                 'track_artist':track['artist']
             }
             list.append(track_data)
             # Add each track's data as a dictionary to the list
    return list

# %%
def search_purified_weekly_tracks():
    print("Here we go ! Process en cours")
    sp = get_spotify_client()
    if not sp:
        return 'Error initializing Spotify client.'

    try:
        user_id = sp.current_user()['id']
    except Exception as e:
        print(f"Error during Spotify API call: {e}")
        return 'You are not logged in or there was an error with the Spotify API.'
    #print(f"User ID: {user_id}")   

    spotify_track_list = []
    state = load_state()
    current_index = state['current_index']
    confirmed_tracks = state['confirmed_tracks']
    tracks_not_found = state['tracks_not_found']

    batch_counter = 0  

    track_and_artist_data = format_track_data()

    for i in range(current_index, len(track_and_artist_data)):
        #print(f"Processing track {i}")
        #match_confirmed = False  # Initialize match_confirmed here
        data = track_and_artist_data[i] #define variable to iterate over source track data

        #Reg Expression to parse song and artist names that contain accented characters further downstream
        parse_pattern = re.compile(r"([\pL\pM\p{Zs}.-0-9\s]+)") 

        #Parse Track name from source track data
        track_match = parse_pattern.match(data['track_name']) 
        clean_track_name = track_match[0].strip() if track_match else ""

        #Parse Artist name(s) from source track data
        artist_match = parse_pattern.findall(data['track_artist'])
        clean_artists = [value.strip() for value in artist_match]

        #Search query via Spotify API. Printing number of results
        track_search = sp.search(q=f'track:"{clean_track_name}" artist:"{clean_artists[0]}"', type="track")
        #print(f"Number of items found for track {i}: {len(track_search['tracks']['items'])}")

        #Regular Expression to aid in searching for tracks that contain mixes. I want to capture songs that are mixes where possible within search results
        remix_pattern = re.compile(r"(.*[mM]ix.*)")
        remix_match_found = False
        #Outer Loop to run through API response Items

        for item in track_search['tracks']['items']:
            api_track_name = item['name'].strip() 
    
            #song_name_matches = remix_pattern.findall(api_track_name) if track_search else ""
            #song_names = [value.strip() for value in song_name_matches]
            if remix_pattern.search(api_track_name):
                for artist in item['artists']:
                    api_artist_name = artist['name'].strip()
                    if any(str(clean_artist.upper()) == str(api_artist_name.upper()) for clean_artist in clean_artists):
                        spotify_dict = {
                            'song_name': api_track_name,
                            'name_artist': api_artist_name,
                            'song_id': item['id']
                        }
                        confirmed_tracks.append(spotify_dict)
                        remix_match_found = True
                        break
                    break
                break
                
        
                

        if not remix_match_found:
            for item in track_search['tracks']['items']:
                api_track_name = item['name'].strip()
                for artist in item['artists']:
                    api_artist_name = artist['name'].strip()
                    for n in range(0, len(artist_match)):
                    #art = f"{artist_match[n]}"
                    #f len(track_search['tracks']['items']) >= 2:
                        if str(api_track_name.upper()) == str(clean_track_name.upper()) and any(str(clean_artist.upper()) == str(api_artist_name.upper()) for clean_artist in clean_artists):
                            spotify_dict = {
                            'song_name': api_track_name,
                            'name_artist': api_artist_name,
                            'song_id': item['id']
                             }
                            confirmed_tracks.append(spotify_dict)
                            break
                        break
                    break
                break
                            
        if len(track_search['tracks']['items']) == 0:
            spotify_dict = {
                            'song_name': clean_track_name,
                            'name_artist': clean_artists,
                            'song_id': None
                            }
            tracks_not_found.append(spotify_dict)
            
        
    
                

                    #if len(track_search['tracks']['items']) >= 2:
                            
                        #for t in range(0, len(song_name_matches)):# Loop through search results for remixes when there's more than one result and attempt to match based on cleaned data from source track data
                            #song_name_match = song_name_matches[t]
                            #if str(song_name_match.upper()) == str(clean_track_name.upper()) or any(str(clean_artist.upper()) == str(api_artist_name.upper()) for clean_artist in clean_artists):
                            #    spotify_dict = {
                            #            'song_name': api_track_name,
                            #            'name_artist': api_artist_name,
                            #            'song_id': item['id']
                            #    }
                            #    confirmed_tracks.append(spotify_dict)
                            #    match_confirmed = True
                                
                

                            #print("Match found. Please confirm the track item is correct: ",
                            #    f"\nSpotify Song Title: {api_track_name} -> Youtube Song Title: {clean_track_name}",
                            #    f"\nSpotify Song Artist: {api_artist_name} -> Youtube Artist Name: {clean_artists[n]}\n\n")
                            #user_response = str(input("Is the match valid ? (Y/N): "))
                            #while user_response.upper() != 'Y' and user_response.upper() != 'N':
                                #print("Invalid Value, please input either 'Y' for Yes or 'N' for No")
                                #user_response = input("Let's try this again. Is the match valid ? (Y/N): ")
    
                            #if user_response == 'Y':
                            #    spotify_dict = {
                            #            'song_name': api_track_name,
                            #            'name_artist': api_artist_name,
                            #            'song_id': item['id']
                            #        }
                            #    confirmed_tracks.append(spotify_dict)
                            #    match_confirmed = True  # Set match_confirmed to True when match is confirmed
                            #    break
                            #elif user_response.upper() == 'N':
                            #    continue
                    #elif len(track_search['tracks']['items']) == 1: #No validation required, just save data for the only result
                    #    spotify_dict = {
                    #                    'song_name': api_track_name,
                    #                    'name_artist': api_artist_name,
                    #                    'song_id': item['id']
                    #                }
                    #    confirmed_tracks.append(spotify_dict)
                    #    match_confirmed = True
    
                    #else: # Condition to capture tracks from source track data that did not return any results in Spotify
                    #    spotify_dict = {
                    #                    'song_name': clean_track_name,
                    #                    'name_artist': clean_artists,
                    #                    'song_id': None
                    #                }
                    #    confirmed_tracks.append(spotify_dict)
                    #    match_confirmed = True
    
                #if match_confirmed:
                #    break
        
        current_index += 1
        batch_counter += 1
    
        if batch_counter >= 2:
            save_state(current_index, confirmed_tracks, tracks_not_found)
            batch_counter = 0  # Reset for next batch

    save_state(current_index, confirmed_tracks, tracks_not_found)
    return "All values have been evaluated. Job is done"



# %%
search_purified_weekly_tracks()

# %%



