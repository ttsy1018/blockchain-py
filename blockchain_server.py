"""
ブロックチェーンノードのサーバを立ち上げる
"""

from flask import Flask
from flask import jsonify

import blockchain
import wallet

app = Flask(__name__)

# DB用意するのが面倒なのでキャッシュに入れる
cache = {}
def get_blockchain():
    cached_blockchain = cache.get('blockchain')
    # キャッシュがない場合
    if not cached_blockchain:
        # ウォレットを生成
        miners_wallet = wallet.Wallet()
        # ブロックチェーンオブジェクトをキャッシュに入れる
        cache['blockchain'] = blockchain.BlockChain(
            blockchain_address= miners_wallet.blockchain_address,
            port=app.config['port']
        )
        
        # 確認用ログ
        app.logger.warning({
            'private_key': miners_wallet.private_key,
            'public_key': miners_wallet.public_key,
            'blockchain_address': miners_wallet.blockchain_address
        })
    # ブロックチェーンオブジェクトを返す
    return cache['blockchain']

@app.route('/chain', methods=['GET'])
def get_chain():
    block_chain = get_blockchain()
    response = {
        'chain': block_chain.chain
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to Listen on')

    args = parser.parse_args()
    port = args.port

    app.config['port'] = port

    app.run(host='127.0.0.1', port=port, threaded=True, debug=True)