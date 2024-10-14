from flask import Flask,render_template,flash, Blueprint,blueprints,request,redirect,url_for
from second import second
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from PIL import Image as PILImage
from PIL import Image
from gtts import gTTS
import os
from io import BytesIO

import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo

from datetime import datetime




app = Flask(__name__)
app.secret_key='123'
app.register_blueprint(second,url_prefix="")


# def text_to_speech(text,lang):
#     tts = gTTS(text=text, lang=lang)
#     tts.save("output.mp3")

#     os.system("start output.mp3")

def read_excel(file_path):
    try:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)
        # Convert the DataFrame to a list of dictionaries
        data = df.to_dict(orient='records')
        return data
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []


excel_file_path = 'Book1.xlsx'
dataset = read_excel(excel_file_path)
#print(dataset)


# Configuration for MongoDB
app.config['MONGO_URI'] = 'mongodb://localhost:27017/image_db'
mongo = PyMongo(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user_data = mongo.db.user.find_one({'username': username, 'password': password})
            if user_data:
                flash('Login successful!', 'success')
                return render_template('index.html')
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html')
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            email = request.form.get('email')
            # You should hash and salt the password in a real-world application
            mongo.db.user.insert_one({'username': username, 'password': password, 'email': email})
            flash('Sign up successful! Please log in.', 'success')
            return redirect(url_for('login'))
    else:
        flash('Sign up successful! Please log in.', 'success')
    return render_template('login.html')
    








# Configuration for file upload
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
excel_file_path = 'Book1.xlsx'



@app.route('/api',methods=['GET','POST'])
def api():
    return render_template('api.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            timestamp = datetime.utcnow()
            mongo.db.images.insert_one({'filename': filename, 'timestamp': timestamp})
        
            return render_template('index.html')
    return render_template('index.html')


@app.route('/save-image', methods=['GET', 'POST'])
def save_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['cap']
        print(file)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            timestamp = datetime.utcnow()
            mongo.db.images.insert_one({'filename': filename, 'timestamp': timestamp})
        
            return render_template('index.html')
    return render_template('index.html')






@app.route('/display',methods=['GET', 'POST'])    
def fetch_by_index():
    #image =mongo.db.images.objects.order_by('-id').first()
    #images = mongo.db.images.find()
    import tensorflow as tf
    new_model = tf.keras.models.load_model('model_fiv.h5')
    lables = ['Ashwagandha', 'Avacado', 'Castor', 'Curry_Leaf', 'neem']
    # predict with new images
    import numpy as np


    # Get the last uploaded image from MongoDB
    
    latest_image = list(mongo.db.images.find())[-1]
    #print(latest_image)
    filename = latest_image['filename']
    img = tf.keras.preprocessing.image.load_img('static/uploads/'+filename, target_size=(320, 320))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    predictions = new_model.predict(img_array)
    
    score = tf.nn.sigmoid(predictions[0])
    index=(np.argmax(score))
    #print("index=",index)
    # Read data from the Excel file
    #print("filename=",filename)
    per=(100 * np.max(score))
    # variable1 = "This image most likely belongs to {} with a {:.2f} percent confidence.".format(lables[np.argmax(score)], 100 * np.max(score))
    # text_to_speech(f"Variable 1: {variable1}")
    print("This image most likely belongs to {} with a {:.2f} percent confidence.".format(lables[np.argmax(score)], 100 * np.max(score)))
    if filename:
        #filename = latest_image['filename']
        latest_image = mongo.db.images.find_one(sort=[('upload_time', 1)])
        if 0 <= index < len(dataset):
            selected_data = dataset[index]
            data=selected_data
            return render_template('display.html', filename=filename,resu=lables[np.argmax(score)], data=data,Accuracy=per)
        else:
            return 'No images found in the database'
    return render_template('display.html', filename=filename,resu=lables[np.argmax(score)],data=data,Accuracy=per)



  

@app.route('/profile')
def profile():
    return render_template("profile.html")
@app.route('/camera', methods=['GET', 'POST'])
def camera():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            timestamp = datetime.utcnow()
            mongo.db.images.insert_one({'filename': filename, 'timestamp': timestamp})
        
            return render_template('index.html')

    return render_template('index.html')










if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)