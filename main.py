from flask import Flask, render_template, redirect, url_for, request, session
from google.cloud import datastore
import datetime

datastore_client = datastore.Client()

def store_user(loginuser, password, displayname):#ok
    entity = datastore.Entity(key=datastore_client.key('user'))
    entity.update({
        'loginuser': loginuser,
        'password': password,
        'displayname': displayname
    })

    datastore_client.put(entity)

app=Flask(__name__)
app.secret_key = 'jagioeheiII3SJ695i3i5ofi'



def find_by_loginuser(loginuser):
    if loginuser:
        query = datastore_client.query(kind='user')
        query.add_filter('loginuser','=',loginuser)
        user = query.fetch()#取得
        return user
    return None

def store_chat(displayname, dt, chat):#要点検
    entity = datastore.Entity(key=datastore_client.key('chat'))
    entity.update({
        'displayname': displayname,
        'timestamp': dt, 
        'contents': chat
    })

    datastore_client.put(entity)

def fetch_chat(limit):#要点検
    query = datastore_client.query(kind='chat')
    query.order = ['-timestamp']

    chats = query.fetch(limit=limit)

    return chats

@app.route('/<name>')#ok
def main(name):
    templname=name+'.htm'
    loginuser=session.get('loginuser',None)
    return render_template(templname,path=name,loginuser=loginuser)

@app.route('/')#ok
def root():
    #return redirect(url_for('main',name='index'))
    loginuser = session.get('loginuser',None)
    user = find_by_loginuser(loginuser)
    return render_template('root.htm', user=user)

@app.route('/login',methods=['GET'])#ok
def login_get():
    loginuser = session.get('loginuser',None)
    user = find_by_loginuser(loginuser)
    return render_template('login_get.htm', user=user)

@app.route('/login',methods=['POST'])#no
def login_post():
    account = request.form['account']
    password = request.form['password']
    
    user = find_by_loginuser(account)
    if user:
        #if user['password'] == password:
            session['loginuser'] = account
            return redirect(url_for('root'))
    
    return render_template('login_post_error.htm')

@app.route('/logout')#ok
def logout():
    if 'loginuser' in session:
        session.pop('loginuser')
    return f'''logged out.<br>return <a href = "{ url_for('main',name='index')}">home</a>.'''

@app.route('/members')#ok
def members():
    query = datastore_client.query(kind='user')
    users = query.fetch()
    return render_template('members.htm', users=users)

@app.route('/apply', methods=['GET'])#ok
def apply_get():
    loginuser = session.get('loginuser', None)
    user = find_by_loginuser(loginuser)
    return render_template('apply_get.htm', user=user)

@app.route('/apply', methods=['POST'])#no
def apply_post():
    account = request.form['account']
    password = request.form['password']
    displayname = request.form['displayname']
    
    #test if 'account' is existing
    user = find_by_loginuser(account)
    user_list = list(user)
    if len(user_list) == 1:
        return render_template('apply_post_error.htm',user=user)
    #new user
    store_user(account, password, displayname)
    session['loginuser'] = account
    return redirect(url_for('root'))

#これより下は要点検

@app.route('/chat', methods=['GET'])
def chat_get():
    loginuser = session.get('loginuser', None)
    chats = fetch_chat(100)
    return render_template('chat_get.htm', chats=chats, loginuser=loginuser)

@app.route('/chat', methods=['POST'])
def chat_post():
    chat = request.form['chat']

    loginuser = session.get('loginuser', None)
    user = find_by_loginuser(loginuser)
    dt = datetime.datetime.now()
    dt_str = dt.strftime('%Y/%m/%d %H:%M:%S')
    
    user_list = list(user)
    if len(user_list) == 1:
        store_chat(displayname=loginuser, dt=dt_str, chat=chat)
        chats = fetch_chat(100)
        return render_template('chat_get.htm', chats=chats, loginuser=loginuser)
    
    store_chat(dt=dt_str, chat=chat)

    chats = fetch_chat(100)
    return render_template('chat_get.htm', chats=chats, loginuser=loginuser)

if __name__=='__main__':
    app.run(debug=True)
