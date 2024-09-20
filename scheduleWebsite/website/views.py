from flask import Blueprint, render_template

views = Blueprint('views',__name__)

#defining root/home page
@views.route('/')
def home():
    return render_template("home.html")