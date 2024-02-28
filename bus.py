import requests
import subprocess
import re
import json
import sys

selected_stop = None #Will be read from config.json
agency_code = "112"
api_url = "https://rest.citybus.gr"
language = "el"

date_format = "%d-%m-%Y"

#=====================================================

def get_new_token() -> str:
    '''
        If we have no saved token or it has expired, we need to retrieve a new one from the server.
        
        This function requests for a new token.
    '''
    resp = requests.get("https://patra.citybus.gr/el/stops")
    match = re.search(r".*const token = '(.*)'.*", resp.text)
    return match.group(1)

#=====================================================

def read_token() -> str:
    '''
        Once a token is used for the first time, it is saved in token.txt for later use until it expires.

        This function reads the saved token.
    '''
    token = None

    try:
        with open("token.txt", "r") as f:
            token = f.read()
    except FileNotFoundError:
        #print("Missing token.txt file")
        pass
    
    return token

#=====================================================

def write_token(token: str) -> None:
    '''
        Once a token is used for the first time, it is saved in token.txt for later use until it expires.

        This function writes the token to the file.
    '''
    with open("token.txt", "w") as f:
        token = f.write(token)

#=====================================================
        

if __name__ == "__main__":

    #Read bus stop fron config.json
    with open("config.json", "r") as f:
        selected_stop = json.load(f)["stop"]

    token = read_token()

    req_url = f"{api_url}/api/v1/{language}/{agency_code}/stops/live/{selected_stop}"

    resp = None

    got_new_token = False

    while(1):
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json; charset=utf-8"
        }

        try:
            resp = requests.get(req_url, headers = headers)
        except requests.ConnectionError:
            print("Could not reach server")
            sys.exit()

        #print(resp.headers)

        if resp.status_code != requests.codes.ok: #Token probably expired
            match = re.search(r'error="(.*?)"', resp.headers.get("WWW-Authenticate", ""))

            if match is not None:
                if match.group(1) == "invalid_token":
                    got_new_token = True
                    token = get_new_token()

                    #Now that we have the new token, we will try to make another request
                    #If it succeeds, we write the new token 
                else:
                    break
            else:
                print("No buses at the moment")
                sys.exit()
            
        else:
            if got_new_token:
                write_token(token)
            break

    subprocess.run("clear", shell=True)

    if resp.status_code == requests.codes.ok:
        json_obj = resp.json()

        print("ΠΑΝΕΠΙΣΤΗΜΙΟ\n================================================================")

        last_min = 0
        last_sec = 0

        for v in json_obj["vehicles"]:
            if (v["lineCode"] in ["601", "604"]):
                print(f"> {v['lineCode']} - {v['lineName']} σε {v['departureMins']:02}:{v['departureSeconds']:02}")

        print("\nΚΕΝΤΡΟ\n================================================================")

        last_min = 0
        last_sec = 0

        for v in json_obj["vehicles"]:
            if (v["lineCode"] == "609"):
                print(f"> {v['lineCode']} - {v['lineName']} σε {v['departureMins']:02}:{v['departureSeconds']:02}")

        print("\n")
