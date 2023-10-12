from flask import Flask, render_template, request, send_file, make_response, jsonify, redirect, url_for, session
from flask_sock import Sock
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import json
import time
import pymongo
from kiteconnect import KiteConnect
import asyncio, asyncssh, sys
import os

app = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 2}

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
# Enter a secret key
app.config["SECRET_KEY"] = "andresdashboard"
# Initialize flask-sqlalchemy extension
db = SQLAlchemy()
 
# LoginManager is needed for our application
# to be able to log in and out users
login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    session_token = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
 
 
# Initialize app with extension
db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()

# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
	return Users.query.get(user_id)


sock = Sock(app)
data = []
flag =0

data1 = []
flag1 = 0

data2 = []
flag2 = 0

data3 = []
flag3 = []



def get_all_users():
    return Users.query.all()


#@app.route('/emergency', methods = ['GET','POST'])
#def emergency_test():
#	ss = get_all_users()
#	for s in ss:
#		print(s.username,s.password)
#	return 00
def remove_user_helper(user_id):
    user = Users.query.filter_by(username=user_id).first()
    #print(user.username)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def change_password_helper(user_id, new_password):
    user = Users.query.filter_by(username=user_id).first()
    #print(111,user,user.username)
    if user:
        print(user.username)
        user.password = new_password  # update password
        db.session.commit()
        return True
    return False

@app.route('/remove-user', methods = ['GET','POST'])
def remove_user():
	if current_user.is_authenticated and current_user.username == "admin" and request.method == "POST":
		if request.json["username"] == "admin":
			return "Cannot delete admin"
		if current_user.username == "admin":
			try:
				rem_res = remove_user_helper(request.json["username"])
				#print(request.json["username"])
				if rem_res == True:
					return "User Removed"
				else:
					return "Check Username"
			except Exception as e:
				print(e)
				return "Check Username"
	else:
		 return redirect(url_for("login"))


@app.route('/change-admin-password', methods = ['GET','POST'])
def change_password():
	if current_user.is_authenticated and current_user.username == "admin" and request.method == "POST":
		try:
			passwd = request.json["password"]
			#print(passwd)
			res_pass = change_password_helper("admin",passwd)
			if res_pass == True:
				return "Password Changed"
			else:
				return "Error changing password"
		except Exception as e:
			print(e)
			return "Error updating password"

	else:
		return redirect(url_for("login"))

@app.route('/admin-dashboard', methods=["GET", "POST"])
def admin_dash():
	if current_user.is_authenticated:
		if current_user.username == "admin":
			users = []
			all_users = get_all_users()
			for user1 in all_users:
				users.append(user1.username)
			return render_template("admin-dash.html",users=users)
		else:
			return redirect(url_for("index"))
	else:
		 return redirect(url_for("login"))

@app.route('/create-new-user-admin', methods=["GET", "POST"])
def register():
	print(current_user.username,request.json['username'])
# If the user made a POST request, create a new user
	if current_user.is_authenticated and current_user.username == "admin" and request.method == "POST":
	#if request.method == "POST":
		try:
			user = Users(username=request.json["username"],
					session_token=os.urandom(32).hex(),
					password=request.json["password"])
		# Add the user to the database
			db.session.add(user)
		# Commit the changes made
			db.session.commit()
		# Once user account created, redirect them
		# to login route (created later on)
			return "User Added"
		#return redirect(url_for("login"))
		except:
			return "Failed, Check username for duplicate"
	# Renders sign_up template if user made a GET request
	return "No permission"
	#return render_template("sign_in.html")



@app.route("/login-user", methods=["GET", "POST"])
def login():
	# If a post request was made, find the user by
	# filtering for the username
	if request.method == "POST":
		user = Users.query.filter_by(
			username=request.form.get("username")).first()
		print(user)
		try:
			if user.password == request.form.get("password"):
			# Use the login_user method to log in the user
				user.session_token = os.urandom(32).hex()
				db.session.commit()
				login_user(user)
				session['session_token'] = user.session_token
				if request.form.get("username") == "admin":
					return redirect(url_for("admin_dash"))
				else:
					return redirect(url_for("index"))
		except:
			pass
	return render_template("sign_in.html")

