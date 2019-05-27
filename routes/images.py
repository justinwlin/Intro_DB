from flask import Flask, Blueprint, flash, render_template, request, session, redirect, url_for, send_file
import pymysql.cursors
import os
from . import routes
from init1 import app
from werkzeug.utils import secure_filename

IMAGES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images")
UPLOAD_FOLDER = '/Users/justinlin/Documents/Github/DB2/static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

#Connecting to MYSQL DB
connection = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='FlaskDemo2',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            session.pop('_flashes', None)
            flash('No file part')
            return redirect(url_for(".home"))
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            session.pop('_flashes', None)
            flash('No selected file')
            return redirect(url_for(".home"))
        if file and allowed_file(file.filename):
            #UPLOAD IMAGE
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            fileloc = os.path.join(UPLOAD_FOLDER, filename)
            #GRAB VARIABLES
            if request.form:
                requestData = request.form 
                caption = requestData["caption"]
                visibility = requestData["visibility"]
            #UPLOAD POST
            #caption, visibility, filePath
            with connection.cursor() as cursor:
                query = "INSERT INTO Photo (photoOwner, filePath, caption, allFollowers, visible) VALUES(%s, %s, %s, %s, %s)"
                photoOwner = session["username"]
                filePath = fileloc
                caption = caption
                if(visibility == 'public'):
                    allFollowers = True
                    visible = None
                else:
                    allFollowers = False
                    visible = visibility
                cursor.execute(query, (photoOwner, filePath, caption, allFollowers, visible))
                connection.commit()
            return redirect(url_for(".home"))