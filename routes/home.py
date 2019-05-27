from flask import Flask, Blueprint, flash, render_template, request, session, redirect, url_for, send_file
import pymysql.cursors
from . import routes

# @routes.route('/')
# def index():
#     return render_template('index.html')

#Connecting to MYSQL DB
connection = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='FlaskDemo2',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
def getRidDups(x):
  return list(dict.fromkeys(x))

@routes.route("/home")
def home():
    #Make sure to grab the new updated changes
    connection.commit()
    #Clear Flash
    session.pop('_flashes', None)
    listPplFollowing = []
    posts = [] #photoIDs the user can see
    with connection.cursor() as cursor:
        #===================================================================
        # GRAB PHOTO OF EVERYONE USER IS FOLLOWING WITH PHOTO TO allFollowers
        #===================================================================
        query = "SELECT followeeUsername FROM Follow WHERE followerUsername = %s"
        cursor.execute(query, session["username"])
        #Grab all the names of the people we are following
        following = cursor.fetchall()
        #Insert it into a list
        for user in following:
            listPplFollowing.append(user["followeeUsername"])
        #Grab all the IDs of photos relevant that following made public
        for user in listPplFollowing:
            query = "SELECT photoID FROM Photo WHERE photoOwner=%s AND allFollowers = 1"
            cursor.execute(query, user)
            results = cursor.fetchall()
            for result in results:
                posts.append(result["photoID"])
        #===================================================================
        # GRAB PHOTO THAT ALLOWS THE PEOPLE IN A GROUP TO SEE
        #===================================================================
        #Find the groups that user is part of
        query = "SELECT DISTINCT groupName FROM Belong WHERE username = %s"
        cursor.execute(query, session["username"])
        groupsBelong = cursor.fetchall()
        groupBelongList = []
        for group in groupsBelong:
            groupBelongList.append(group["groupName"])
        #Find the photos that are avaliable to the user
        query = "SELECT DISTINCT photoID, visible from Photo"
        cursor.execute(query)
        immStep = cursor.fetchall()
        for photo in immStep:
            if(photo["visible"] in groupBelongList):
                posts.append(photo["photoID"])
        #===================================================================
        # GRAB OWN PHOTOS
        #===================================================================
        query = "SELECT DISTINCT photoID from Photo where photoOwner = %s"
        cursor.execute(query, session["username"])
        ownPhotos = cursor.fetchall()
        for photo in ownPhotos:
            posts.append(photo["photoID"])
        #===================================================================
        # Get rid of repeating IDs
        #===================================================================
        posts = getRidDups(posts)
        #===================================================================
        # Destruct from the IDS
        #===================================================================
        #Photos to put into the post
        finalPosts = []
        photos = []
        for photo in posts:
            #INITIALIZING VARIABLE
            timestamp = None
            caption = None
            url = None
            ID = None
            name = None
            taggedPeopleList = []
            #GRABBING POSTS
            query = "SELECT * FROM photo WHERE photoID = %s"
            cursor.execute(query, photo)
            result = cursor.fetchall()
            result = result[0]
            timestamp = result["timestamp"]
            caption = result["caption"]
            url = result["filePath"]
            ID = result["photoID"]
            name = result["photoOwner"] #TODO
            #Formatting the URL
            staticIndex = url.find('/static')
            url = url[staticIndex:]
            #GRABBING TAG LOGIC
            #Grabbing all the tagged people and turning it into a list > then a comma separated string value
            query = "SELECT * FROM Tag WHERE photoID = %s AND acceptedTag = True"
            cursor.execute(query, ID)
            TaggedPeople = cursor.fetchall()
            for people in TaggedPeople:
                taggedPeopleList.append(people["username"])
            # taggedPeopleList = ", ".join(taggedPeopleList)
            full_name_list = []
            query = "SELECT * FROM Person WHERE username = %s"
            #Converting into name
            for person in taggedPeopleList:
                print(person)
                cursor.execute(query, person)
                result = cursor.fetchall()
                result = result[0]
                full_name = result["fname"] + " " + result["lname"]
                print(full_name)
                full_name_list.append(full_name)
            taggedPeopleList = ", ".join(full_name_list)

            item = dict(ts=timestamp, caption = caption, url=url, ID=ID, name = name, tagPpl = taggedPeopleList)
            finalPosts.append(item)
    #Groups that are part of:
    partOf = []
    with connection.cursor() as cursor:
        query = "SELECT DISTINCT groupName FROM Belong WHERE username=%s"
        cursor.execute(query, session["username"])
        ownGroups = cursor.fetchall()
        for requests in ownGroups:
            item = dict(groupName = requests["groupName"])
            partOf.append(item)
    #SORT LIST
    finalPosts = sorted(finalPosts, key=lambda k: k['ts'], reverse=True) 

    #===================================================================
    # Store Owned Photos into a session
    #===================================================================
    myPhotos = []
    for photo in finalPosts:
        if(photo["name"] == session["username"]):
            myPhotos.append(photo)
    session["myPhotos"] = myPhotos

    return render_template("home.html", username=session["username"], posts = finalPosts, partOf=partOf)