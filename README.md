# Discordouble
GPT-2 AI Discord Doppleganger bot. Uses [AiTextGen](https://github.com/minimaxir/aitextgen) to train a GPT-2 Model on your Discord server's message history, then uses that training data to join discord conversations and become the ultimate doppelganger.
Inspired by [yourAI](https://github.com/M4cs/yourAI)

## Requirements
Please make sure you download and install [Python](https://www.python.org/downloads/) on your computer. I recommend Python 3.7, but later version should work as well. 

If you want to use your Nvidia GPU to train/run the bot, you will need to install [Cuda Toolkit 11.1](https://developer.nvidia.com/cuda-11.1.0-download-archive)
(be sure to update your graphics drivers as well!)

## Initial Setup

1. Download this repository to your computer, extract it to a place that's easily accessible. 
2. Navigate to the folder where you downloaded the bot, then open a PowerShell window in the folder as administrator. (You can do this by pressing **Alt** + **F** + **S** + **A** in that order.
3. Enter these lines into PowerShell to install python dependencies: 
	 `pip install --upgrade pip`
	 `pip install -r requirements.txt`
4. Once everything installs, enter `python main.py` into PowerShell to run the code! (You can also run the code by double-clicking *RUN_CODE.bat* included in the folder). After a few seconds, you should get a message asking you to fill the 'config.json' file that the code just created. We will do that later.
5. You're all set for now! Press Enter to exit the terminal, then move on to the next section to learn how to set up a discord bot account.

## Setting up a Discord Bot Account
Before you can run the discord bot, you will need to create a Discord bot account. You can do that by following the "*Creating a Bot Account*" section of [this guide!](https://discordpy.readthedocs.io/en/stable/discord.html)
(I highly recommend not setting your bot to be public, as setting it to public will let others invite the bot to as many servers as they want, which might be a privacy concern depending on how you train the chatbot, but do as you will)

Once you have the bot setup, take note of the bot's application ID, as well as the bot's token. We will need these later.(NEVER share the token with anyone, doing so might make you lose control of the bot)

## Editing config.json
Now that you have your bot's token and application id, open the config.json file that was created earlier (You can use Notepad for this)
1. On the line that looks like `"discord_token": "DISCORD_BOT_TOKEN_HERE",`, replace the `"DISCORD_BOT_TOKEN_HERE",` with the discord bot token that you got from the previous step. (keep the quotation marks!)
2. Do the same for `"discord_app_id": "DISCORD_BOT_APPLICATION_ID_HERE"`, but with your bot's application ID.
3. Next, replace `"pretending_to_be": "YOUR_DISCORD_USERNAME#1234",` with the discord username that the bot will imitate! (use full username, and include the # tag number as well!)

The start of your config.json should look something like this:
`  "bot": {`
	`    "discord_token": "ODU1FSER8jAwMDA5MzAzrdr9.YMzvBA.bov8Hw9KAe0GqBi97SAF23DdminJ",`
`    "discord_app_id": "842324200109452192",`
`    "pretending_to_be": "BillyBobson#1337",`
`    ...`

Save the file, then move on to the next section.

## Getting Message History
Download and run the [Discord Chat Exporter GUI](https://github.com/Tyrrrz/DiscordChatExporter), and follow the instructions to download message logs of the server that you want the bot to be in. **Make sure the exported logs are in csv format!**
The more messages the bot is trained on, the better. 

Now, run the code using *RUN_CODE.bat*, and when presented with a menu, type 2 or P to select the "Parse Dataset" option. A window will open prompting you to select the csv file with your exported logs. Once selected, the csv file will be parsed, have youtube links replaced, then save a text file called "TrainingDataset.txt". This file will be used later to train the AI!


## (optional) Training Settings
Before you begin training, there are a few options in the training section of *config.json* that you may want to change to get the best experience. The defaults chosen are a good middle ground of training speed/quality, so If you don't care too much about how long training might take, you're safe to just skip this section. 

***uses_gpu***
If you're using a NVidia gpu, set this to true, otherwise set it to false to use your CPU instead. Training/generating on CPU will work, but will be SIGNIFICANTLY slower than gpu, so if you've got a gpu, use it!

***GPT2_model_type***
This determines how big the language model of the bot will be. The bigger the model, the better the responses the ai generates, but at the cost of slower speed and more VRAM usage. The options are 124M, 355M, and 774M. I highly reccomend just sticking to 124M. If you have a super powerful GPU with more than 8GB of VRAM, you can try 355M if you want better results. 774M will ONLY work if you have insane server grade GPUs with 20GB+ of VRAM.

***dataset_file_name / out_folder_name***:
The file name for the training dataset file, and the name of the output training model folder. Leave these as defaults, unless you want to have different training datasets for different situations etc.

***num_steps***
The most influential parameter you can change is how many steps the bot trains for. The number of steps correspond to how long the bot will train on a certain dataset. The more steps the bot has been trained for, the more accurate the bot's responses will be. Training for too many steps, however, might make the bot uncreative, and give too many of the exact same responses over and over (this is called "Overtraining").
I've gotten good results with the default value of 8000 steps, but if you have a really large dataset, you can increase this to 10-20k. 

***generate_every / save_every***:
How often the bot will save the training progress, and generate a training sample. Adjust these as you will.

**Other Settings**:
I wouldn't change learning rate/batch size unless I knew what I was doing. The defaults are fine.

## Training
If you don't have a super powerful GPU, or don't want to spend time on your own PC training the bot, you can train online on [Google Collab](https://colab.research.google.com/drive/15qBZx5y9rdaQSyWpsreMDnTiZ5IlN0zD?usp=sharing). Just follow the steps and then download the created *trained_model* folder to your own pc, and place it in the same directory as the *RUN_CODE.bat*.

If you'd rather train the bot on your own PC, follow the steps below.

Launch the bot's console app, then select the "Train Bot" option. It will use the *TrainingDataset.txt* created in the last step to train the bot's AI model. Training will take a long time, but it will save and print a sample generation every 1000 training steps.
By default, the bot will keep training until 8000 steps. It will save the training model into a folder called *trained_model*. This folder contains 2 files (*config.json* and *pytorch_model.bin*) that the bot will use to generate text.

## Running the bot
Now that the bot has been trained, and the *trained_model* folder has been created, you can now start using and talking to the bot on your own server!

Open the bot console program, then select the "Run Bot" option to start the bot. Once you do, you should see the bot come online on your server. All you have to do to get the bot to talk to you is to ping the bot in your messages! It will read context and use that as a prompt to generate a response, while pretending to be the user you set earlier. It can even send youtube links from time to time! If you want to turn off the bot, simply close the console window!

If the bot's responses are too crazy, try lowering the "temperature" value in the "gen" section of the *config.json*. You can also mess around with the other generation parameters if you want, but other than the temperature, the defaults are fine.
You can read more about what the generation parameters do in the [aitextgen](https://docs.aitextgen.io/) website.

Enjoy!