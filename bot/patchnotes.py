"""
patchnotes.py

Handles patch note scraping from Riot's official Valorant News website.
"""

import requests
import os
from bs4 import BeautifulSoup
import discord
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
LAST_PATCHNOTE_FILE = str(os.getenv("LAST_PATCHNOTE_FILE"))

#custom headers to emulate an actual user/browser
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/', 
        'Connection': 'keep-alive'
    }

"""
Searches the News website for any articles that have the label "Patch Notes."
Compares against the already posted patch notes, formats the retrieved data, and returns a Discord Embed object for the new patch notes. 
"""
def fetch_latest_patchnotes():
    try:
        url = "https://playvalorant.com/en-us/news/"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        #main HTML data to be used later
        matches = soup.select('a[aria-label*="Patch Notes"]')

        #literally just to have the article image as a thumbnail; it's loaded with JS so more complex
        scripts = soup.find_all("script")
        target_script = None
        for index, script in enumerate(scripts):
            script_string = str(script.string or script.text or "")
            if "VALORANT Patch Notes" in script_string and '"media":{' in script_string:
                target_script = script_string
                break
        start = target_script.index("VALORANT Patch Notes")
        target_script = target_script[start-10:] #script starts 10 chars before the title always
        end = target_script.index("publishDate") 
        target_script = target_script[:end+41] #script ends 41 chars after the publishDate always
        data = json.loads(target_script)
        image_link = data["media"]["url"]

        #could get data from script entirely. e.g.:
        #print(data["title"])
        #print(data["publishedAt"])
        #print(data["media"]["url"])
        #print(data["description"]["body"])
        #print(data["category"]["title"])
    except Exception as e:
        print(e)
        return None
    try:
        pieces = matches[0].get_text(separator="\n").split("\n")
        title = pieces[2].strip()
        link = "https://playvalorant.com" + matches[0]['href']
        dateObject = datetime.strptime(pieces[1], "%Y-%m-%dT%H:%M:%S.%fZ")
        date = f"{dateObject.month}/{dateObject.day}/{dateObject.year}"

        if link == load_last_patchnote_url():
            return None
        
        description = "### " + date + "\n" + " ".join(pieces[3:])
        image_url = image_link
        save_last_patchnote_url(link)
        return get_patchnote_embed(title, link, description, image_url)
    except:
        #if anything goes wrong with the embed build, simply return nothing
        return None

"""
Creates a Discord Embed object with custom formatting specific to patch note data.
"""    
def get_patchnote_embed(title, link, description, image_url):
    embed = discord.Embed(title=title, url=link, description=description, color=discord.Color.green()).set_thumbnail(url=image_url)
    return embed

"""
Loads most recent patch note URL from the JSON file. If file does not exist, creates it.
"""
def load_last_patchnote_url():
    try:
        if not os.path.exists(LAST_PATCHNOTE_FILE):
            with open(LAST_PATCHNOTE_FILE, "x") as f:
                f.write('{"url": ""}')
        with open(LAST_PATCHNOTE_FILE, "r") as f:
            return json.load(f).get("url")
    except Exception as e:
        print(e)
        return None
   
"""
Saves new patch note URL to the JSON file. Overwrites existing one.
""" 
def save_last_patchnote_url(url):
    try:
        with open(LAST_PATCHNOTE_FILE, "w") as f:
            json.dump({"url": url}, f)
    except Exception as e:
        print(e)