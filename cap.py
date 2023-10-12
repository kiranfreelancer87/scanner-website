from flask import Flask, render_template, request, send_file, make_response, jsonify, redirect
from flask_sock import Sock
import json
import time
import at

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
     at.place_trade(item,quantity, trade_type, trail)
     return str(0)
   except Exception as e:
    print(str(e))
    return str(e)
   

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
