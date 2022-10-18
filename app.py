from flask import Flask, render_template;

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register_form.html')