from flask import Flask,render_template, request, session, Response, redirect
from database import connector
from model import entities
import json
import datetime
import time
from operator import itemgetter, attrgetter

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<content>')
def static_content(content):
    return render_template(content)


@app.route('/users', methods = ['GET'])
def get_users():
    session = db.getSession(engine)
    dbResponse = session.query(entities.User)
    data = []
    for user in dbResponse:
        data.append(user)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

#
@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')
#

@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])
    user = entities.User(
        username=c['username'],
        name=c['name'],
        fullname=c['fullname'],
        password=c['password'],
        country=c['country']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'Created User'

@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'Updated User'

@app.route('/users', methods = ['DELETE'])
def delete_users():
    id = request.form['key']
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    return "Deleted User"



@app.route('/messages', methods = ['GET'])
def get_messages():
    session = db.getSession(engine)
    dbResponse = session.query(entities.Message)
    data = []
    for message in dbResponse:
        data.append(message)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/messages', methods = ['POST'])
def create_message():
    c =  json.loads(request.form['values'])
    session = db.getSession(engine)
    content = c['content']
    user_from_id = c['user_from_id']
    user_to_id = c['user_to_id']

    message = entities.Message(
        content=content,
        user_from_id=user_from_id,
        user_to_id=user_to_id,
    )
    session.add(message)
    session.commit()
    return 'Created Message'

@app.route('/messages', methods = ['PUT'])
def update_message():
    session = db.getSession(engine)
    id = request.form['key']
    message = session.query(entities.Message).filter(entities.Message.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(message, key, c[key])
    session.add(message)
    session.commit()
    return 'Updated Message'

@app.route('/messages', methods = ['DELETE'])
def delete_message():
    id = request.form['key']
    session = db.getSession(engine)
    messages = session.query(entities.Message).filter(entities.Message.id == id)
    for message in messages:
        session.delete(message)
    session.commit()
    return "Deleted Message"


@app.route('/messages/<user_from_id>/<user_to_id>', methods = ['GET'])
def get_message(user_from_id, user_to_id ):
    db_session = db.getSession(engine)
    messages = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_from_id).filter(
        entities.Message.user_to_id == user_to_id
    )
    data = []
    for message in messages:
        data.append(message)
    messages = db_session.query(entities.Message).filter(
        entities.Message.user_from_id == user_to_id).filter(
        entities.Message.user_to_id == user_from_id
    )
    for message in messages:
        data.append(message)
    data = sorted(data, key=attrgetter('sent_on'), reverse=False)
    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype='application/json')

@app.route('/sendmessage', methods = ['POST'])
def send_message():
    message = json.loads(request.data)
    content = message['content']
    user_from_id = message['user_from_id']
    user_to_id = message['user_to_id']
    session = db.getSession(engine)
    add = entities.Message(
        content=content,
        user_from_id=user_from_id,
        user_to_id=user_to_id,
    )
    session.add(add)
    session.commit()
    return 'Message Sent'


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    #Get data from request (name from html form)
        #username = request.form['username']
        #password = request.form['password']

    message=json.loads(request.data)
    username=message['username']
    password=message['password']

    #look in databes
    db_session = db.getSession(engine)

    #anyone has the username and password requested?

        #users = db_session.query(entities.User)
        #for user in users:
        #    if user.username==username and user.password==password:
        #        return render_template("success.html")
        #return render_template("fail.html")

    try:
        user = db_session.query(entities.User
            ).filter(entities.User.username==username
            ).filter(entities.User.password==password
            ).one()
        session['logged_user']=user.id
        message = {'message':'Authorized'}
        return Response(message, status=200, mimetype='application/json')
    except Exception:
        message = {'message':'Unauthorized'}
        return Response(message, status=401, mimetype='application/json')

@app.route('/current', methods = ['GET'])
def current_user():
    db_session = db.getSession(engine)
    user = db_session.query(entities.User).filter(
        entities.User.id==session['logged_user']).first()
    return Response(json.dumps(user,
                               cls=connector.AlchemyEncoder),
                    mimetype='application/json')

@app.route('/logout', methods = ['GET'])
def logout():
    session.clear()
    return render_template('index.html')

@app.route('/createUser', methods = ["POST"])
def createUser():
    message = json.loads(request.data)
    user = entities.User(
    name=message['name'],
    fullname=message['fullname'],
    username=message['username'],
    password= message['password'],
    country= message['country']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    message = {'message': 'User Created'}
    return Response(message, status=200, mimetype='application/json')




if __name__ == '__main__':
    app.secret_key = ".."
    app.run(port=8080, threaded=True, host=('127.0.0.1'))
