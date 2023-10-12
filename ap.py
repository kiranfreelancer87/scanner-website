from flask import Flask, render_template, request, send_file,jsonify, make_response, redirect
from flask_sock import Sock
import pymongo
import time
import json
from kiteconnect import KiteConnect
app = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 2}
sock = Sock(app)
data = []
flag =0


def gen_token(rtoken):
  return "1"
  request_token= rtoken
  api_key = "w60j5yagqsbomli1"
  api_secret = "kx8ejzsl3087zm12wjloxv9p51tx79jo"
  kite = KiteConnect(api_key=api_key)
  data = kite.generate_session(request_token, api_secret=api_secret)
  kite.set_access_token(data["access_token"])
  access_token = (data["access_token"])
  try:
     cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/")
     db = cl.zerodha
     table = db['creds']
     table.update_one({'id':'access_token'},{'$set':{'value':access_token}}, upsert=True)
     return '1'
  except Exception as e:
     return str(e)

@app.route('/',methods=['GET'])
def index():
    return render_template("screener.html")

@app.route('/rqtoken', methods = ['GET'])
def token():
    try:
     req_token = request.args.get('request_token')
     res = gen_token(req_token)
     if res == "1":
      return redirect("http://remote-vpn.com", code=302)
    except Exception as e:
     return str(e)
@app.route('/test',methods=['GET'])
def index1():
    return render_template("index1.html")

@app.route('/list', methods=['GET'])
def list1():
    lst = []
    cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/")
    db = cl.zerodha
    table  = db['alerts'].find()
    for tab in table:
      del tab['_id']
      lst.append(tab)
    return make_response(jsonify(lst),200)
@app.route('/list-file', methods=['GET'])
def listFile():
    lst = []
    cl = pymongo.MongoClient("mongodb://10.122.0.3:27017/")
    db = cl.zerodha
    table  = db['alerts'].find()
    with open("alerts.txt", "w") as fp:
     for tab in table:
       del tab['_id']
       fp.write(str(tab)+"\n")
       #lst.append(tab)
    return send_file('/home/app/alerts.txt',as_attachment=True) 

@app.route('/alert',methods=['POST'])
def alert():
    global data
    global flag
    tdata = request.get_json(force=True)
    if tdata not in data:
     data.append(tdata)
     flag = 1
     #print(data)
     return '1'
    else:
     return '0'

@sock.route('/echo')
def echo(sock):
    global data
    global flag
    while True:
         #time.sleep(.5)
         if flag == 1:
            print(data)
            for dat in data:
              sock.send(dat)
            flag = 0
            data = []


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
