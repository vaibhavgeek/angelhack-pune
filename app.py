import os
import sys
import json
from constants import *
import requests
from flask import Flask, request
from util import *
from mathlib9 import *
import traceback
import random
from pymongo import MongoClient
import base64

app = Flask(__name__)
client = MongoClient(CONNECTION)
db = client.angelhack10
    
labelist = ["child abuse" , "bribe" , "domestic violence" , "acid attack" , "dowry" ]

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200   



@app.route('/', methods=['POST'])
def webhook():   
    data = request.json
    print data
    try:
        user = None
        payload = request.get_data()
        try:
            sender, message = messaging_events(payload)
            print message
            print sender
        except:
            try:
                print("case for complaint:")
                message, sender = get_message(data)
                print message
                print sender
            except:
                print("case for url:")
                message,sender = urlparser(payload)
                print message
                print sender
        user = db.user.find_one({"fbId": sender})
        fbinfo = get_user_info(sender)
        if user is None:
            db.user.insert({"fbId": sender ,  "first_name" : fbinfo["first_name"] , "last_name" : fbinfo["last_name"] , "profile_pic" : fbinfo["profile_pic"]})
            user = db.user.find_one({"fbId": sender })

       # db.user.update({"fbId": user["fbId"]} , {"$set" : {}})
        
         
        print message
        if message == "complaint":
            send_text_message(sender , "Hi, " + user["first_name"] + " We are here to help you. Please give us following info for the person facing the injustice")
            send_replies(
                 sender, "Religion",
                 [
                     quick_reply("Hindu",payload="relHindu"),
                     quick_reply("Muslim", payload="relMuslim"),
                     quick_reply("Sikh",payload="relSikh"),
                     quick_reply("Christian",payload="relChristian"),
                     quick_reply("Buddhism",payload="relBuddhism")
                 ]) 
            complaint = db.complaints.insert({"fbId" : sender})
        elif message.startswith("rel"):
            db.complaints.update({"fbId": user["fbId"]} , {"$set" : { "rel" : message[3:] }})
            send_text_message(sender , "Thanks for your telling your religion. We have noted it down.")
            send_replies(
                 sender, "Caste",
                 [   
                     quick_reply("General",payload="casGeneral"),
                     quick_reply("SC",payload="casSC"),
                     quick_reply("ST", payload="casST"),
                     quick_reply("OBC",payload="casOBC"),
                     quick_reply("Other",payload="casOther")
                 ]) 
        elif message.startswith("cas"): 
            db.complaints.update({"fbId": user["fbId"]} , {"$set" : { "caste" : message[3:] }})
            send_text_message(sender , "Thanks for your telling your caste. We have noted it down.")
            send_replies(
                 sender, "Gender",
                 [
                     quick_reply("Male",payload="genMale"),
                     quick_reply("Female",payload="genFemale"),
                     quick_reply("Other",payload="genOther")

                 ]) 
        elif message.startswith("gen"): 
            db.complaints.update({"fbId": user["fbId"]} , {"$set" : { "gender" : message[3:] }})
            send_text_message(sender , "Thanks for your telling your Gender. We have noted it down.")
            send_text_message(sender,"Can you please tell us about the complaint?")


        elif message == "imhelp": 
            send_text_message(sender , "Please provide us your location so that we can asset you")
    
            


        elif message.startswith("Complaint"):
            many = ""
            dat = json.dumps({"encodingType": "UTF8","document": {"type": "PLAIN_TEXT","content": message[10:]}})
            a = requests.post("https://language.googleapis.com/v1/documents:analyzeEntities?key=AIzaSyCsnF5slLTIh4CxKnO82SNfc3A6YHNwOiw",dat)
            data_label_text =  a.json()
            many = ""
            for utility in data_label_text["entities"]:
                if utility["type"] == "OTHER":
                    useful = utility["name"] + " : " + str(utility["salience"]) + " , "
                    many = many + useful
            print many[:-2]
            db.complaints.update({"fbId": user["fbId"]} , {"$set" : { "complaint_text_labels" : many }})
            db.complaints.update({"fbId": user["fbId"]} , {"$set" : { "complaint_text" : message }})
            send_text_message(sender,"We are here to help you, Can you please upload a image related to the voilence.Anything might be helpful")


        elif message.startswith("https"):
            many = ""
            print "hey hi url worked"
            base = base64.b64encode(requests.get(message).content)
            print "base64 worked"
            dat = json.dumps({"requests":[{"image":{"content":str(base)},"features":[{"type":"WEB_DETECTION","maxResults":100}]}]})
           
            a = requests.post("https://vision.googleapis.com/v1/images:annotate?key=AIzaSyCsnF5slLTIh4CxKnO82SNfc3A6YHNwOiw",dat)
           
            data = a.json()
            
            Labels = data["responses"][0]["webDetection"]["webEntities"]
            print Labels
            for Label in Labels[:-1]:
                print Label
                try:
                    many = many + Label["description"] +','
                    print many
                except:
                    print "failed"

                
            print "Labels caught"
            db.complaints.update({"fbId": user["fbId"]} , {"$set" : { "complaint_pic" : message }})
            db.complaints.update({"fbId": user["fbId"]} , {"$set" : { "complaint_pic_labels":many }})
             
            send_text_message(sender,"Thanks for the image. We are making sure of the aunthenticity of image.")

        # elif message == "topics_to_learn" or message == "back":
        #     send_text_message(sender , "1.) Operation on Numbers\n2.) Rational Numbers\n3.)Linear Equation in One Variable\n4.)Linear Equations in Two Variables\n5.) Quadratic Equations")
        #     send_replies(
        #         sender, "Enter the number corresponding to the chapter. Example '1' for Operation on Numbers",
        #         [
        #             quick_reply("1",payload="oon"),
        #             quick_reply("2", payload="rat"),
        #             quick_reply("3",payload="lin"),
        #             quick_reply("4",payload="lin2"),
        #             quick_reply("5",payload="quad")
        #         ]) 
        # elif message == "1": 
        #    print "try"
        # elif message == "2": 
        #     send_button_template_message(
        #         sender,
        #         "You have selected the topic, Rational Numbers. What do you want to do next?",
        #         [
        #             generate_button("Learn", "learn" + message),
        #             generate_button("Practice", "prac" + message),
        #             generate_button("Ask Doubts", "ask_doubt" + message)
        #         ]
        #     )
        # elif message == "3": 
        #     send_button_template_message(
        #         sender,
        #         "You have selected the topic, Linear Equation in one variable. What do you want to do next?",
        #         [
        #             generate_button("Learn", "learn" + message),
        #             generate_button("Practice", "prac" + message),
        #             generate_button("Ask Doubts", "ask_doubt" + message)
        #         ]
        #     )
        # elif message == "4": 
        #     send_button_template_message(
        #         sender,
        #         "You have selected the topic, Linear Equation in Two variables. What do you want to do next?",
        #         [
        #             generate_button("Learn", "learn" + message),
        #             generate_button("Practice", "prac" + message),
        #             generate_button("Ask Doubts", "ask_doubt" + message)
        #         ]
        #     )
        # elif message == "5": 
        #     send_button_template_message(
        #         sender,
        #         "You have selected the topic, Quadratic Equations. What do you want to do next?",
        #         [
        #             generate_button("Learn", "learn" + message),
        #             generate_button("Practice", "prac" + message),
        #             generate_button("Ask Doubts", "ask_doubt" + message)
        #         ]
        #     )
    except: 
        pass        
    return "ok"

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
