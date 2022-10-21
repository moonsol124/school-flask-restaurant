import json
from flask import Flask,jsonify,request, redirect, render_template, url_for, session
import pymongo
import bcrypt
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from datetime import datetime, timedelta, timezone, date
import uuid

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)
CORS(app)
app.secret_key = 'testing'
client = pymongo.MongoClient('mongodb+srv://school:school@cluster0.p9yyvaf.mongodb.net/?retryWrites=true&w=majority')
db = client.get_database('restaurant')
users = db.users
orders = db.orders

@app.route("/")
def index():
    allOrders = []
    user = 'Stranger'
    if "email" in session:
        print ("user loggined")
        user = session["email"]
    else:
        user = 'Stranger'

    for order in orders.find():
        allOrders.insert(0, order)

    return render_template('index.html', user=user, orders=allOrders)

@app.route('/order', methods=['POST', 'GET'])
def order():
    if request.method == "POST":
        data = request.json
        order = data['order']
        totalPrice = 0
        for i in range(0, len(order)):
            totalPrice = totalPrice+int(order[i]['price'])
        now = datetime.now()
        time = str(now.year)+'-'+str(now.month)+'-'+str(now.day)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second)
        # print(order, totalPrice)
        id = uuid.uuid1().hex
        order_input = {
            'order': order,
            'total_price': totalPrice,
            'order_time' : time,
            '_id': id,
        }
        orders.insert_one(order_input)
        order_found = orders.find_one({'_id': id})
        response = {
            'order_number': order_found['_id']
        }
        return jsonify(response), 200


@app.route('/oven', methods=['POST', 'GET'])
def oven_get():
    data = request.json
    return render_template('oven.html')

@app.route("/register", methods=['post', 'get'])
@cross_origin()
# @jwt_required()
def mongo_login():
    data = request.json
    print(data)
    userFirstName = data['userFirstName']
    userSecondName = data['userSecondName']
    userEmail = data['userEmail']
    userFirstPassword = data['userFirstPassword']
    userSecondPassword = data['userSecondPassword']

    if request.method == "POST":
        email_found = users.find_one({"email": userEmail})
        if email_found:
            response = {
                'message': 'This email already exists in database',
                'status': 'failed'
            }
            return jsonify(response), 401

        elif userFirstPassword != userSecondPassword:
            response = {
                'message': 'Passwords do not match',
                'status': 'failed'
            }
            return jsonify(response), 401

        else:
            hashed = bcrypt.hashpw(userSecondPassword.encode('utf-8'), bcrypt.gensalt())
            user_input = {'first_name': userFirstName, 
            'second_name': userSecondName,
            'email': userEmail,
            'password': hashed}
            users.insert_one(user_input)

            response = {
                'message': 'Account successfully created',
                'status': 'success',
            }
            return jsonify(response), 200

@app.route("/logout", methods=["POST"])
@cross_origin()
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

@app.route("/login", methods=["POST", "GET"])
@cross_origin()
def login():
    data = request.json
    print(data)
    email = data['userEmail']
    password = data['userPassword']

    if request.method == "POST":
        email = email
        password = password
       
        # login success / password matches
        email_found = users.find_one({"email": email})
        if email_found:
            passwordcheck = email_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                access_token = create_access_token(identity=email)
                response = {"access_token":access_token, "user": email_found['first_name'], 'message': 'login success', 'status': 'success'}
                return jsonify(response), 200
            else:
                response = {'message': 'passwords do not match', 'status': 'failed'}
                return jsonify(response), 401
        # password doesn't match
        else:
            return jsonify({
                'message': 'email not found'
            }), 401
