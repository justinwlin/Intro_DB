from flask import Flask, Blueprint, flash, render_template, request, session, redirect, url_for, send_file
import pymysql.cursors
import os
from . import routes

IMAGES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
#Connecting to MYSQL DB
connection = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='FlaskDemo2',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


#===========================
# Group Routes
#===========================
@routes.route("/createGroup", methods=["POST"])
def createGroup():
    if request.form:
        requestData = request.form 
        groupName = requestData["group"]
        groupName = groupName.replace(" ", "")
        print("GROUP NAME")
        print(groupName)
    #Make sure group doesn't exist already
    with connection.cursor() as cursor:
        query = "SELECT * FROM CloseFriendGroup WHERE groupOwner = %s AND groupName = %s"
        cursor.execute(query, (session["username"], groupName))
        result = cursor.fetchall()
        if(len(result)>0):
            session.pop('_flashes', None)
            flash('Group Name already being used')
            return redirect(url_for(".groups"))
    #Creating a Group
    with connection.cursor() as cursor:
        query = "INSERT INTO CloseFriendGroup(groupOwner, groupName) VALUES(%s, %s)"
        cursor.execute(query, (session["username"], groupName))
        connection.commit()
        session.pop('_flashes', None)
        flash('You successfully Created a Group')
    
    #Insert self into group
    with connection.cursor() as cursor:
            query = "INSERT INTO Belong (groupName, groupOwner, username) VALUES(%s, %s, %s)"
            cursor.execute(query, (groupName, session["username"], session["username"]))
            connection.commit()
    return redirect(url_for(".groups"))

#Adding someone to Group
@routes.route("/addgroup", methods=["POST"])
def addGroup():
    if request.form:
        requestData = request.form 
        username = requestData["username"]
        groupName = requestData["groupName"]
    
    session["CurrentGroupName"] = groupName
    exist = False
    alreadyIn = False
    #CHECK IF THE USER EXISTS
    with connection.cursor() as cursor:
        query = "SELECT username FROM PERSON WHERE username=%s"
        cursor.execute(query, username)
        exist = cursor.fetchall()
        if(len(exist) == 0):
            exist = True
            flash("User Doesn't Exist")
            return redirect(url_for(".groupManage"))
    #CHECK IF THE USER IS IN THE GROUP ALREADY
    with connection.cursor() as cursor:
        query = "SELECT * FROM BELONG WHERE username=%s AND groupName = %s"
        cursor.execute(query, (username, groupName))
        inGroupAlready = cursor.fetchall()
        if(len(inGroupAlready) > 0):
            alreadyIn = True
            flash("User Already in Group")
            print("USER DOES NOT EXIST")
            return redirect(url_for(".groupManage"))
    if(exist and not alreadyIn):
        #ADD THE PERSON TO THE GROUP
        with connection.cursor() as cursor:
            query = "INSERT INTO Belong (groupName, groupOwner, username) VALUES(%s, %s, %s)"
            cursor.execute(query, (groupName, session["username"], username))
            connection.commit()
    return redirect(url_for(".groupManage"))
#===========================
# GET REQUESTS FOR PAGES
#===========================
@routes.route("/groups", methods=["GET"])
def groups():
    ownedList = []
    partOf = []
    #Send Group that Own
    with connection.cursor() as cursor:
        query = "SELECT * FROM CloseFriendGroup WHERE groupOwner = %s"
        cursor.execute(query, session["username"])
        ownGroups = cursor.fetchall()
        for requests in ownGroups:
            item = dict(name = requests["groupName"])
            ownedList.append(item)
    #Groups that are part of:
    with connection.cursor() as cursor:
        query = "SELECT DISTINCT groupName FROM Belong WHERE username=%s"
        cursor.execute(query, session["username"])
        ownGroups = cursor.fetchall()
        for requests in ownGroups:
            item = dict(groupName = requests["groupName"])
            partOf.append(item)
    return render_template("friendGroup.html", username=session["username"], own = ownedList, partOf = partOf)

@routes.route("/groupManage", methods=["POST", "GET"])
def groupManage():
    peopleList = []
    if(request.method == "POST"):
        group = request.args["group_name"]
    else:
        group = session["CurrentGroupName"]
        session["CurrentGroupName"] = None
    peopleList = []
    with connection.cursor() as cursor:
        query = "SELECT username FROM BELONG WHERE groupOwner = %s AND groupName = %s"
        cursor.execute(query, (session["username"], group))
        people = cursor.fetchall()
    for person in people:
        item = dict(username = person["username"])
        peopleList.append(item)
    return render_template("groupManage.html", username=session["username"], group=group, people = peopleList)