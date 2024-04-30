from flask import Flask
from flask import jsonify
from flask import render_template

import wallet

app = Flask(__name__, template_folder='./templates')

@app.route('/')
def index():
    return render_template('./index.html')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument(
        '-p', '--port', 
        default=8080, 
        type=int, help='port to Listen on')
    parser.add_argument(
        '-g', '--gw', 
        default='http://127.0.0.1:5000', 
        type=str, help='blockchain gateway')

    args = parser.parse_args()
    port = args.port
    app.config['gw'] = args.gw

    app.run(host='0.0.0.0', port=port, threaded=True, debug=True)