from flask import Flask, Blueprint, flash, render_template, request, session, redirect, url_for, send_file
import pymysql.cursors
import os
from . import routes
from init1 import app
from werkzeug.utils import secure_filename

#Connecting to MYSQL DB
connection = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='FlaskDemo2',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


#===========================
# TAG ROUTES
#===========================
@routes.route("/acceptTag", methods=["Post"])
def acceptTag():
    photoID = request.args["photoID"]
    with connection.cursor() as cursor:
        query = "UPDATE Tag SET acceptedTag = 1 WHERE photoID = %s AND username  = %s"
        cursor.execute(query, (photoID, session["username"]))
        connection.commit()
    return redirect(url_for(".tags"))

@routes.route("/declineTag", methods=["Post"])
def declineTag():
    photoID = request.args["photoID"]
    with connection.cursor() as cursor:
        query = "DELETE FROM Tag WHERE photoID = %s AND username  = %s"
        cursor.execute(query, (photoID, session["username"]))
        connection.commit()
    return redirect(url_for(".tags"))

@routes.route("/addtags", methods=["POST"])
def addTags():
    #Variables
    exist = False
    #GRAB FORM DATA
    if request.form:
        requestData = request.form 
        photoID = requestData["photoID"]
        username = requestData["username"]

    #MAKE SURE THE USER EXISTS
    with connection.cursor() as cursor:
        query = "SELECT username FROM Person WHERE username = %s"
        cursor.execute(query, username)
        exist = cursor.fetchall()
        if(len(exist) > 0):
            exist = True
    if(not exist):
        session.pop('_flashes', None)
        flash("User Doesn't Exist")
        return redirect(url_for(".tags"))
    else:
        #Make sure tag doesn't already exist
        with connection.cursor() as cursor:
            query = "SELECT username FROM Tag WHERE photoID = %s AND username = %s"
            cursor.execute(query, (photoID, username))
            alreadyTagged = cursor.fetchall()
            if(len(alreadyTagged) > 0):
                session.pop('_flashes', None)
                flash("User Already been tagged or sent a request")
                return redirect(url_for(".tags"))
        #ADD TAG TO MYSQL
        with connection.cursor() as cursor:
            #If User tagging himself
            if(session["username"] == username):
                query = "INSERT INTO Tag (username, photoID, acceptedTag) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, photoID, True))
                connection.commit()
            #If User is tagging someone else
            else:
                query = "INSERT INTO Tag (username, photoID, acceptedTag) VALUES (%s, %s, %s)"
                cursor.execute(query, (username, photoID, False))
                connection.commit()
    return redirect(url_for(".tags"))

@routes.route("/tags", methods=["GET"])
def tags():
    posts = session["myPhotos"]
    IDS = []
    for post in posts:
        IDS.append(post["ID"])
    
    with connection.cursor() as cursor:
        query = "SELECT Photo.photoOwner, Tag.username, Tag.photoID, Photo.filePath FROM TAG NATURAL JOIN Photo WHERE acceptedTag = 0 AND username = %s"
        cursor.execute(query, session["username"])
        tagRq = cursor.fetchall()
        reqs = []
        for request in tagRq:
            owner = request["photoOwner"]
            photoID = request["photoID"]
            photo = request["filePath"]
            staticIndex = photo.find('/static')
            photo = photo[staticIndex:]
            item = dict(owner = owner, photoID = photoID, photo = photo)
            reqs.append(item)

    return render_template("tag.html", username=session["username"], posts = posts, IDS = IDS, reqs = reqs)
