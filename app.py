from flask import Flask, render_template;

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/menu")
def menu():
    return render_template('menu.html')

@app.route("/menu/pasta")
def pasta_menu():
    return render_template('menu_pasta.html')

@app.route("/menu/drinks")
def drinks_menu():
    return render_template('menu_drinks.html')

@app.route('/register')
def register():
    return render_template('register_form.html')

@app.route('/order')
def order():
    return render_template('order.html')