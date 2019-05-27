from flask import Flask, Blueprint, flash, render_template, request, session, redirect, url_for, send_file
import pymysql.cursors
import hashlib
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
#Base URL
@routes.route("/")
def index():
    if "username" in session:
        return redirect(url_for(".home"))
    return render_template("index.html")

@routes.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@routes.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

#===========================
# AUTHENTICATION
#===========================
@routes.route("/loginAuth", methods=["POST"])
def loginAuth():
    if request.form:
        requestData = request.form
        username = requestData["username"]
        plaintextPasword = requestData["password"]
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
        with connection.cursor() as cursor:
            query = "SELECT * FROM Person WHERE username = %s AND password = %s"
            cursor.execute(query, (username, hashedPassword))
        data = cursor.fetchone()
        if data:
            session["username"] = username
            posts = [1, 2, 3, 4, 5,6]
            return redirect(url_for(".home"))
        error = "Incorrect username or password."
        return render_template("login.html", error=error)
    error = "An unknown error has occurred. Please try again."
    return render_template("login.html", error=error)

@routes.route("/registerAuth", methods=["POST"])
def registerAuth():
    if request.form:
        requestData = request.form
        username = requestData["username"]
        plaintextPasword = requestData["password"]
        fname = requestData['fname']
        lname = requestData['lname']
        hashedPassword = hashlib.sha256(plaintextPasword.encode("utf-8")).hexdigest()
        try:
            with connection.cursor() as cursor:
                query = "INSERT INTO Person (fname, lname, username, password) VALUES (%s,%s,%s, %s)"
                cursor.execute(query, (fname, lname, username, hashedPassword))
                connection.commit()
        except pymysql.err.IntegrityError:
            error = "%s is already taken." % (username)
            return render_template('register.html')    
        return redirect(url_for(".login"))
    error = "An error has occurred. Please try again."
    return render_template("register.html")

@routes.route("/logout", methods=["GET"])
def logout():
    session.pop("username")
    return redirect("/")