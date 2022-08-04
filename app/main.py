# Run by typing python3 main.py

# **IMPORTANT:** only collaborators on the project where you run
# this can access this web server!

"""
    Bonus points if you want to have internship at AI Camp
    1. How can we save what user built? And if we can save them, like allow them to publish, can we load the saved results back on the home page? 
    2. Can you add a button for each generated item at the frontend to just allow that item to be added to the story that the user is building? 
    3. What other features you'd like to develop to help AI write better with a user? 
    4. How to speed up the model run? Quantize the model? Using a GPU to run the model? 
"""

# import basics
import os
import requests
import json


# import stuff for our web server
from flask import Flask, request, redirect, url_for, render_template, session
from utils import get_base_url
# import stuff for our models
from aitextgen import aitextgen

# load up a model from memory. Note you may not need all of these options.
ai = aitextgen(model_folder="model/", to_gpu=False)


# setup the webserver
# port may need to be changed if there are multiple flask servers running on same server
port = 62745
base_url = get_base_url(port)


# if the base url is not empty, then the server is running in development, and we need to specify the static folder so that the static files are served
if base_url == '/':
    app = Flask(__name__)
else:
    app = Flask(__name__, static_url_path=base_url+'static')

app.secret_key = os.urandom(64)

# set up the routes and logic for the webserver


@app.route(f'{base_url}')
def home():
    return render_template('index.html', generated=None)


@app.route(f'{base_url}', methods=['POST'])
def home_post():
    return redirect(url_for('results'))


@app.route(f'{base_url}/results/')
def results():
    if 'data' in session:
        data = session['data']
        return render_template('Write-your-story-with-AI.html', generated=data)
    else:
        return render_template('Write-your-story-with-AI.html', generated=None)

@app.route(f'{base_url}/model/')
def model():
    if 'data' in session:
        data = session['data']
        return render_template('model.html', generated=data)
    else:
        return render_template('model.html', generated=None)

@app.route(f'{base_url}/model2/')
def model2():
    if 'data' in session:
        data = session['data']
        return render_template('model-lyric.html', generated=data)
    else:
        return render_template('model-lyric.html', generated=None)

@app.route(f'{base_url}/model/index/')
def index():
    home()

@app.route(f'{base_url}/model2/generate_text/', methods=["POST"])
def generate_text():
    """
    view function that will return json response for generated text.
    """
    prompt = request.form['prompt']
    if prompt == 'up up down down left right left right b a start':
        return redirect(url_for('model'))
    headers = {
    # Already added when you pass json= but not when you pass data=
    # 'Content-Type': 'application/json',
    'Authorization': 'Bearer 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',
    }
    json_data = {
        'model': 'davinci:ft-personal-2022-07-28-19-11-11',
        'prompt': prompt,
        'temperature': 0.2,
        'max_tokens': 9,
        'echo' : True,
    }
    response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=json_data)
    asT = response.text
    res = json.loads(asT)
    data = {'generated_ls': response.json()}
    session['data'] = res["choices"][0]["text"]
    return redirect(url_for('model2'))

@app.route(f'{base_url}/gpt2_text/', methods=["POST"])
def gpt2_text():
    """
    view function that will return json response for generated text. 
    """
    prompt2 = request.form['prompt']
    if prompt2 is not None:
        generated2 = ai.generate(
            n=1,
            batch_size=3,
            prompt=str(prompt2),
            max_length=30,
            temperature=0.9,
            return_as_list=True
        )
    data = {'generated_ls': generated2}
    session['data'] = generated2[0]
    return redirect(url_for('model2'))

# define additional routes here
# for example:
# @app.route(f'{base_url}/team_members')
# def team_members():
#     return render_template('team_members.html') # would need to actually make this page


if __name__ == '__main__':
    # IMPORTANT: change url to the site where you are editing this file.
    website_url = 'cocalc10.ai-camp.dev'

    print(f'Try to open\n\n    https://{website_url}' + base_url + '\n\n')
    app.run(host='0.0.0.0', port=port, debug=True)