@app.before_request
def check_valid_login():
    #print("checking")
    user = current_user
    #print(user)
    if user.is_authenticated:
        db_token = user.session_token
        session_token = session.get('session_token')
        if db_token != session_token:
            logout_user()


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

def normalize_query_param(value):
    """
    Given a non-flattened query parameter value,
    and if the value is a list only containing 1 item,
    then the value is flattened.

    :param value: a value from a query parameter
    :return: a normalized query parameter value
    """
    return value if len(value) > 1 else value[0]


def normalize_query(params):
    """
    Converts query parameters from only containing one value for each parameter,
    to include parameters with multiple values as lists.

    :param params: a flask query parameters data structure
    :return: a dict of normalized query parameters
    """
    params_non_flat = params.to_dict(flat=False)
    return {k: normalize_query_param(v) for k, v in params_non_flat.items()}


@app.route('/login')
def redirect_to_zerodha():
   return redirect("https://kite.trade/connect/login?api_key=w60j5yagqsbomli1&v=3", code=302)



def gen_token(rtoken):
  request_token= rtoken
  api_key = "w60j5yagqsbomli1"
  api_secret = "kx8ejzsl3087zm12wjloxv9p51tx79jo"
  kite = KiteConnect(api_key=api_key)
  data = kite.generate_session(request_token, api_secret=api_secret)
  print(data)
  kite.set_access_token(data["access_token"])
  access_token = (data["access_token"])
  try:
     cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
     db = cl.zerodha
     table = db['creds']
     table.update_one({'id':'access_token'},{'$set':{'value':access_token}}, upsert=True)
     return "1"
  except Exception as e:
     return str(e)

@app.route('/',methods=['GET'])
def index():
  while True:
    try:
      if current_user.is_authenticated:
         return render_template("scanner2.html")
      else:
         return redirect(url_for("login"))
    except:
        continue
#@app.route('/1',methods=['GET'])
#def index1():
 #   return render_template("scanner.html")

#@app.route('/2',methods=['GET'])
#def index2():
 #   return render_template("scanner2.html")

#@app.route('/3',methods=['GET'])
#def index3():
 #   return render_template("scanner3.html")


@app.route('/test',methods=['GET'])
def test():
     stocks = []
     cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
     db = cl.zerodha
     table = db['new']
     results = table.find({},{'_id':0})
     for result in results:
         stocks.append(result)
        #print(result)
     return render_template("index1.html",stocks=stocks)


@app.route('/s1',methods = ['GET'])
def s1():
    five = []
    ten = []
    fifteen = []
    cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    db = cl.zerodha
    table = db["five"]
    res_five = table.find({},{'_id':0})
    for res in res_five:
      five.append(res)

    table = db["ten"]
    res_five = table.find({},{'_id':0})
    for res in res_five:
      ten.append(res)

    table = db["fifteen"]
    res_five = table.find({},{'_id':0})
    for res in res_five:
      fifteen.append(res)

    return render_template("s1.html",five=five, ten=ten, fifteen=fifteen)

@app.route('/s2',methods=['GET'])
def s2():
     stocks = []
     stocks_ce = []
     cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
     db = cl.zerodha
     table = db['new']
     results = table.find({},{'_id':0}).sort("change_diff", -1)
     for result in results:
        stocks.append(result)
     results2_ce = table.find({},{'_id':0}).sort("change_diff_ce", -1)
     for result in results2_ce:
        stocks_ce.append(result)
     #results_pe = table.find({},{'_id':0}).sort("total_pe_change", -1)
     #results_ce = table.find({},{'_id':0}).sort("total_ce_change", -1)
     #for result in results_pe:
      #   stocks["pe"].append(result)
     #for result in results_ce:
      #   stocks["ce"].append(result)
     return render_template("s2.html",stocks=stocks, stocks_ce=stocks_ce)


