from aitextgen import aitextgen
import discord
import asyncio, random, string
import time
import re 
import data_parser as parser
import json
import os


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
        print("Invite link: $s", INVITE_LINK)
        activity = discord.Activity(name="as %s" % YOURNAME_NOID, type=discord.ActivityType.playing)
        await client.change_presence(status=discord.Status.online, activity=activity)

    @client.event
    async def on_message(message):
        if client.user.mention in message.content.replace('<@!', '<@'):
            if message.author == client.user:
                return
            else:
                if client.is_ready:
                    print("\n%s: " % time.ctime(time.time()))
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
                    
                    # print("RESULTS:[\n", results, "]\n")
                    # print("FINAL:[\n", final, "]\n")
                    
                    for i, msg in enumerate(ok):
                        if i == (len(ok) -1):
                            await message.channel.send(msg)
                        else:
                            async with message.channel.typing():
                                await message.channel.send(msg)   
                    
                    
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