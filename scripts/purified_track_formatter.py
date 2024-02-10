import pandas as pd
import json
import re
import csv
##NOTE - Some track lists are not  extracted properly in this script due to inconsistent formatting on some of the older videos. I will later update to check for these inconsistent formats and add them in later.
print("jobs done")

# load JSON file w/ Track Information
with open('track_lists.json', 'r') as file:
    purified_track_info = json.load(file)

#print(purified_track_info)

#initialize track info dictionary with empty values
purifiedRadioTracks = {'videos': []}

# Reg Expression Logic for parsing the respective values for each track_info dictionary key. This will be taken within JSON 'text' key

regex_pattern = re.compile(r'(\d{2})-\s(\d{2}:\d{2})\s(\b[a-zA-Z].*?)\s-\s(.*?)(?=\s*\d{2}-|\s*$|\r\n)')

#test_str = purified_track_info[2]['text']
#print(test_str)
print("Extracting the track information into a more readable format bruv...")
for purified_track in purified_track_info:
    
    video_tracks = [] # This list will hold all tracks for each individual video
    video_name = purified_track['video_name']
    info_strs = regex_pattern.findall(purified_track['text'])

    for substr in info_strs:
        track_dict = {
            'trackNumber': substr[0],
            'timestamp': substr[1],
            'artist': substr[2],
            'trackName': substr[3]
        }
        video_tracks.append(track_dict) # Add the track info to the temporary list
        
    #Create dictionary for each video and add it to the purifiedRadioTracks list
    video_dict = {'videoName': video_name, 'tracks': video_tracks}
    purifiedRadioTracks['videos'].append(video_dict)

    
print("The job is done")
#problem_str = '12- 53:55 Willy Commy - Alcyone (Original Mix)[Beatlick]'
#problem_reg_str = regex_pattern.findall(problem_str)
#print(problem_reg_str)
#print(track_info)


#print(track_info)

##flattened_track_info = [track for video in track_info for track in video]

#print("Writing file to CSV my brother")
#csv_columns = ['video_name', 'track_number', 'timestamp', 'artist', 'track_name']
#csv_file = 'purified_radio_track_lists.csv'
#with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    #write = csv.DictWriter(file, fieldnames=csv_columns)
    #write.writeheader()
    #write.writerows(flattened_track_info)


print("Writing file to JSON file too my brother")
with open('purified_radio_track_lists_not_flattened.json', 'w') as file:
    json.dump({'purifiedRadioTracks': purifiedRadioTracks}, file, indent=2)

print("job's done")