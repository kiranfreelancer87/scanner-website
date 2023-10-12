from flask import Flask, render_template, request, send_file, make_response, jsonify, redirect
from flask_sock import Sock
import json
import time
import pymongo
from kiteconnect import KiteConnect
import asyncio, asyncssh, sys
from fw import run_client

app = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 2}
sock = Sock(app)
data = []
flag =0

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


#@app.route('/login')
#def redirect_to_zerodha():
 #  return redirect("https://kite.trade/connect/login?api_key=", code=302)

@app.route('/firewall',methods=['GET'])
#@basicAuth.login_required
def firewall():
   return render_template("firewall.html")

@app.route('/command', methods=['GET'])
def send_command():
   query_params = normalize_query(request.args)
   #print(query_params)
   try:
     asyncio.run(run_client('10.91.127.1',query_params['unm'],query_params['upw']))
   except (OSError, asyncssh.Error) as exc:
     print(str(exc))
     sys.exit('SSH connection failed: ' + str(exc))
   return str(exc)

@app.route('/link/<evid>')
def link(evid):
    return render_template("link.html", event=evid)

@app.route('/live/<evid>')
def livetv(evid):
    return render_template("live.html", event=evid)

@app.route('/live2/<evid>')
def livetv2(evid):
    return render_template("live2.html", event=evid)

@app.route('/live3/<evid>')
def livetv3(evid):
    return render_template("live3.html", event=evid)

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
    return render_template("scanner.html")

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
