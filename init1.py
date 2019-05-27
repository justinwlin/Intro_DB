from flask import Flask, Blueprint, flash, render_template, request, session, redirect, url_for, send_file
import os
import uuid
import pymysql.cursors
from functools import wraps
import time

#Importing Routes
app = Flask(__name__)
app.secret_key = "super secret key"
IMAGES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
from routes import *
app.register_blueprint(routes)

#Connecting to MYSQL DB
connection = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='FlaskDemo2',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# def login_required(f):
#     @wraps(f)
#     def dec(*args, **kwargs):
#         if not "username" in session:
#             return redirect(url_for("login"))
#         return f(*args, **kwargs)
#     return dec
    
if __name__ == "__main__":
    if not os.path.isdir("images"):
        os.mkdir(IMAGES_DIR)
    app.run()