@app.route('/s3',methods=['GET'])
def s3():
     stocks = []
     stocks_ce = []
     cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
     db = cl.zerodha
     table = db['new1']
     results = table.find({},{'_id':0}).sort("change_diff", -1)
     for result in results:
        stocks.append(result)
     results_ce = table.find({},{'_id':0}).sort("change_diff_ce", -1)
     for result in results_ce:
        stocks_ce.append(result)
     #results_pe = table.find({},{'_id':0}).sort("total_pe_change", -1)
     #results_ce = table.find({},{'_id':0}).sort("total_ce_change", -1)
     #for result in results_pe:
      #   stocks["pe"].append(result)
     #for result in results_ce:
      #   stocks["ce"].append(result)
     return render_template("s2.html",stocks=stocks, stocks_ce=stocks_ce)

@app.route('/data/<inst>', methods=['GET'])
def data(inst):
  try:
     inst =  inst.upper()
     data = {}
     ce ={}
     pc = {}
     pe_up = {}
     pe_down = {} 
     cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
     db = cl.zerodha
     price_table = db['priceList']
     price_result = price_table.find_one({"name":inst})
     cmp = price_result['CMP']
     print(cmp)
     final_list = {"MONTHLY":[],"WEEKLY":[],"CMP":cmp}
     final_data = {"MONTHLY":{},"WEEKLY":{}}
     final_dict = {"MONTHLY":{"CE":[],"PE":[]},"WEEKLY":{"CE":[],"PE":[]}}
     mw = ['MONTHLY','WEEKLY']
     for m in mw:
       tmp_dict = {m:{"CE":[],"PE":[]}}
       table = db[inst+m]
       result_ce = list(table.find({"side":"CE"},{'_id': 0}))
       result_pe = list(table.find({"side":"PE"},{'_id': 0}))
       try:
           maxCE = max(result_ce, key=lambda x:x['oi'])
           maxPE = max(result_pe, key=lambda x:x['oi'])
       except :
            continue
       print(maxPE['strike'],maxCE['strike'])
       ce_up = sorted(result_ce, key=lambda d: d['strike'])
       pe_up = sorted(result_pe, key=lambda d: d['strike'])
       c_above = []
       c_below = []
       p_above= []
       p_below = []
       for c in ce_up:
          if (c['strike']) < maxCE['strike']:
            c_above.append(c)
          elif (c['strike']) >= maxCE['strike']:
            c_below.append(c)
       for c in pe_up:
         if (c['strike']) < maxPE['strike']:
            p_above.append(c)
         elif (c['strike']) >= maxPE['strike']:
            p_below.append(c)
       for p in c_above[-15:]:
           tmp_dict[m]["CE"].append([p['strike'],p['oi']])
       for p in c_below[:15]:
           tmp_dict[m]["CE"].append([p['strike'],p['oi']])
       for p in p_above[-15:]:
           tmp_dict[m]["PE"].append([p['strike'],p['oi']])
       for p in p_below[:15]:
           tmp_dict[m]["PE"].append([p['strike'],p['oi']])
       strikes = set()
       for lst in tmp_dict[m]['CE']:
           strikes.add(lst[0])
       for lst in tmp_dict[m]['PE']:
           strikes.add(lst[0])
       strikes = sorted(strikes,reverse=True)
       for strike in strikes:
           final_data[m][strike] = {}
       for rce in result_ce:
           if rce['strike'] in strikes :
              final_data[m][rce['strike']]['CE'] = rce['oi']
              final_data[m][rce['strike']]['CE_CHANGE'] = int(rce['oi']) - int(rce['poi'])
       for rpe in result_pe:
           if rpe['strike'] in strikes :
              final_data[m][rpe['strike']]['PE'] = rpe['oi']
              final_data[m][rpe['strike']]['PE_CHANGE'] =  int(rpe['oi']) - int(rpe['poi'])
       #print(final_dict)
       #data[m] = results
       for val in final_data[m]:
         final_list[m].append([val,final_data[m][val]['CE'],final_data[m][val]['PE'],final_data[m][val]['CE_CHANGE'],final_data[m][val]['PE_CHANGE']])
     return render_template("charts.html",expiry=final_list,chart=json.dumps(final_data))
  except Exception as e:
     return str(e)


