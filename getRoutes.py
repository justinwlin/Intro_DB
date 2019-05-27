from flask import Blueprint

simple_page = Blueprint('simple_page', __name__, template_folder='templates')

@simple_page.route("/login", methods=["GET"])
def login():
    return render_template("login.html")