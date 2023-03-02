from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import os
import configparser
from transaction_import import Database

config = configparser.ConfigParser()
config.read("config.ini")

host = config["MYSQL"]["HOST"]
user = config["MYSQL"]["USER"]
passwd = config["MYSQL"]["PASSWORD"]
database = config["MYSQL"]["DATABASE"]
table = config["MYSQL"]["TABLE"]


app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["UPLOAD_FOLDER"] = "static/files"


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route("/", methods=["GET", "POST"])
def home():

    db = Database(host=host, user=user, password=passwd, database=database)
    trans_history = db.select_all("transactions")
    return render_template("index.html", trans_history=trans_history)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadFileForm()

    db = Database(host=host, user=user, password=passwd, database=database)
    if form.validate_on_submit():
        file = form.file.data  # First grab the file
        file_upload = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            app.config["UPLOAD_FOLDER"],
            secure_filename(file.filename),
        )
        file.save(file_upload)  # Then save the file
        transactions = db.import_csv(table, file_upload)
        return render_template("upload_list.html", form=transactions)
    return render_template("upload.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
