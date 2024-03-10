import hashlib
import json
import logging
import sys
import time
import utils

MINING_DIFFICULTY = 3                # ナンスを求める際にハッシュ値の何桁目までを検証に使用するか
MINING_SENDER     = 'THE BLOCKCHAIN' # ブロックチェーン側の送信者名
MINING_REWARD     = 1.0              # マイニング報酬額

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class BlockChain(object):

    def __init__(self, blockchain_address=None) -> None:
        self.transaction_pool = []
        self.chain = []
        self.create_block(0, self.hash({}))
        self.blockchain_address = blockchain_address

    # ナンスと直前のハッシュ値を受け取りブロックを作成
    def create_block(self, nonce, previous_hash):
        # ブロックを作成
        block = utils.sorted_dict_by_key({
            'timestamp': time.time(),
            'transactions': self.transaction_pool,
            'nonce': nonce,
            'previous_hash': previous_hash
        })

        # チェーンにブロックに追加
        self.chain.append(block)
        # プールを空にする
        self.transaction_pool = []

        return block
    
    # ブロックをハッシュ化する
    def hash(self, block):
        sorted_block = json.dumps(block, sort_keys=True)
        return hashlib.sha256(sorted_block.encode()).hexdigest()
    
    # トランザクションプールの追加
    def add_transaction(self, sender_blockchain_address, recipient_blockchain_address, value):
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': sender_blockchain_address,
            'recipient_blockchain_address': recipient_blockchain_address,
            'value': float(value)
        })

        self.transaction_pool.append(transaction)
        return True
    
    # ナンスの検証
    # 今回の検証：検証ナンスを含めてブロックをハッシュ化した際、先頭の3桁が「0」になることを検証する
    def valid_proof(self, transactions, previous_hash, nonce, difficulty=MINING_DIFFICULTY):
        # 推測するブロックを定義
        guess_block = utils.sorted_dict_by_key({
            'transactions': transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        })
        # 推測ブロックをハッシュ化
        guess_hash = self.hash(guess_block)
        return guess_hash[:difficulty] == '0'*difficulty

    # ナンスの導出
    def proof_of_work(self):
        # プールされているトランザクションをコピーして取得
        transactions = self.transaction_pool.copy()
        # 最後のチェーンのハッシュ値を取得
        previous_hash = self.hash(self.chain[-1])
        # ナンスの初期化
        nonce = 0

        # ナンスの検証を行って不正解だった場合、ナンスをインクリメントし再計算する
        while self.valid_proof(transactions, previous_hash, nonce) == False:
            nonce += 1
        
        # 検証が終わったらナンスを返して、返したナンス値でブロック作成処理を行う
        return nonce
    
    def mining(self):
        # 報酬のトランザクションを追加
        self.add_transaction(
            sender_blockchain_address=MINING_SENDER,
            recipient_blockchain_address=self.blockchain_address,
            value=MINING_REWARD
        )
        # ナンスの計算
        nonce = self.proof_of_work()
        # 最後尾のハッシュ値
        previous_hash = self.hash(self.chain[-1])
        # ブロック生成
        self.create_block(nonce, previous_hash)
        
        logger.info({'action': 'mining', 'status': 'success'})
        return True
    
    # トランザクションの合計を計算する
    def calculate_total_amount(self, blockchain_address):
        total_amount = 0.0
        for block in self.chain:
            for transaction in block['transactions']:
                value = float(transaction['value'])
                if blockchain_address == transaction['recipient_blockchain_address']:
                    total_amount += value
                if blockchain_address == transaction['sender_blockchain_address']:
                    total_amount -= value
        return total_amount

if __name__ == '__main__':
    my_blockchain_address = 'my_blockchain_address'
    block_chain = BlockChain(blockchain_address=my_blockchain_address)
    utils.pprint(block_chain.chain)

    # トランザクションの追加
    # 最後のチェーンのハッシュ値を取得（previous_hash）
    # ナンスを導出
    # ナンスと最後のチェーンのハッシュ値を渡してブロック作成
    block_chain.add_transaction('A', 'B', 1.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    block_chain.add_transaction('C', 'D', 2.0)
    block_chain.add_transaction('X', 'Y', 3.0)
    block_chain.mining()
    utils.pprint(block_chain.chain)

    print('my', block_chain.calculate_total_amount(my_blockchain_address))
    print('C', block_chain.calculate_total_amount('C'))
    print('D', block_chain.calculate_total_amount('D'))