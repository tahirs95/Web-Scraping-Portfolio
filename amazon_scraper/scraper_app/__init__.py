from flask import Flask, render_template, request
from .functions import process_data, scrape

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def index():
    data = {'None': 'None'}
    data_available = False
    if request.form:
        asin = request.form['search']
        if asin:
            url = "https://amazon.com/dp/{}".format(asin)
            data = scrape(url)
            data = process_data(data)
            data_available = True

    return render_template('index.html', data_available=data_available, data=data)
