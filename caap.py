from flask import Flask, render_template, request, send_file, make_response, jsonify, redirect
#from flask_sock import Sock
import json
import time
import att
from helium import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 2}
data = []
flag =0




users = [["surawadeesoo1@gmail.com","Bangkok101!"],["iansooamazonuk@gmail.com","Lifeisgreat5!"]]
drives = {}

for user in users:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    driver = start_chrome(options= chrome_options)
    print(driver,user[0],user[1])
    att.login_site(driver,user[0],user[1])
    drives[user[0]] = driver
print(drives)

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

@app.route('/at',methods=['GET'])
#@basicAuth.login_required
def att():
   print(1)
   quantity = "0.5"
   trade_type = "Buy" 
   item = "GBP/AUD - Rolling Spot"
   trail = "5"
   try:
     print(2)
     for drive in drives:
        t = Thread(target=place_td, args=(drives[drive],item,quantity, trade_type, trail)).start()
     return str(0)
   except Exception as e:
    print(str(e))
    return str(e)
   

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
