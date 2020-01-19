from flask import Flask, redirect, url_for, render_template,request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index3.html')

@app.route('/index2', methods= ['POST','GET'])
def index2():
        os.system("dir")
        os.system('python Air_Drums_Final.py')
        return render_template('index3.html')
   
if __name__ == "__main__":
    app.run(host='0.0.0.0')

