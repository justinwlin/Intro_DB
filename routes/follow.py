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

@routes.route("/follow", methods=["GET"])
def follow():
    requestList = []
    followerList = []
    currentlyFollow = []
    #=========================
    #Grabbing all Requests
    #=========================
    with connection.cursor() as cursor:
        query = "SELECT * FROM Follow WHERE followeeUsername = %s AND acceptedfollow = False"
        cursor.execute(query, session["username"])
        followRequests = cursor.fetchall()
    for requests in followRequests:
        item = dict(user = requests["followerUsername"])
        requestList.append(item)

    #=========================
    #Grabbing all Followers    
    #=========================
    with connection.cursor() as cursor:
        query = "SELECT * FROM Follow WHERE followeeUsername = %s AND acceptedfollow = True"
        cursor.execute(query, session["username"])
        followRequests = cursor.fetchall()
    for requests in followRequests:
        item = dict(user = requests["followerUsername"])
        followerList.append(item)
    #=========================
    #People you follow  
    #=========================
    with connection.cursor() as cursor:
        query = "SELECT * FROM Follow WHERE followerUsername = %s AND acceptedfollow = True"
        cursor.execute(query, session["username"])
        followRequests = cursor.fetchall()
    for requests in followRequests:
        item = dict(user = requests["followeeUsername"])
        currentlyFollow.append(item)
    print("REQUEST")
    print(requestList)
    return render_template("follow.html", username = session['username'], requests = requestList, followers = followerList, follows = currentlyFollow)

    #return render_template("follow.html", username=session["username"], requests = requestList, followers = followerList, follows = currentlyFollow)

#===========================
# Following Routes
#===========================
@routes.route("/acceptRequest", methods=["POST"])
def acceptRequest():
    follower = request.args["follower"]
    followee = session['username']
    query = "UPDATE Follow SET acceptedfollow = True WHERE followerUsername = %s AND followeeUsername = %s "
    with connection.cursor() as cursor:
        cursor.execute(query, (follower, followee))
        connection.commit()
    return redirect(url_for(".follow"))

@routes.route("/declineRequest", methods=["POST"])
def declineRequest():
    follower = request.args["follower"]
    followee = session['username']
    query = "DELETE FROM Follow WHERE followerUsername = %s AND followeeUsername = %s "
    with connection.cursor() as cursor:
        cursor.execute(query, (follower, followee))
        connection.commit()
    return redirect(url_for(".follow"))

@routes.route("/followAuth", methods=["POST"])
def followAuth():
    if request.form:
        requestData = request.form 
        follow = requestData["follow"]
    #=================================
    #Fail Checks
    #=================================
        #=================================
        #First Check if the user exists
        #=================================
        with connection.cursor() as cursor:
            #Check if user exists
            query = "SELECT username FROM Person WHERE username = %s"
            cursor.execute(query, follow)
            result = cursor.fetchall()
        followee = follow
        follower = session["username"]
        #=================================
        #Make sure previous request doesn't exist
        #=================================
        with connection.cursor() as cursor:
            #Check if user exists
            query = "SELECT followeeUsername FROM Follow WHERE followerUsername = %s AND followeeUsername = %s"
            cursor.execute(query, (session['username'], follow))
            checkIfExist = cursor.fetchall()
        if(len(checkIfExist) > 0):
            session.pop('_flashes', None)
            flash('You have already sent a request')
            return redirect(url_for(".follow"))
        #=================================
        #Don't allow to follow self
        #=================================
        if(len(result) == 0):
            #Flash user doesn't exist
            session.pop('_flashes', None)
            flash('User doesn\'t exist')
            return redirect(url_for(".follow"))
        if(followee == follower):
            session.pop('_flashes', None)
            flash('Can not follow yourself')
            return redirect(url_for(".follow"))
    #=================================
    # Passes Checks
    #=================================
        #=================================
        # Insert Follow Request
        #=================================
        with connection.cursor() as cursor:
            query = "INSERT INTO Follow (followerUsername, followeeUsername, acceptedfollow) VALUES (%s, %s, %s)"
            cursor.execute(query, (follower, followee, False))
            connection.commit()
        session.pop('_flashes', None)
        flash('You successfully sent a request')
    return redirect(url_for(".follow"))