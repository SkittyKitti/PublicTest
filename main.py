from github import Github
import time
import os
import pickle
import sys
# Gmail API utils


from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
    #Binance
from binance.client import Client



SCOPES = ['https://mail.google.com/']
our_email = 'antoniu.malis@gmail.com'
apiKey = "ActpohLhavLK1XZQi5T1EfJRa7UTvakyoPzJfhGaQjPFK8rTQkAVhs68oCRdUsv2"
apiSecurity = "TLVPmUirOMg87j4wJ091p7p9KFXgLQDaxUAD2kv9xvVAigt5FfTdIZk5X2OD1I04"
access_token = "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"



def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages

def delete_messages(service, query):
    messages_to_delete = search_messages(service, query)
    # it's possible to delete a single message with the delete API, like this:
    # service.users().messages().delete(userId='me', id=msg['id'])
    # but it's also possible to delete all the selected messages with one query, batchDelete
    return service.users().messages().batchDelete(
      userId='me',
      body={
          'ids': [ msg['id'] for msg in messages_to_delete]
      }
    ).execute()

    #Gmail API Section
go = True
#while go:
service = gmail_authenticate()
results = search_messages(service, "DynamicEffect")
login = Github(access_token)
user = login.get_user()
my_repos = user.get_repos()
for repo in login.search_repositories("LastTradingBot"):
    new_target=repo
#for repo in my_repos:
#    print(repo)
target=new_target
#target=my_repos[2]
#print(results[0])

# Binance API Section

client = Client(apiKey, apiSecurity)
test = client.futures_position_information()
test2 = client.futures_account_balance()
test3 = client.futures_coin_mark_price()
for m in test2:
    if m["asset"]=="USDT":
        cash=float(m["balance"])

for z in test3:
    if z["symbol"]=="ADAUSD_PERP":
        aid=float(z["markPrice"])
position_desired= round((cash/aid)*0.07 *10) #(cash/aid)* % of total * leverage




contents = target.get_contents("test.txt")
snip = list(contents.decoded_content.decode())
stu = "".join(snip)
stud = stu.replace("\n", " ")
studd = stud.split()
print(studd)
last_list = [float(x) for x in studd]

# new_content = []
# with open("test.txt") as sheet:
#    content = sheet.readlines()
# for thing in content:
#    new_content.append(float(thing.replace("\n","")))

stop_value = last_list[0]
counter = last_list[1]
daily = last_list[2]
repeater = last_list[3]
side = last_list[4]
confirmation = False

for t in test:
    if t["symbol"]=="ADAUSDT":
        placehold=t["positionAmt"]
        midpoint=abs(float(placehold))
        if midpoint > 0:
            printentry=t["entryPrice"]
            print(f"size= {midpoint}, entryPrice= {printentry}")
            current_position = t
            position_amount=midpoint
            confirmation = True

if confirmation:
    short_stop_value = round(1.01 * stop_value, 4)
    long_stop_value = round(0.99 * stop_value, 4)
    calc = 1.01 * float(current_position["entryPrice"])
    target_long = round(calc, 4)
    new_calc = 0.99 * float(current_position["entryPrice"])
    target_short = round(new_calc, 4)

