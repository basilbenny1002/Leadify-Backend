import os
import pandas as pd
from scrapers.scraper_functions import get_follower_count, scrape_twitch_about, scrape_twitter_profile, extract_emails, scrape_youtube, get_live_streams, is_valid_email, get_subscriber_count, is_valid_text, get_twitch_game_id
from tqdm import tqdm
from scrapers.scraper_functions import scrape_twitter
from scrapers.scraper_functions import convert_to_percentage, get_twitch_details, format_time
import logging
import datetime
import time
from dotenv import load_dotenv
import threading
import queue
from supabase import create_client
import uuid
import requests
import os
from app.utils.superbase_functions import upload_csv 
from scrapers.scraper_functions import AnyValue, classify
from app.utils.superbase_functions import add_notification

active_scrapers = {}
data_template = {
    "Stage": 0, "Rate":0 , "ETA": format_time(0), "Streamers":0,
    "Completed": 0, "Percentage": 0, "Total_Streamers": 0, 
    "Done": False, "search_id": "", "download_url": "", "progress_data":[]
}
def update_progress(user_id, values: dict):
    if user_id not in active_scrapers:
        active_scrapers[user_id] = data_template.copy()
    active_scrapers[user_id].update(values)
    # print(f"Updated progress for {user_id}: {values}")

def remove_progress(user_id):
    if user_id in active_scrapers:
        del active_scrapers[user_id]
    

ANYT = AnyValue(choice=True)
ANYF = AnyValue(choice=False)


lock = threading.Lock()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


logging.basicConfig(level=logging.INFO, filename="scraper.log", filemode="a",
                    format="%(asctime)s - %(levelname)s - %(message)s")


def initial(user_id: str, streamers,game_id, min_followers: int, max_followers: int, min_viewer_count: int, choice_l: str):
    choice_language = choice_l
    category = game_id
   
    ANYT = AnyValue(choice=True)
    ANYF = AnyValue(choice=False)
    # Set up logging
    logging.basicConfig(level=logging.INFO, filename="scraper.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(message)s")


    load_dotenv()
    access_token = os.getenv("access_token") 
    client_id = os.getenv("client_id")  

    update_progress(user_id, values={
    "Stage": 1, "Rate": 0, "ETA": format_time(0), "Streamers": 0,
    "Completed": 0, "Percentage": 0, "Total_Streamers": 0, 
    "Done": False, "search_id": "", "download_url": ""
    })  
 
    streams = get_live_streams(game_id, client_id=client_id, access_token=access_token)  # making the api request to get the list of live streamers

    print(f"Found {len(streams)} streamers ")
    valid_streamers= 0
    
    with tqdm(total=len(streams)) as pbar:
        # global elapsed, remaining, rate
        update_progress(user_id, values={
        "Stage": 2, "Rate": 0, "ETA": format_time(0), "Streamers": 0,
        "Completed": 0, "Percentage": 0, "Total_Streamers": len(streams), 
        "Done": False, "search_id": "", "download_url": ""
        }) 
        current_process = 2
        print(f"finding streamers with more than {min_followers} followers, {max_followers} max followers, {min_viewer_count} min viewer count, language {choice_language}, category {category}")
        for i in range(len(streams)):
            """
            Iterating over the API response and appending details of streamers with more than the specified number of followers to a list
            """
            if valid_streamers > 10:
                break
            follower = get_follower_count(client_id, access_token, user_id=streams[i]['user_id'])  # function to get follower count
            if follower > min_followers and streams[i]['user_name'] and follower < int(max_followers) and classify(choice_l=choice_language, min_viewer_c=min_viewer_count, streams=streams[i]):
                streamer_info = {
                    "user_name": streams[i]['user_name'],
                    "user_id": streams[i]['user_id'],
                    "viewer_count": streams[i]['viewer_count'],
                    "language": streams[i]['language'],
                    'game_name': streams[i]['game_name'],
                    'followers': follower
                }
                streamers.append(streamer_info)
                valid_streamers+=1
            elapsed = pbar.format_dict["elapsed"]
            current = pbar.n
            total = pbar.total
            stage_2_rate = 0
            stage_2_remaining = 0
            if current > 0 and total:
                stage_2_rate =  elapsed / current
                stage_2_remaining = stage_2_rate * (total - current)
                pbar.set_postfix({
                    "Elapsed": f"{elapsed:.1f}s",
                    "Remaining": f"{stage_2_remaining:.1f}s"
                })
            percentage = convert_to_percentage(i, len(streams))
            update_progress(user_id, values={
        "Stage": 2, "Rate": stage_2_rate, "ETA": format_time(int(stage_2_remaining)), "Streamers": valid_streamers,
        "Completed": 0, "Percentage": percentage, 
            }) 

            pbar.update(1)


