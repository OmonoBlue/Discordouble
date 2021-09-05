import re 
import csv
import codecs
import pickle
import os 

from youtubesearchpython.__future__ import VideosSearch
import asyncio
import json
from requests_html import AsyncHTMLSession

# init session
asession = AsyncHTMLSession()


def get_youtube_links(text):
    yt_regex = r'((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?'
    
    links = re.findall(yt_regex, text)
    return links


async def get_video_title(url):
    
    request_url = "https://noembed.com/embed?url=" + url
    
    # download HTML code
    response = await asession.get(request_url)
    vid_info = json.loads(response.text)
    return vid_info["title"]
    
    
async def replace_youtube_links(text):
    
    links = get_youtube_links(text)
    
    for link in links:
        full_link = "".join(link)
        
        try:
            vTitle = await get_video_title(full_link)
            text = text.replace(full_link, "<|YOUTUBE: " + vTitle + " |>")
        except Exception as e:
            print("error replacing", full_link, "in messages: \n", text)
            print(e)
            text = text.replace(full_link, "")

    return text


async def replace_youtube_search(text):
    search_regex = r'(?<=<\|YOUTUBE: )(?:(?!<\|YOUTUBE: ). ?)*(?=\|>)'
    
    searches = re.findall(search_regex, text)
    
    for search in searches:
        
        videosSearch = VideosSearch(search, limit = 1)
        search_result = await videosSearch.next()
        print("Searched Youtube for: '%s'" % search)
        
        if len(search_result["result"]) > 0:
            link = "https://www.youtube.com/watch?v=" + search_result["result"][0]["id"]
            print("Result link: %s" % link)
            text = text.replace("<|YOUTUBE: " + search + "|>", link, 1)
        else:
            print("Could not find result!")
        
    return text
        

def parse_csv(file_name = "C-Eng - Central - general [671308707975397376].csv", out_name = "parsedMessages.txt", line_limit = -1, replace_YT = True, include_attachments = False):
    
    dataset = open(filename, "r", encoding='utf-8')
    output = open(outName, "w", encoding='utf-8')
    
    reader = csv.reader((x.replace('\0', '') for x in dataset), delimiter=",")
    line_count = 0
    last_author = ""
    
    print("Parsing CSV...")
    for row in reader:
        if line_count == 0:
            line_count = 1
            continue
        elif line_count == lineLimit:
            break
        
        line_count += 1
        
        author = row[1]
        text = row[3]
        attachment = row[4]
            
        if replaceYT:
            text = asyncio.get_event_loop().run_until_complete(replace_youtube_links(text))
        
        if text == "" and not includeAttachments:
            continue
            
        if last_author == "":
            output.write(author + ":\n" + text + (attachment if includeAttachments else "") + "\n")
        elif author == last_author:
            output.write(text + (attachment if includeAttachments else "") + "\n")
        else:
            output.write("\n" + author + ":\n" + text + (attachment if includeAttachments else "") + "\n")

        last_author = author  
        
    dataset.close()
    output.close()
    print("CSV Parsed Successfully. Total messages:", line_count)
    
    print("Dataset saved to", outName)

def load_set_from_file(filename):
    try:
        with open(filename,'rb') as f:
            return pickle.load(f)
    except:
        return None
