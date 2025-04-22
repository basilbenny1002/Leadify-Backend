import asyncio
import json
import os
import pandas as pd
from Scrapers.functions import get_follower_count, scrape_twitch_about, scrape_twitter_profile, extract_emails, scrape_youtube, get_live_streams, is_valid_email, get_subscriber_count, is_valid_text, get_twitch_game_id
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from Scrapers.functions import convert_to_percentage
import logging
import datetime
import time
from dotenv import load_dotenv
import threading
import queue
from supabase import create_client
import uuid

import os
from Scrapers.functions import AnyValue, classify
ANYT = AnyValue(choice=True)
ANYF = AnyValue(choice=False)
choice_language = ANYT
min_followers = 0
max_followers = 100000000000000
min_viewer_count = 0
category = None
current_process = 0
completed = 0
done = False
search_id = ""
download_url = ""

elapsed, remaining, rate, valid_streamers = 0, 0, 0, 0
total_streamers = 0
percentage = 0

lock = threading.Lock()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


# Set up logging
logging.basicConfig(level=logging.INFO, filename="scraper.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
load_dotenv()
streams = None
access_token = os.getenv("access_token")  # TODO: paste your access token here
client_id = os.getenv("client_id")  # TODO: paste your client_id here
game_id = ""  # TODO: paste the game id you want to filter from
output_file_name = "CSGO streamers(17-04-2025)3.csv"  # TODO: file name of the output, make sure to include .csv
# Initialising empty lists to store values
datas = {}

username = []
followers = []
viewer_count = []
language = []
game_name = []
discord = []
youtube = []
gmail = []
streamers = []
subscriber_count = []
def initial():
    global streams, elapsed, rate, remaining, valid_streamers, all_streamers, results_queue, completed, streamers
    global min_followers, max_followers, choice_language, min_viewer_count, category, current_process,percentage, total_streamers
    global access_token, client_id, min_followers, game_id, output_file_name, username, followers, viewer_count, language, game_name, discord, youtube, gmail, subscriber_count
    global search_id, download_url
    ANYT = AnyValue(choice=True)
    ANYF = AnyValue(choice=False)
    


    # Set up logging
    logging.basicConfig(level=logging.INFO, filename="scraper.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(message)s")

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    load_dotenv()
    streams = None
    access_token = os.getenv("access_token")  # TODO: paste your access token here
    client_id = os.getenv("client_id")  # TODO: paste your client_id here
    output_file_name = "CSGO streamers(17-04-2025)3.csv"  # TODO: file name of the output, make sure to include .csv

    
    current_process = 1
    streams = get_live_streams(game_id, client_id=client_id, access_token=access_token)  # making the api request to get the list of live streamers



    # previous_data = pd.read_csv(f"All streamers list.csv")
    #
    # previous_streamers = previous_data['Name'].tolist()
    previous_streamers = []
    all_streamers = {"Name": previous_streamers}
      # TODO uncomment this part to make sure previous streamers thingy is working properly
    total_streamers = len(streams)
    print(f"Found {len(streams)} streamers ")
    good_streamer_count = 0
    with tqdm(total=len(streams)) as pbar:
        # global elapsed, remaining, rate
        current_process = 2
        print(f"finding streamers with more than {min_followers} followers, {max_followers} max followers, {min_viewer_count} min viewer count, language {choice_language}, category {category}")
        for i in range(len(streams)):
            """
            Iterating over the API response and appending details of streamers with more than the specified number of followers to a list
            """
            if valid_streamers > 19:
                break
            follower = get_follower_count(client_id, access_token, user_id=streams[i]['user_id'])  # function to get follower count
            if follower > min_followers and streams[i]['user_name'] not in previous_streamers and follower < int(max_followers) and classify(choice_l=choice_language, min_viewer_c=min_viewer_count, streams=streams[i]):
                streamer_info = {
                    "user_name": streams[i]['user_name'],
                    "viewer_count": streams[i]['viewer_count'],
                    "language": streams[i]['language'],
                    'game_name': streams[i]['game_name'],
                    'followers': follower
                }
                streamers.append(streamer_info)
                valid_streamers+=1
                previous_streamers.append(streams[i]['user_name'])
            elapsed = pbar.format_dict["elapsed"]
            current = pbar.n
            total = pbar.total

            if current > 0 and total:
                rate = elapsed / current
                remaining = rate * (total - current)
                pbar.set_postfix({
                    "Elapsed": f"{elapsed:.1f}s",
                    "Remaining": f"{remaining:.1f}s"
                })
            percentage = convert_to_percentage(i, len(streams))

            pbar.update(1)
    complete_streamer_list = {"Name": previous_streamers}
    # print(previous_streamers)
    # valid_streamers = len(streamers)
    logging.info("Found %d unique streamers", len(streamers))
    logging.info("Done collecting streamers with more than %d followers", min_followers)
    logging.info("Collecting other info")
    results_queue = queue.Queue()

def process_streamer(streamer, index):
    global results_queue, completed, current_process, percentage
    current_process = 3
    if not is_valid_text(streamer['user_name']):
        logging.warning(f"Invalid username: {streamer['user_name']}")
        return

    # Initialize data containers
    yt_links = set()
    dc_links = []
    twitter_links = []
    mails_found = set()
    percentage = convert_to_percentage(completed, len(streamers))

    # Collect basic info
    try:
        result = {
            'username': streamer['user_name'],
            'followers': streamer['followers'],
            'viewer_count': streamer['viewer_count'],
            'language': streamer['language'],
            'game_name': streamer['game_name'],
            'discord': "Couldn't find discord",
            'youtube': "Couldn't find youtube",
            'subscriber_count': 0,
            'gmail': "Couldn't find a valid mail",
            'emailed': "No",
            'second_f': "Null",
            'third_follow_up': "Null",
            'initial_contact_date': "Null",
            'second_contact_date': "Null",
            'third_contact_date': "Null",
            'replied': "Null",
            'classify': "Null",
            'interested': "Null"
        }
        #results_queue.put(result)
    except Exception as e:
        logging.error(f"Error processing streamer {streamer['user_name']}: {str(e)}")
    


    # Scrape Twitch about section with error handling
    try:
        response = scrape_twitch_about(f"https://www.twitch.tv/{streamer['user_name']}/about")
        if not isinstance(response, dict):
            logging.error(f"Invalid response type for {streamer['user_name']}: {type(response)}")
            results_queue.put(result)
            return
        socials = response.get('links', [])
        mail = response.get('emails', [])
        mails_found.update(mail)
    except Exception as e:
        logging.error(f"Error scraping Twitch about for {streamer['user_name']}: {str(e)}")
        results_queue.put(result)
        return

    if not socials:
        result['gmail'] = ", ".join(str(element).lower() for element in mails_found) if mails_found else "Couldn't find a valid mail"
        results_queue.put(result)
        return

    # Process social links
    for social_links in socials:
        if "youtube" in str(social_links).lower():
            yt_links.add(social_links)
        if "discord" in str(social_links).lower():
            dc_links.append(social_links)
        if "x" in str(social_links).lower() or "twitter" in str(social_links).lower():
            twitter_links.append(social_links)

    # Process YouTube info
    if not yt_links:
        result.update({
            'youtube': "Couldn't find youtube",
            'subscriber_count': 0
        })
    else:
        result['youtube'] = ", ".join(str(link) for link in yt_links)
        try:
            subs = get_subscriber_count(list(yt_links)[0])
            result['subscriber_count'] = subs if subs else 0
        except Exception as e:
            logging.error(f"Error getting YouTube subscriber count for {streamer['user_name']}: {str(e)}")
            result['subscriber_count'] = 0

    # Process Discord info
    result['discord'] = dc_links[0] if dc_links else "Couldn't find discord"

    # Process Twitter and additional email scraping
    if twitter_links:
        try:
            twitter_response = scrape_twitter_profile(twitter_links[0])
            if isinstance(twitter_response, dict) and 'bio' in twitter_response:
                bio = twitter_response['bio']
                mail = extract_emails(bio)
                if mail:
                    mails_found.update(mail)
            else:
                logging.warning(f"Invalid Twitter response for {streamer['user_name']}: {twitter_response}")
        except Exception as e:
            logging.error(f"Error scraping Twitter for {streamer['user_name']}: {str(e)}")

    if yt_links:
        try:
            youtube_mails = scrape_youtube(yt_links)
            if youtube_mails:
                mails_found.update(youtube_mails)
        except Exception as e:
            logging.error(f"Error scraping YouTube for {streamer['user_name']}: {str(e)}")

    # Process email validation
    if not mails_found:
        result['gmail'] = "Couldn't find a valid gmail"
    else:
        valid_mails = [i for i in set(mails_found) if is_valid_email(i)]
        result['gmail'] = ",".join(valid_mails) if valid_mails else "Couldn't find a valid mail"
        
    # Once processing is done
    with lock:
        completed += 1
        percentage = convert_to_percentage(completed, len(streamers))
    results_queue.put(result)

# Main processing with threading
def start(min_f: int, max_f: int, choice_l: str, min_viewer_c: int, c: str, user_id: str):
    """
    Main function to start the scraping process.
    """
    global min_followers, max_followers, choice_language, min_viewer_count, category, completed, game_id, datas, results_queue, current_process,streamers, rate, elapsed, remaining, valid_streamers, total_streamers, percentage, done, search_id, download_url
    completed = 0
    percentage = 0
    min_followers = min_f
    max_followers = max_f
    choice_language = choice_l
    min_viewer_count = min_viewer_c
    category = c
    game_id = c
    initial()

    current_process = 3

    threads = []
    all_threads = []
    start_time = time.time()
    print(f"Streamers: {streamers}")
    print(f"Number of streamers: {len(streamers)}")
    for i in tqdm(range(len(streamers)), desc="Getting more info"): 
        try:
            thread = threading.Thread(target=process_streamer, args=(streamers[i], i))
            thread.start()
            threads.append(thread)
            all_threads.append(thread)
        except Exception as e:
            print(f"Error occurred{e}:", flush=True)
        if len(threads) >= 4:  #number of threads
            for t in threads:
                t.join()
            threads = []
        elapsed = time.time() - start_time
        processed = i + 1
        avg_time = elapsed / processed
        rate = avg_time
        remaining = avg_time * (len(streamers) - processed)

    for t in all_threads:
        t.join()

    with lock:
        if completed != len(streamers):
            completed = len(streamers)  # Force synchronization
            percentage = convert_to_percentage(completed, len(streamers))

    datas = {
        'username': [],
        'followers': [],
        'viewer_count': [],
        'language': [],
        'game_name': [],
        'discord': [],
        'youtube': [],
        'gmail': [],
        'subscriber_count': [],
        'emailed': [],
        'second_f': [],
        'third_follow_up': [],
        'initial_contact_date': [],
        'second_contact_date': [],
        'third_contact_date': [],
        'replied': [],
        'classify': [],
        'interested': []
    }
    current_process = 4

    while not results_queue.empty():
        result = results_queue.get()
        for key in datas:
            datas[key].append(result[key])

    # Save
    df = pd.DataFrame(all_streamers)
    df.to_csv("All streamers list.csv")
    df = pd.DataFrame(datas)
    df.to_csv(path_or_buf=output_file_name, index=False)
    print(f"Processed {len(datas['username'])} streamers")

   



    # Save data to CSV
    current_process = 4
    df = pd.DataFrame(datas)
    df.to_csv(path_or_buf=output_file_name, index=False)
    logging.info(f"Data saved to {output_file_name}")

    file_name = f"{user_id}/{str(uuid.uuid4())}.csv"  # you must pass user_id to this function

    with open(output_file_name, "rb") as f:
        res = supabase.storage.from_("results").upload(file_name, f)
        print(res)
    if not res.path:
        raise Exception(f"CSV upload failed: {res}")
    
    # Now insert metadata into the table
    search_id_uuid = str(uuid.uuid4())  # Generate a unique search ID
    filters = {
        "min_followers": min_f,
        "max_followers": max_f,
        "language": choice_l,
        "min_viewers": min_viewer_c,
        "category": c
    }
    print(type(min_f), min_f)
    print(type(max_f), max_f)
    print(type(choice_l), choice_l)
    print(type(min_viewer_c), min_viewer_c)
    print(type(c), c)

    filters_json = json.dumps(filters)
    
    res =  supabase.table("search_results").insert({
    "user_id": user_id,
    "search_id": search_id_uuid,
    "filters": filters_json,
    "valid_streamers": len(datas["username"]),
    "total_streamers": len(streamers),
    "file_path": file_name
    }).execute()

    print(res)
    
    search_id = search_id_uuid
    download_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/results/{file_name}"


    done = True
#
# if __name__ == "__main__":
#     start()