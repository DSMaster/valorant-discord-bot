"""
redditmatches.py

Handles post match data and thread retrieval from the r/ValorantCompetitive subreddit using PRAW and the Reddit API.
"""

import praw
from dotenv import load_dotenv
import os
import json
import discord

load_dotenv()

POSTED_THREADS_FILE = os.getenv("POSTED_THREADS_FILE")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

#include/exclude certain threads
included = ["Americas", "Masters", "Champions"]
excluded = ["EMEA", "Pacific", "China"]

#initialize PRAW for use with Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    check_for_async=False #removes annoying debug messages
)

"""
Searches the r/ValorantCompetitive subreddit for the latest 10 threads that match the flair "Post-Match Thread."
Compares against the already posted thread IDs, formats the retrieved data, and returns Discord Embed objects for all new threads. 
"""
def fetch_latest_postmatches():
    posted_ids = load_posted_ids()

    output = []

    subreddit = reddit.subreddit("ValorantCompetitive")

    for submission in subreddit.search('flair:"Post-Match Thread"', sort='new', limit=10): #pretty sure it automatically sorts by new but you know
        if submission.id in posted_ids: #if already posted, move to next thread in the 10 pulled
            continue
        
        construct = {}
        lines = submission.selftext.split("\n")
        endingIndex = lines.index("---") #relevant data ends at the line that has "---"

        construct.update({"url": submission.url})
        construct.update({"teams": submission.title.split(" / ")[0]})
        construct.update({"event": submission.title.split(" / ")[1]})
        construct.update({"result": construct['teams'].split(" vs ")[0] + lines[0].split(")")[1][:5] + construct['teams'].split(" vs ")[1]}) #teamname1 + score + teamname2
        construct.update({"vlr": lines[2].split("](")[1][:-1]}) #"[VLR](link)" so pulls "link)" and then takes just "link"
        construct.update({"maps": [m.replace("**", "") for m in lines[7:endingIndex] if m.strip()]}) #map results start on line 7 in the Reddit post

        #only pass events that are in included and not in excluded
        included_flag = False
        excluded_flag = False
        for i in (construct["event"].split(" ")):
            if i in excluded:
                excluded_flag = True
                break
            if i in included:
                included_flag = True
                continue
        if (not included_flag or excluded_flag):
            continue

        comment_summary = get_top_comments(submission)
        construct.update({"comments": comment_summary})

        posted_ids.update({submission.id: construct}) #really only need to store ids, but info could be useful later

        output.append(create_embed(construct))
        
    save_posted_ids(posted_ids)

    return output

"""
Retrieves top 3 comments from a thread and formats each for display in the Discord Embed object. Returns a String of the joined and formatted comments or no comments.
"""
def get_top_comments(submission, max_comments=3):
    submission.comments.replace_more(limit=0) #removes ALL "load more comments" and "continue this thread" links leaving only top-level comments
    top_comments = submission.comments[:max_comments]

    top_list = []
    for comment in top_comments:
        body = comment.body.strip()

        #formatting for the embed: simply appends new lines to existing text.
        body = body.replace("\n\n", " ")

        #formatting: removes all links in the comment, including markdown ones (e.g. [Display](URL))
        #should and will swap to regex eventually
        start_index = body.find("https://")
        if (start_index == 0): pass
        elif (body[start_index-1] == "("): start_index = start_index-1
        while(start_index != -1):
            paren_index = body[start_index:].find(")") #link ends w/ paren
            space_index = body[start_index:].find(" ") #link ends w/ space
            fallback_index = len(body[start_index:]) #link ends w/ comment
            end_index = start_index + min([i for i in [paren_index, space_index, fallback_index] if i != -1])

            body = body[:start_index]+body[end_index+1:]

            start_index = body.find("https://")
            if (start_index == 0 or start_index == -1): pass
            elif (body[start_index-1] == "("): start_index = start_index-1
        
        #formatting: only allow 147 chars of the comment before cutoff
        if len(body) > 150:
            body = body[:147] + "..."
        
        #formatting: start comment with bullet point
        top_list.append(f"• {body}")

    return "\n\n".join(top_list) if top_list else "No top comments found."

"""
Creates a Discord Embed object with custom formatting specific to post match data.
"""
def create_embed(thread):
    embed = discord.Embed(
        title=thread["event"],
        url=thread["vlr"],
        description="## " + thread["result"] + "\n\n" + "\n".join(thread["maps"]) + "\n\n----------\n### Top Comments\n"+thread["comments"].encode('utf-16', 'surrogatepass').decode('utf-16')+"\n\n[Reddit Link]("+str({thread["url"]})[2:-2]+")",
        color=discord.Color.orange()
    )
    return embed

"""
Loads 10 most recent thread IDs from the JSON file. If file does not exist, creates it.
"""
def load_posted_ids():
    try:
        if not os.path.exists(POSTED_THREADS_FILE):
            with open(POSTED_THREADS_FILE, "x") as f:
                f.write("{}")      
        with open(POSTED_THREADS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(e)
        return []

"""
Saves all thread IDs (including new ones) to the JSON file. Only keeps a max of 10 most recent threads. Deletes oldest ones to make room for new ones.
"""
def save_posted_ids(posted_ids):
    try:
        while (len(posted_ids) > 10):
            key = list(posted_ids.keys())[0]
            posted_ids.pop(key)
        with open(POSTED_THREADS_FILE, "w") as f:
            json.dump(posted_ids, f)
    except Exception as e:
        print(e)