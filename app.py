from flask import Flask,render_template,request,redirect,flash, send_file
from werkzeug.utils import secure_filename
import os
from pdf2image import convert_from_path
import easyocr
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import json
import io
import cv2
import numpy as np
app = Flask(__name__)
app.secret_key = "super secret key"
UPLOAD_FOLDER = '/Users/shivraj/Downloads/entity-ext/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DOWNLOAD_FOLDER = '/Users/shivraj/Downloads/entity-ext/json'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
EXTENSIONS = {'png', 'jpg','jpeg','tiff'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected','error')
            return render_template('index.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(1)
            img=cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_hsv=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_red = np.array([0,50,50])
            upper_red = np.array([10,255,255])
            mask0 = cv2.inRange(img_hsv, lower_red, upper_red)
            lower_red = np.array([170,50,50])
            upper_red = np.array([180,255,255])
            mask1 = cv2.inRange(img_hsv, lower_red, upper_red)
            maskxx = mask0+mask1
            contours = cv2.findContours(maskxx, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            mask = np.ones(img.shape[:2], dtype="uint8") * 255
            cnt=0
            dict={}
            st='box'
            count=0
            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                if w*h>500:
                    cv2.rectangle(mask, (x, y), (x+w, y+h), (0, 0, 255), -1)
                    cropped_image = img[y:y+h, x:x+w]
                    reader = easyocr.Reader(['en']) # load once only in memory.
                    # gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
                    # sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                    # sharpen = cv2.filter2D(gray, -1, sharpen_kernel)
                    # thresh = cv2.threshold(sharpen, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                    r_easy_ocr=reader.readtext(cropped_image,detail=0)
                    print(r_easy_ocr)

                    dict[st+str(count)]=r_easy_ocr
                    count=count+1
            with open(os.path.join(app.config['DOWNLOAD_FOLDER'], filename.rsplit('.', 1)[0]+'.json'), "w") as outfile:
                json.dump(dict, outfile)
                FILENAME =  filename.rsplit('.', 1)[0]+'.json'
                app.config['FILENAME'] = FILENAME
            flash('Your file is ready to download','download')
            return redirect('/')
    else:
        return render_template('index.html')

@app.route('/download',methods=['GET', 'POST'])
def download():
    return send_file(app.config['DOWNLOAD_FOLDER']+'/'+app.config['FILENAME'],as_attachment=True)
    
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

