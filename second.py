from flask import Flask,render_template,flash, Blueprint


second=Blueprint("second", __name__,static_folder="static",template_folder="templates")
@second.route('/s')
def s():
    return render_template("s.html")


