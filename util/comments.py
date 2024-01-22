def process_comments(response_items, reg_comments=True, replies=True, commenter_name=None, csv_output=False):
    local_comments = []

    if response_items is None:
        print("Received None in process_comments")
        return local_comments

    for i, res in enumerate(response_items):
        try:
            # Process regular top-level comments
            if reg_comments:
                author_name = res['snippet']['topLevelComment']['snippet']['authorDisplayName']
                #print(f"Checking OG comment by {author_name}")
                #if commenter_name is None or author_name == commenter_name:
                if commenter_name == None or author_name == commenter_name:
                    #continue # skip top-level comments in loop where the author does not match the user input commenter_name
                    
                    comment = {
                        'text': res['snippet']['topLevelComment']['snippet']['textOriginal'],
                        'commentId': res['snippet']['topLevelComment']['id']
                    }
                    local_comments.append(comment)

            # Process replies
            if replies and 'replies' in res:
                for reply in res['replies']['comments']:
                    author_name = reply['snippet']['authorDisplayName']
                    #print(f"Checking reply by {author_name}")
                    #if commenter_name is None or author_name == commenter_name:
                    if commenter_name == None or author_name == commenter_name:
                        #continue #skip replies in loop where the author does not match the user input commenter_name
                        comment = {
                            'text': reply['snippet']['textOriginal'],
                            'commentId': reply['id']
                        }
                        local_comments.append(comment)

        except Exception as e:
            print(f"Error processing comment at index {i}: {e}")
            print(f"Problematic item: {res}")
            


        
            """if 'replies' in res:
                for reply in res['replies']['comments']:
                    author_name = reply['snippet']['authorDisplayName']
                    print(f"Checking reply by {author_name}")
                    if commenter_name is None or author_name == commenter_name:
                        comment = {
                            'text': reply['snippet']['textOriginal'],
                            'commentId': reply['id']
                        }
                        local_comments.append(comment)"""
    
            #else:
               

    return local_comments

def process_videos_items_in_playlist(response_items, csv_output=False):
    video_info = []
    
    if response_items is None:
        print("Received None in process_comments")
        return response_items
        
    for i, res in enumerate(response_items):
        try:
            if res['status']['privacyStatus'] != 'public':
                continue
            # 
            video = {
                'video_name': res['snippet']['title'],
                'video_id': res['snippet']['resourceId']['videoId']
                
            }
            video_info.append(video)

        except Exception as e:
            print(f"Error processing comment at index {i}: {e}")
            print(f"Problematic item: {res}")

    return video_info

