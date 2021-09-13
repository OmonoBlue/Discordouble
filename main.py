import os
import sys
import argparse
import json
import shutil
import asyncio

import tkinter as tk
from tkinter import filedialog

import bot
import data_parser


def load_config(configFileName = "config.json", exampleFileName = "example_config.json"):
    if not os.path.isfile(configFileName):
        if os.path.isfile(exampleFileName):
            shutil.copyfile(exampleFileName, configFileName)
            print("Please fill out the file '%s', then re-run the program" % configFileName)
        else:
            print("ERROR: Config and example config files are missing!")
        return None
    
    config = {}
    
    with open(configFileName, 'r') as configFile:
        config = json.load(configFile)
    
    return config
    

def main():
    
    config = load_config()
    if config != None:
        while True:
            choice = get_user_input()
            print("You chose %s!" % choice)
            
            if choice == "R":
                print("Running bot...\n")
                bot.run_bot(config)
                break
            elif choice == "P":
                print("Parsing Dataset...\n")
                parse_csv(config)
            elif choice == "T":
                print("Training bot...\n")
                bot.train_bot(config)
            elif choice == "Q":
                break
    input("Press Enter to exit...")
    

def parse_csv(config):
    parseConfig = config["parsing"]
    ## Promp user for dataset CSV file
    print("\nPlease choose a CSV file to parse...")
    root = tk.Tk()
    root.withdraw() 
    
    file_path = filedialog.askopenfilename()
    
    if not file_path.endswith(".csv"):
        print("File must be a CSV file!")
    else:
        try:
            data_parser.parse_csv(file_name = file_path, 
                out_name = parseConfig["out_file_name"], 
                line_limit = parseConfig["line_limit"], 
                replace_YT = parseConfig["replace_youtube_links"],
                include_attachments = parseConfig["include_attachments"])
        except Exception as e:
            print("Error parsing CSV: ")
            print(e)

def get_user_input():
    options = {
        "1" : "R",
        "2" : "P",
        "3" : "T",
        "4" : "Q"
    }
        
    while True:
        print("\nPlease select an option:\n")
        print("1 - (R)un Bot")
        print("2 - (P)arse Dataset")
        print("3 - (T)rain Bot using Parsed Dataset")
        print("4 - (Q)uit")
        
        choice = input("\nYour choice: ").upper()[0]
        print()
        
        if choice in options:
            return options[choice]
        elif choice in options.values():
            return choice
        else:
            print("Invalid input!\n")
    
    
if __name__ == "__main__":
    main()