@app.route('/rqtoken', methods = ['GET'])
def token():
    try:
     req_token = request.args.get('request_token')
     print(req_token)
     res = gen_token(req_token)
     if res == "1":
      return redirect("https://lokmaarenko.com", code=302)
    except Exception as e:
     return str(e)

@app.route('/newscanner', methods=['GET','POST'])
def index_strategy():
 while True:
  try:
    if current_user.is_authenticated:
     lst = []
     lst2 = []
     cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
     db = cl.zerodha_index
     table = db['banknifty_strong']
     results = table.find({},{'_id':0})
     for res in results:
       lst2.append(res)
     table = db['nifty_strong']
     results = table.find({},{'_id':0})
     for res in results:
       lst.append(res)
     nifty = []
     nifty.append(lst[4])
     nifty.append(lst[3])
     nifty.append(lst[2])
     nifty.append(lst[1])
     nifty.append(lst[0])
    # nifty.append(lst[4])
    # nifty.append(lst[5])
    # nifty.append(lst[6])
    # nifty.append(lst[7])
     bnifty = []
     bnifty.append(lst2[4])
     bnifty.append(lst2[3])
     bnifty.append(lst2[2])
     bnifty.append(lst2[1])
     bnifty.append(lst2[0])
     #bnifty.append(lst2[4])
     #bnifty.append(lst2[5])
     #bnifty.append(lst2[6])
     #bnifty.append(lst2[7])
     return render_template("indexstrat.html",stocks_nifty=nifty, stocks_bnf=bnifty)
    else:
     return redirect(url_for("login"))
  except:
     
     continue
  # return render_template("error.html")
@app.route('/list', methods=['GET'])
def list1():
    lst = []
    cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    db = cl.zerodha
    table  = db['alerts'].find()
    for tab in table:
      del tab['_id']
      lst.append(tab)
    return make_response(jsonify(lst),200)

@app.route('/list1', methods=['GET'])
def list11():
    lst = []
    cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    db = cl.zerodha
    table  = db['alerts1'].find()
    for tab in table:
      del tab['_id']
      lst.append(tab)
    return make_response(jsonify(lst),200)


@app.route('/list2', methods=['GET'])
def list12():
    lst = []
    cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    db = cl.zerodha
    table  = db['alerts2'].find()
    for tab in table:
      del tab['_id']
      lst.append(tab)
    return make_response(jsonify(lst),200)

@app.route('/list3', methods=['GET'])
def list13():
    lst = []
    cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    db = cl.zerodha
    table  = db['alerts3'].find()
    for tab in table:
      del tab['_id']
      lst.append(tab)
    return make_response(jsonify(lst),200)

@app.route('/list-file', methods=['GET'])
def listFile():
    lst = []
    cl = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
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

@app.route('/alert1',methods=['POST'])
def alert1():
    global data1
    global flag1
    tdata = request.get_json(force=True)
    if tdata not in data1:
     data1.append(tdata)
     flag1 = 1
     #print(data)
     return '1'
    else:
     return '0'

@app.route('/alert2',methods=['POST'])
def alert2():
    global data2
    global flag2
    tdata = request.get_json(force=True)
    if tdata not in data2:
     data2.append(tdata)
     flag2 = 1
     #print(data)
     return '1'
    else:
     return '0'

@app.route('/alert3',methods=['POST'])
def alert3():
    global data3
    global flag3
    tdata = request.get_json(force=True)
    if tdata not in data3:
     data3.append(tdata)
     flag3 = 1
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
