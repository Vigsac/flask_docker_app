from flask import Flask, render_template, request, redirect, url_for
from models import MobileNet
import os
import json
from math import floor
from collections import OrderedDict

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['static'] = 'static'

model = MobileNet()

@app.route('/')
def index():
    if app.config['sample']:
        return redirect(url_for('success'))
    else:
        return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/infer', methods=['POST','GET'])
def success():
    result=OrderedDict()

    if request.method == 'POST':
        myfiles = request.files.getlist('myfiles')
        for uploaded_file in myfiles:
            if uploaded_file.filename != '':
                
                saveLocation = os.path.join(app.config['static'],app.config['UPLOAD_FOLDER'],uploaded_file.filename)
                uploaded_file.save(saveLocation)
                inference, confidence = model.infer(saveLocation)
                # make a percentage with 2 decimal points
                confidence = floor(confidence * 10000) / 100
                # delete file after making an inference
                # os.remove(saveLocation)
                result[uploaded_file.filename] = [inference, confidence]
    else:
        myfiles = [app.config['sample']]
        inference, confidence = model.infer(f'static/uploads/{myfiles[0]}')
        confidence = floor(confidence * 10000) / 100
        result[myfiles[0]] = [inference, confidence]
        
    # print(result)
    
    fname_results = os.path.join(app.config['static'],'predictions.json')
    if not os.path.isfile(fname_results):
        feeds={}
        if not app.config['sample']:
            with open(fname_results, mode='w') as f:
                f.write(json.dumps(result, indent=2))
    else:
        with open(fname_results) as feedsjson:
            feeds = json.load(feedsjson,object_pairs_hook=OrderedDict)
        if not app.config['sample']:
            for k in result.keys():
                if k in feeds.keys():
                    feeds.pop(k)
            feeds.update(result)
            while len(feeds) > 5:
                feeds.popitem(last=False)
            with open(fname_results, mode='w') as f:
                f.write(json.dumps(feeds, indent=2))
    app.config['sample'] = None
    # respond with the inference
    return render_template('inference.html', result=result,prev_results=enumerate(reversed(feeds.items())) )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", help="sample image file ( shoule be in static/uploads/) ",default=None)
    args = parser.parse_args()
    app.config['flag']=True
    if args.sample:
        app.config['sample']=args.sample
    else:
        app.config['sample']='sample_image.jpg'

    # print(args.sample)
    # app.run(debug=True)
    app.debug = True
    port = int(os.environ.get("PORT", 80))
    app.run(host='0.0.0.0', port=port, debug=True)
    