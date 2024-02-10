# %%
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from util.comments import process_comments, process_videos_items_in_playlist
import sys
import json
from dotenv import load_dotenv
load_dotenv(r'C:\path\to\myy\directory\Scripts\Python Projects\YT_Purified_Radio\util\.env.example')
print("Jobs Done")

# %%
#vid_id = "l2DlaF6q4eY"

#initialize the YT API client

yt_client = build("youtube", "v3", developerKey=YT_DEVELOPER_KEY)

def get_playlist_items(playlist_id):
    playlist_item_list = []

    request = yt_client.playlistItems().list(
        part="id,snippet,status",
        playlistId=playlist_id,
        maxResults=100
    )
    response = request.execute()
    playlist_item_list.extend(process_videos_items_in_playlist(response['items']))

    # if there is nextPageToken, then keep calling the API

    while response.get('nextPageToken', None):
        request = yt_client.playlistItems().list(
            part='id,snippet,status',
            playlistId=playlist_id,
            maxResults=100,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        #print(response)
        playlist_item_list.extend(process_videos_items_in_playlist(response['items']))

    return playlist_item_list
    

def get_comments(video_id, to_csv=False):
    comments_list = []
    
    request = yt_client.commentThreads().list(
        part='replies,snippet',
        order="relevance",
        maxResults=100,
        videoId=video_id,
    )
    response = request.execute()
    #print(response)
    #print(response['items'])
    #return print(process_comments(response['items']))
    comments_list.extend(process_comments(response['items'],replies=False, commenter_name = '@daa-music'))

    # if there is nextPageToken, then keep calling the API
    while response.get('nextPageToken', None):
        request = yt_client.commentThreads().list(
            part='replies,snippet',
            order="relevance",
            maxResults=100,
            videoId=video_id,
            pageToken=response['nextPageToken']
        )
        response = request.execute()
        #print(response)
        comments_list.extend(process_comments(response['items'],replies=False, commenter_name = "@daa-music"))
        
    #print(response['items'])
    #return print(process_comments(response['items']))
    return comments_list


# %%
video_ids = get_playlist_items("PL-Wt-lDOPUzHBDXm8ODmax9oHhVX6YtEb")
all_comments = []
print('Processing Videos in specified Playlist. Please standby broham...')

for video in video_ids:
    video_id = video['video_id'] # Getting the video ID
    video_name = video['video_name']  # Getting the video name
    comments = get_comments(video_id) # Getting comments for the video

    for comment in comments:
        updated_comment = {'video_name': video_name} # Adding the video name to each comment grouping (create a new dictionary so that the video_name is the first key)
        updated_comment.update(comment)
        all_comments.append(updated_comment) # adds the modified comment to the list

    
print('Process complete')

# %%
with open('track_lists.json', 'w',) as file:
    json.dump(all_comments, file, indent=2)

print('exported results to a json file')

# %%



