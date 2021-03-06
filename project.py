from flask import Flask, render_template,\
    request, redirect, jsonify, url_for, flash
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, University, College, Base
import random
import string

app = Flask(__name__)

engine = create_engine('sqlite:///universities.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "universty"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None \
            and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_id = getUserId(data["email"])
    if not user_id:
        user_id = createNewUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: ' \
              '150px;-webkit-border-radius: ' \
              '150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke '
                                            'token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createNewUser(login_session):
    user = User(name=login_session['username'],
                email=login_session['email'], picture=login_session['picture'])
    session.add(user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


@app.route('/universty/<int:id>/college/json')
def universty_collegies_json(id):
    collegies = session.query(College).filter_by(university_id=id).all()
    return jsonify(Colleges=[i.serialize for i in collegies])


@app.route('/universty/json')
def homepagejson():
    universty = session.query(University).all()

    return jsonify(universies=[i.serialize for i in universty])


@app.route('/universty/colleges/items/<int:college_id>/json')
def show_college_detail_json(college_id):
    collegie = session.query(College).filter_by(id=college_id).one()
    return jsonify(collegie=collegie.serialize)


@app.route('/universty/')
def homepage():
    universties = session.query(University).all()
    if 'username' not in login_session:
        return render_template('homepagepublic.html', universty=universties)
    else:
        return render_template('homepage.html', universty=universties)


@app.route('/universty/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/universty/<int:id>/college', methods=['GET', 'POST'])
def universty_collegies(id):
    universty = session.query(University).filter_by(id=id).one()
    collegies = session.query(College).filter_by(university_id=id).all()
    return render_template('college_of_universty.html',
                           universty=universty, college=collegies)


@app.route('/universty/addnewcollege', methods=['GET', 'POST'])
def add_new_college():
    if 'username' not in login_session:
        return redirect('/login')
    universties = session.query(University).all()
    if request.method == 'POST':
        college = College(name=request.form['name'],
                          department=request.form['department'],
                          university_id=request.form["universtyid"],
                          user_id=login_session['user_id'])
        flash('New college %s Successfully Created' % college.name)
        session.add(college)
        session.commit()
        return redirect(url_for('homepage'))

    return render_template('newcollege.html', universty=universties)


@app.route('/universty/<int:uni_id>/colleges/items/<int:college_id>')
def show_college_detail(college_id, uni_id):
    universty = session.query(University).filter_by(id=uni_id).one()
    college = session.query(College).filter_by(id=college_id).one()
    creator = getUserInfo(college.user_id)
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('collegedetailpublic.html',
                               university=universty, college=college)
    else:
        return render_template('collegedetail.html',
                               university=universty, college=college)


@app.route('/universty/college/<int:uni_id>/<int:college_id>/edit',
           methods=['GET', 'POST'])
def edit_college(uni_id, college_id):
    college = session.query(College).filter_by(id=college_id).one()
    universties = session.query(University).all()
    universty = session.query(University).filter_by(id=uni_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if college.user_id != login_session['user_id']:
        return "<script>function alertfun() {alert('Error You are not " \
               "authorized to edit this college');}" \
               "</script><body onload='alertfun()''>"
    if request.method == 'POST':
        if request.form['name']:
            college.name = request.form['name']
        if request.form['department']:
            college.department = request.form['department']
        if request.form['universtyid']:
            college.university_id = request.form['universtyid']
        session.add(college)
        session.commit()
        flash('%s Successfully updated' % college.name)
        return redirect(url_for('homepage'))
    else:
        return render_template('editCollege.html',
                               universty=universties,
                               college=college,
                               universty_id=universty.id)


@app.route('/universty/<int:uni_id>/<int:college_id>/delete',
           methods=['GET', 'POST'])
def delete_college(uni_id, college_id):
    collegewantdelete = session.query(College).filter_by(id=college_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if collegewantdelete.user_id != login_session['user_id']:
        return "<script>function alertfun() {alert('Error You are not " \
               "authorized to delete this college');}</script>" \
               "<body onload='alertfun()''>"

    if request.method == 'POST':
        if 'submit' in request.form:
            session.delete(collegewantdelete)
            flash('%s Successfully Deleted' % collegewantdelete.name)
            session.commit()
            return redirect(url_for('homepage'))
        else:
            return redirect(url_for('homepage'))
    else:
        return render_template('deletecollege.html',
                               college=collegewantdelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
