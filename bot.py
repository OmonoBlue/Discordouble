from typing import Dict
from aitextgen import aitextgen
import discord
from discord.ext import tasks, commands
import asyncio, random, string
import time
import re 
import data_parser as parser
import json
import os


# When previously sent message was sent
BOT_PREV_MESSAGE_TIME : float = 0
# If someone sends a message between auto_reply_min_wait and auto_reply_interval seconds after the bot's message, auto reply to the user's message
auto_reply_inverval : float = 40
auto_reply_min_wait : float = 10
auto_reply_chance : float = 0.3
# If someone sends a message, and it's been at least (auto_message_wait) seconds since the bot's last message, then the bot has (auto_message_chance) chance of replying to that message
auto_message_wait : float = 60* 10
# chance of auto replying to message
auto_message_chance : float = 0.2


def run_bot(config):
    
    genConfig = config["gen"]
    botConfig = config["bot"]
    
    if not (os.path.exists(os.path.join(os.getcwd(), genConfig["model_folder_name"]))):
        print("AI model folder \"%s\" does not exist! Did you forget to train?" % os.path.join(os.getcwd(), genConfig["model_folder_name"]))
        return
    
    INVITE_LINK = "https://discord.com/oauth2/authorize?client_id=%s&scope=bot+applications.commands" % botConfig["discord_app_id"]
    YOURNAME = botConfig["pretending_to_be"]
    YOURNAME_NOID = YOURNAME.split("#")[0]
    BOT_MENTION_ID = "<@!%s>" % botConfig["discord_app_id"]
    USERNAME_REGEX = r'^(\w+?#\d{4}:)'

    HISTORY_LIMIT = botConfig["context_history_limit"]
    
    GEN_TEMP = 0.9
    GEN_TOP_P = 0.9
    EMOTE_CODES = {}

    try:
        with open("emotes.json") as file:
            EMOTE_CODES = json.load(file)
    except:
        print("Error opening emote file")
    
    try:
        ai = aitextgen(model_folder=genConfig["model_folder_name"], to_gpu=genConfig["uses_gpu"])
    except Exception as e:
        print("An error has occured while loading the model into aitextgen!")
        print(e)
        return

    client = discord.Client()

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))
        print(f'Invite link: {INVITE_LINK}')
        activity = discord.Activity(name="as %s" % YOURNAME_NOID, type=discord.ActivityType.playing)
        await client.change_presence(status=discord.Status.online, activity=activity)

    @client.event
    async def on_message(message):
        global BOT_PREV_MESSAGE_TIME
        if client.is_ready:
            # Don't let bot reply to itself
            if message.author == client.user:
                return
            
            if client.user.mention in message.content.replace('<@!', '<@') or YOURNAME_NOID in message.content:
                # IF BOT IS MENTIONED, REPLY TO THE MESSAGE
                print("\n%s: " % time.ctime(time.time()))
                await send_reply_to_message(message)
            else:
                curr_time = time.time()
                time_since_last_bot_msg = curr_time - BOT_PREV_MESSAGE_TIME
                if time_since_last_bot_msg > auto_reply_min_wait:
                    if time_since_last_bot_msg <= auto_reply_inverval:
                        # CHANCE TO AUTO REPLY
                        if random.uniform(0, 1) <= auto_reply_chance:
                            print("\nAuto Replying at %s: " % time.ctime(time.time()))
                            await send_reply_to_message(message)

                    elif time_since_last_bot_msg > auto_message_wait:
                        # CHANCE TO AUTO MESSAGE
                        if random.uniform(0, 1) <= auto_message_chance:
                            print("\nAuto Messaging at %s: " % time.ctime(time.time()))
                            await send_reply_to_message(message)
    

    async def send_reply_to_message(message):
        """Generate response to message, and send the reply"""
        message_replies = await generate_reply(message)

        for i, msg in enumerate(message_replies):
            if i == (len(message_replies) -1):
                await message.channel.send(msg)
            else:
                async with message.channel.typing():
                    await message.channel.send(msg)
        global BOT_PREV_MESSAGE_TIME
        BOT_PREV_MESSAGE_TIME = time.time()


    async def generate_reply(message):
        msgHist = ""
        last_author = ""
        
        old = await message.channel.history(limit=HISTORY_LIMIT).flatten()
        old.reverse()
        
        for msg in old:
            if len(msg.mentions) > 0:
                for mention in msg.mentions:
                    msg.content.replace("<@!" + str(mention.id) + ">", "@" + mention.name)
                
            if last_author == msg.author.name:
                msgHist = msgHist + msg.content.replace(BOT_MENTION_ID, "@" + YOURNAME_NOID) + "\n"
            else:
                msgHist = msgHist + ("\n" if len(msgHist) > 0 else "") \
                        + msg.author.name + "#" + msg.author.discriminator + ":\n" \
                        + msg.content.replace(BOT_MENTION_ID, "@" + YOURNAME_NOID) + "\n"
                        
            last_author = msg.author.name
        
        msgHist = await parser.replace_youtube_links(msgHist)
            
        prompt = msgHist + "\n" + YOURNAME + ":\n"
        
        # Generate response 
        tic = time.perf_counter()
        results = ai.generate_one(
            prompt=prompt, 
            max_length=450, 
            temperature=genConfig["temperature"],
            top_k=genConfig["top_k"]
            )
        
        toc = time.perf_counter()
        print("Generated response in %0.4f seconds" % (toc-tic))
        
        final = results[len(prompt):].splitlines()
        
        ok = []
        for msg in final:
            if msg == "":
                break
            if botConfig["can_send_YT_links"]:
                msg = await parser.replace_youtube_search(msg)
            msg = replace_emotes(msg)
            ok.append(msg)
        return ok
    
    
    def replace_emotes(text):
        emoteRegex = r':(\w*?):'
        
        emotes = re.findall(emoteRegex, text)
        
        if len(emotes) > 0:
            emoteSet = set()
            for e in emotes:
                if not (e in emoteSet):
                    emoteSet.add(e)
            for e in emoteSet:
                #Check emote code dictionary first
                if e in EMOTE_CODES:
                    print("replacing", e, "with", EMOTE_CODES[e])
                    text = text.replace(":" + e + ":", EMOTE_CODES[e])
                else:
                    print("Can't find emote in dataset:", e)
                    #Search through all servers the bot is in
                    emoji_match = lambda v: v.name == e
                    
                    emoji = next(filter(emoji_match, client.emojis), None)
                    if emoji:
                        ID = emoji.id
                        
                        text = text.replace(":" + e + ":", ("<a:" if emoji.animated else "<:") + e + ":" + str(ID) + ">")
    
        return text
        
    client.run(botConfig["discord_token"])
    

def train_bot(config):
    traincfg = config["training"]
    ai = aitextgen(tf_gpt2=traincfg["GPT2_model_type"], to_gpu=traincfg["uses_gpu"], model_folder=traincfg["out_folder_name"])
    
    ai.train(traincfg["dataset_file_name"],
         line_by_line=False,
         from_cache=False,
         num_steps=traincfg["num_steps"],
         generate_every=traincfg["generate_every"],
         save_every=traincfg["save_every"],
         learning_rate=traincfg["learning_rate"],
         fp16=False,
         batch_size=traincfg["batch_size"], 
         )