if results != []:
    #print("a")
    msg = service.users().messages().get(userId='me', id=results[0]['id'], format='full').execute()
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")

    #print(msg["snippet"])
    string = msg["snippet"]
    new_list = string.split()
    print(new_list)
    #sys.exit("bye")

    if side==1 and new_list[0]=="ImprovedLong":
        delete_messages(service, "DynamicEffect - ImprovedLong")
    if side==2 and new_list[0]=="ImprovedShort":
        delete_messages(service, "DynamicEffect - ImprovedShort")

    if new_list[0] == "Stop":
        counter += 1
        if confirmation:
            if side==1 and float(new_list[4])>float(new_list[2]):
                stop_value = float(new_list[4])
            if side==2 and float(new_list[4])<float(new_list[2]):
                stop_value = float(new_list[4])
        if not confirmation:
            stop_value = float(new_list[2])
        if counter % 3 == 0:
            delete_messages(service, "DynamicEffect - Stop")
        #target.update_file(contents.path, "new commit", f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}", contents.sha)
        #with open("test.txt", mode="w") as file:
        #    file.write(f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}")

    if confirmation:
        short_stop_value = round(1.01 * stop_value, 4)
        long_stop_value = round(0.99 * stop_value, 4)
        calc = 1.01 * float(current_position["entryPrice"])
        target_long = round(calc, 4)
        new_calc = 0.99 * float(current_position["entryPrice"])
        target_short = round(new_calc, 4)

    if new_list[0] == "ImprovedLong" and side == 0:
        # Futures Market Order
        if confirmation==False and stop_value != 0 and daily == 0:
            side = 1
            #target.update_file(contents.path, "new commit", f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}", contents.sha)
            #with open("test.txt", mode="w") as file:
            #    file.write(f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}")
            buyorder = client.futures_create_order(symbol="ADAUSDT", side="BUY", type="MARKET", quantity=position_desired)
            print(buyorder)
            delete_messages(service, "DynamicEffect - ImprovedLong")

    if new_list[0] == "ImprovedShort" and side == 0:
        # Futures Market Order
        if confirmation==False and stop_value != 0 and daily == 0:
            side = 2
            #target.update_file(contents.path, "new commit", f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}", contents.sha)
            #with open("test.txt", mode="w") as file:
            #    file.write(f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}")
            buyorder = client.futures_create_order(symbol="ADAUSDT", side="SELL", type="MARKET", quantity=position_desired)
            print(buyorder)
            delete_messages(service, "DynamicEffect - ImprovedShort")

# print(current_position["entryPrice"])
if confirmation and repeater ==0 and side==0:
    if current_position["entryPrice"] > current_position["liquidationPrice"]:
        side = 1
    elif current_position["entryPrice"] < current_position["liquidationPrice"]:
        side = 2
#target.update_file(contents.path, "new commit", f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}",
#                   contents.sha)
# with open("test.txt", mode="w") as file:
#    file.write(f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}")

if side!=0 and repeater == 0:
    daily = 1
    counter = 0
    repeater = 1
    #target.update_file(contents.path, "new commit", f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}",
    #                   contents.sha)
    # with open("test.txt", mode="w") as file:
    #    file.write(f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}")


if confirmation==False and counter > 71 and stop_value != 0 and daily == 1 and side != 0:
    counter = 0
    daily = 0
    repeater = 0
    side = 0
    #target.update_file(contents.path, "new commit", f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}",
    #                   contents.sha)
    # with open("test.txt", mode="w") as file:
    #    file.write(f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}")



if confirmation and repeater == 1 and side == 1:
    close_long = client.futures_cancel_all_open_orders(symbol="ADAUSDT")
    limitclose = client.futures_create_order(symbol="ADAUSDT", side="SELL", type="LIMIT", quantity=position_amount,
                                             price=target_long, timeInForce="GTC", reduceOnly="True")
    stopmarket = client.futures_create_order(symbol="ADAUSDT", side="SELL", type="STOP_MARKET", quantity=position_amount,
                                             stopPrice=long_stop_value, reduceOnly="True")

if confirmation and repeater == 1 and side == 2:
    close_short = client.futures_cancel_all_open_orders(symbol="ADAUSDT")
    limitclose = client.futures_create_order(symbol="ADAUSDT", side="BUY", type="LIMIT", quantity=position_amount,
                                             price=target_short, timeInForce="GTC", reduceOnly="True")
    stopmarket = client.futures_create_order(symbol="ADAUSDT", side="BUY", type="STOP_MARKET", quantity=position_amount,
                                             stopPrice=short_stop_value, reduceOnly="True")

target.update_file(contents.path, "new commit", f"{stop_value}\n{counter}\n{daily}\n{repeater}\n{side}",
                   contents.sha)

#time.sleep(300)

        #Futures Market Order
        #if no_order == True:
        #    buyorder = client.futures_create_order(symbol="ADAUSDT", side = "BUY", type="MARKET", quantity=20)
        #    print(buyorder)

        #limitclose = client.futures_create_order(symbol="ADAUSDT", side="SELL", type="LIMIT", quantity=20,
        #                                         price=target_long, timeInForce="GTC", reduceOnly= "True")
        #stopmarket = client.futures_create_order(symbol="ADAUSDT", side="SELL", type="STOP_MARKET", quantity="20",
        #                                         stopPrice=target_stop, reduceOnly= "True")
