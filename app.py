from flask import Flask
from flask import render_template
from flask import Flask,flash,render_template,request,redirect,jsonify
from werkzeug.utils import secure_filename
import os
from ibnr_cal import *




UPLOAD_FOLDER = '.\\tmp'
ALLOWED_EXTENSIONS = set(['xlsx','csv','xls'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug=True
app.config['SECRET_KEY'] = '123456'



@app.route('/', methods=['GET', 'POST'])
def index():
    print('index')
    return render_template('index.html')





@app.route('/upload', methods=['GET', 'POST'])
def upload():
    print('upload')
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':

        if 'data' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['data']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            returndata=read_data(path)
            return jsonify(returndata)
    return ''

@app.route('/caltri', methods=['GET', 'POST'])
def caltri():
    print(caltri)


    import pdb
    pdb.set_trace()


    print(request.json)
    filename = request.data['filename']
    start_date=request.data['start_date']
    end_date=request.data['end_date']

    local_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(local_path,start_date,end_date)




if __name__ == '__main__':
    app.run(debug=True)