def process_streamer(streamer, index, user_id, streamers, results_queue, session):
    
    start_time = time.time()
    if not is_valid_text(streamer['user_name']):
        logging.warning(f"Invalid username: {streamer['user_name']}")
        return

    yt_links = set()
    dc_links = []
    twitter_links = []
    mails_found = set()
    instagram_links = []
    facebook_links = []
    linkedin_links = []
    tiktok_links = []

    try:
        result = {
            'username': streamer['user_name'],
            'channel url': f"https://www.twitch.tv/{streamer['user_name']}",
            'followers': streamer['followers'],
            'viewer_count': streamer['viewer_count'],
            'language': streamer['language'],
            'game_name': streamer['game_name'],
            'discord': "",
            'youtube': "",
            'subscriber_count': 0,
            'gmail': "",
            "instagram": "",
            "twitter": "",
            "facebook":"",
            "tiktok": "",
            "linkedin": ""
        }
        #results_queue.put(result)
    except Exception as e:
        logging.error(f"Error processing streamer {streamer['user_name']}: {str(e)}")


    # Scrape Twitch about section with error handling
    try:
        response = get_twitch_details(streamer['user_name'], streamer['user_id'], session)
        if not isinstance(response, dict):
            logging.error(f"Invalid response type for {streamer['user_name']}: {type(response)}")
            with lock:
                end_time = time.time()
                update_progress(user_id=user_id, values={"Completed": active_scrapers[user_id]["Completed"] + 1})
                update_progress(user_id=user_id, values={"Percentage": convert_to_percentage(active_scrapers[user_id]["Completed"], len(streamers))})
                active_scrapers[user_id]["progress_data"].append(end_time - start_time)
                active_scrapers[user_id]["Rate"] = sum(active_scrapers[user_id]["progress_data"]) / len(active_scrapers[user_id]["progress_data"])
                active_scrapers[user_id]["ETA"] = format_time((len(streamers) - active_scrapers[user_id]["Completed"]) * active_scrapers[user_id]["Rate"])
            
            results_queue.put(result)
            return
        socials = response.get('links', [])
        mail = response.get('emails', [])
        if mail:
            mails_found.update(mail)
    except Exception as e:
        logging.error(f"Error scraping Twitch about for {streamer['user_name']}: {str(e)}",)
        print(f"Error scraping Twitch about for {streamer['user_name']}: {str(e)}", flush=True)
        with lock:
            end_time = time.time()
            update_progress(user_id=user_id, values={"Completed": active_scrapers[user_id]["Completed"] + 1})
            update_progress(user_id=user_id, values={"Percentage": convert_to_percentage(active_scrapers[user_id]["Completed"], len(streamers))})
            active_scrapers[user_id]["progress_data"].append(end_time - start_time)
            active_scrapers[user_id]["Rate"] = sum(active_scrapers[user_id]["progress_data"]) / len(active_scrapers[user_id]["progress_data"])
            active_scrapers[user_id]["ETA"] = format_time((len(streamers) - active_scrapers[user_id]["Completed"]) * active_scrapers[user_id]["Rate"])
        
        results_queue.put(result)
        return

    if not socials:
        result['gmail'] = ", ".join(str(element).lower() for element in mails_found) if mails_found else ""
        with lock:
            end_time = time.time()
            update_progress(user_id=user_id, values={"Completed": active_scrapers[user_id]["Completed"] + 1})
            update_progress(user_id=user_id, values={"Percentage": convert_to_percentage(active_scrapers[user_id]["Completed"], len(streamers))})
            active_scrapers[user_id]["progress_data"].append(end_time - start_time)
            active_scrapers[user_id]["Rate"] = sum(active_scrapers[user_id]["progress_data"]) / len(active_scrapers[user_id]["progress_data"])
            active_scrapers[user_id]["ETA"] = format_time((len(streamers) - active_scrapers[user_id]["Completed"]) * active_scrapers[user_id]["Rate"])
        results_queue.put(result)
        return

    # Process social links
    for social_links in socials:
        if "youtube" in str(social_links).lower():
            yt_links.add(social_links)
        if "tiktok" in str(social_links).lower():
            tiktok_links.append(social_links)
        if "linkedin" in str(social_links).lower():
            linkedin_links.append(social_links)
        if "facebook" in str(social_links).lower():
            facebook_links.append(social_links)
        if "discord.gg" in str(social_links).lower():
            dc_links.append(social_links)
        if "x.com" in str(social_links).lower() or "twitter.com" in str(social_links).lower():
            twitter_links.append(social_links)
        if "instagram" in str(social_links).lower():
            instagram_links.append(social_links)



    if tiktok_links:
        result['tiktok'] = ", ".join(str(link) for link in tiktok_links)

    if linkedin_links:
        result['linkedin'] = ", ".join(str(link) for link in linkedin_links)

    if facebook_links:
        result['facebook'] = ", ".join(str(link) for link in facebook_links)

    if twitter_links:
        result['twitter'] = ", ".join(str(link) for link in twitter_links)
    
    if instagram_links:
        result['instagram'] = ", ".join(str(link) for link in instagram_links)


    # Process YouTube info
    if not yt_links:
        result.update({
            'youtube': "",
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
    result['discord'] = dc_links[0] if dc_links else ""

    # Process Twitter and additional email scraping
    if twitter_links:
        try:
            twitter_response = scrape_twitter(twitter_links[0])
            if twitter_response:
                mail = twitter_response
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
        result['gmail'] = ""
    else:
        valid_mails = [i for i in set(mails_found) if is_valid_email(i)]
        result['gmail'] = ",".join(valid_mails) if valid_mails else ""
    end_time = time.time()
    # Once processing is done]
    with lock:
        update_progress(user_id=user_id, values={"Completed": active_scrapers[user_id]["Completed"] + 1})
        update_progress(user_id=user_id, values={"Percentage": convert_to_percentage(active_scrapers[user_id]["Completed"], len(streamers))})
        active_scrapers[user_id]["progress_data"].append(end_time - start_time)
        active_scrapers[user_id]["Rate"] = sum(active_scrapers[user_id]["progress_data"]) / len(active_scrapers[user_id]["progress_data"])
        active_scrapers[user_id]["ETA"] = format_time((len(streamers) - active_scrapers[user_id]["Completed"]) * active_scrapers[user_id]["Rate"])
    results_queue.put(result)

    #TODO Uncomment the following if doing multi-threading
    # with lock:
    #     # completed += 1
    #     update_progress(user_id, values={ 
    #     "Completed": active_scrapers[user_id]["Completed"] + 1, "Percentage": stage_3_percentage
    #     }) 
    # results_queue.put(result)


# Main processing with threading
def start(min_f: int, max_f: int, choice_l: str, min_viewer_c: int, c: str, user_id: str):
    """
    Main function to start the scraping process.
    
    """
    session = requests.Session()
    r = session.get("https://www.twitch.tv")
    lock = threading.Lock()

    streamers = []
    initial(user_id=user_id, streamers=streamers, min_followers=min_f, max_followers=max_f, choice_l=choice_l, min_viewer_count=min_viewer_c, game_id=c)  # Initialize the variables and get the list of streamers
    
    update_progress(user_id, values={
    "Stage": 3, "Rate": 0, "ETA": format_time(0), 
    "Completed": 0, "Percentage": 0})

    threads = []
    all_threads = []
    results_queue = queue.Queue()

    # start_time = time.time()
    print(f"Streamers: {streamers}")
    print(f"Number of streamers: {len(streamers)}")
    for i in tqdm(range(len(streamers)), desc="Getting more info"): 
        try:
            thread = threading.Thread(target=process_streamer, args=(streamers[i], i, user_id, streamers, results_queue, session))
            thread.start()
            threads.append(thread)
            all_threads.append(thread)
        except Exception as e:
            print(f"Error occurred{e}:", flush=True)
        if len(threads) > 0:  #number of threads
            for t in threads:
                t.join()
            threads = []

    for t in all_threads:
        t.join()

    with lock:
        if active_scrapers[user_id]["Completed"] != len(streamers):
            active_scrapers[user_id]["Completed"] = len(streamers)  # Force synchronization
            percentage = convert_to_percentage(active_scrapers[user_id]["Completed"], len(streamers))
            update_progress(user_id, values={
            "Completed": len(streamers), "Percentage": 100
            })

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
        "instagram": [],
        "twitter": [],
        "facebook":[],
        "tiktok": [],
        "linkedin": [] 
    }
    update_progress(user_id, values={
    "Stage": 4, "Rate": 0, "ETA": format_time(0)})

    while not results_queue.empty():
        result = results_queue.get()
        for key in datas:
            datas[key].append(result[key])


    search_id_uuid = str(uuid.uuid4()) 
    file_name = f"{user_id}_{search_id_uuid}.csv"
    df = pd.DataFrame(datas)
    df.to_csv(path_or_buf=file_name, index=False)
    logging.info(f"Data saved to test.csv")
    if type(choice_l) == AnyValue:
        choice_l = ""
    if type(min_f) == AnyValue:
        min_f = 0
    if type(max_f) == AnyValue:
        max_f = 100000000000000
    if type(min_viewer_c) == AnyValue:
        min_viewer_c = 0

    filters = {
        "min_followers": min_f,
        "max_followers": max_f,
        "language": choice_l,
        "min_viewers": min_viewer_c,
        "category": c
    }
    upload_csv(search_id_uuid, user_id, filters, file_name, active_scrapers[user_id]["Total_Streamers"], active_scrapers[user_id]["Streamers"])

    add_notification(user_id, "Search Complete",f"Found {active_scrapers[user_id]['Streamers']} streamers")
    update_progress(user_id, values={
    "Stage": 5,"Done": True, "search_id": search_id_uuid,
      "download_url": f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/results/{file_name}"
    })  
    time.sleep(10)
    os.remove(file_name)
    remove_progress(user_id)
