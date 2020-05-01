# -*- coding: UTF-8 -*-

from flask import Flask
from flask import render_template
from flask import Flask, flash, render_template, request, redirect, jsonify
from werkzeug.utils import secure_filename
import os
from ibnr_cal import *


import locale
import time
locale.setlocale(locale.LC_CTYPE, 'chinese')

UPLOAD_FOLDER = '.\\tmp'
ALLOWED_EXTENSIONS = set(['xlsx', 'csv', 'xls'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True
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
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            returndata = read_data(path)
            return jsonify(returndata)
    return ''


@app.route('/caltri', methods=['GET', 'POST'])
def caltri():
    print('caltri')
    import json
    data = json.loads(request.get_data())
    filename = data['filename']
    date_start = data['date_start']
    date_end = data['date_end']

    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    tables = cal_tri(local_path, date_start, date_end)
    ret = ''
    for t in tables:
        ret += t
    return ret


@app.route('/calfactor', methods=['GET', 'POST'])
def calfactor():
    print('calfactor')
    import json
    data = json.loads(request.get_data())
    filename = data['filename']
    date_start = data['date_start']
    date_end = data['date_end']
    cfactor_month_nums = data['cfactor_month_nums']
    ffactor_month_nums = data['ffactor_month_nums']
    cfactor_month_nume = data['cfactor_month_nume']
    ffactor_month_nume = data['ffactor_month_nume']
    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    tables = cal_factor(local_path, date_start, date_end, cfactor_month_nums, cfactor_month_nume,ffactor_month_nums, ffactor_month_nume)
    ret = ''
    for t in tables:
        ret += t
    return ret


@app.route('/calres', methods=['GET', 'POST'])
def calres():
    print('calres')
    import json
    data = json.loads(request.get_data())
    filename = data['filename']
    date_start = data['date_start']
    date_end = data['date_end']
    cfactor_adj = data['cfactor_adj']
    ffactor_adj = data['ffactor_adj']
    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    tables = cal_res(local_path, date_start, date_end, cfactor_adj, ffactor_adj)

    ret = ''
    for t in tables:
        ret += t
    return ret


@app.route('/method2', methods=['GET', 'POST'])
def method2():
    print('method2')
    import json
    data = json.loads(request.get_data())
    filename = data['filename']
    date_start = data['date_start']
    date_end = data['date_end']
    af_month_num = data['af_month_num']

    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    tables = method_2(local_path, date_start, date_end, af_month_num)

    ret = ''
    for t in tables:
        ret += t
    return ret


@app.route('/method2res', methods=['GET', 'POST'])
def method2res():
    print('method2res')
    import json
    data = json.loads(request.get_data())
    filename = data['filename']
    date_start = data['date_start']
    date_end = data['date_end']
    average_fee_adj = data['average_fee_adj']
    cfactor_adj = data['cfactor_adj']
    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    tables = method_2_res(local_path, date_start, date_end, cfactor_adj, average_fee_adj)

    ret = ''
    for t in tables:
        ret += t
    return ret


if __name__ == '__main__':
    app.run(debug=True)
