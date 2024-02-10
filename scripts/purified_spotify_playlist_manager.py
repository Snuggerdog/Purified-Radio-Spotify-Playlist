import spotipy
from flask import Flask, request, url_for, session, redirect
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import time
from dotenv import load_dotenv


print("jobs done")

## Load Environment Variables
load_dotenv(r'C:path\to\my\directory\Scripts\Python Projects\YT_Purified_Radio\util\.env')

#Assign Env Variables to objects
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

#Spotify OAuth Request Initialization
def create_spotify_oath():
    return SpotifyOAuth(client_id=client_id,
                        client_secret=client_secret,
                        redirect_uri= url_for('redirect_page', _external=True),
                         scope = 'user-read-private playlist-modify-private playlist-modify-public')


#initalize Flask application
app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'Spotify Biscuit'
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
TOKEN_INFO = 'token_info'

#Grab token
def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', external=False))

    current_time = int(time.time())

    is_expired = token_info['expires_at'] - current_time < 60
    if(is_expired):
        spotify_oath = create_spotify_oath()
        token_info = spotify_oath.refresh_access_token(token_info['refresh_token'])
    return token_info

#Set up Routes

#Home Route
@app.route('/')
def login():
    auth_url = create_spotify_oath().get_authorize_url()
    return redirect(auth_url)


#Redirect Route
@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oath().get_access_token(code)
    session[TOKEN_INFO] = token_info

    # Save token_info to a file
    with open('token_info.json', 'w') as file:
        json.dump(token_info, file)

    return redirect(url_for('create_purified_weekly_playlist', external = True))


#Functionality to perform desired function and output
@app.route('/createPurifiedWeeklyPlaylists')

def create_purified_weekly_playlist():
    
    try: 
        # get the token info from the session
        token_info = get_token()
        if not token_info:
            print('Token information is not available')
            return redirect("/")
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_id = sp.current_user()['id']
    except:
        # if the token info is not found, redirect the user to the login route
        print('User not logged in')
        return redirect("/")

    current_playlists =  sp.current_user_playlists()['items']
    playlist_name = "Purified Radio Tracks"
    for playlist in current_playlists:
        if(playlist['name'] == playlist_name):
            return f"Purified Radio Tracks playlist already exists bro ! The playlist ID is {playlist['id']}"
    #for name in video_names:
    purified_playlist = sp.user_playlist_create(user=user_id,name=playlist_name,description="Tracks from Nora en Pure's Weekly Purified Radioshow")
    purified_playlist_id = purified_playlist['id']
    return f"Playlist created ! The playlist ID is {purified_playlist_id}"

# Search tracks associated with each video name extracted, and save to a dictionary of dictonaries to reference in a later function
#@app.route('/searchPurifiedTracks')

#Migrated logic over to search_tracks_spotify.ipynb


@app.route ('/savePurifiedTracksToPlaylist')
#to cycle through tracks and save to their corresponding playlists (created earlier) based on video name value matches
def save_purified_weekly_tracks_to_playlist():
    try:
        token_info = get_token()
        if not token_info:
            print('Token information is not available')
            return redirect("/")
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_id = sp.current_user()['id']
        
    except:
        print('You not logged in')
        return redirect('/')
    
    with open('state.json', 'r') as file:
        info = json.load(file)
    
    song_ids = []
    purified_playlist_id = os.environ.get('PLAYLIST_ID')

    for i in info['confirmed_tracks']:
        uri = f"spotify:track:{i['song_id']}"
        song_ids.append(uri)

    for i in range(0, len(song_ids), 100):
        temp_list = []
        temp_list.extend(song_ids[i:i+100])
        #uri_strings = ','.join(str(id) for id in temp_list)
        sp.playlist_add_items(playlist_id=purified_playlist_id, items=temp_list, position=None)

    return "Tracks have been added. Check now !"



        


if __name__ == '__main__':
app.run(debug=True,)