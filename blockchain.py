import logging
import sys
import time


logging.basicConfig(level=logging.INFO, stream=sys.stdout)

class BlockChain(object):

    def __init__(self) -> None:
        self.transaction_pool = []
        self.chain = []
        self.create_block(0, 'init hash')

    def create_block(self, nonce, previous_hash):
        # ブロックを作成
        block = {
            'timestamp': time.time(),
            'transactions': self.transaction_pool,
            'nonce': nonce,
            'previous_hash': previous_hash
        }

        # チェーンにブロックに追加
        self.chain.append(block)
        # プールを空にする
        self.transaction_pool = []
        return block
    
def pprint(chains):
    for i, chain in enumerate(chains):
        print(f'{"="*25} Chain {i} {"="*25}')
        for k, v in chain.items():
            print(f'{k:15}{v}')
    print(f'{"*"*15}')

if __name__ == '__main__':
    block_chain = BlockChain()
    pprint(block_chain.chain)
    block_chain.create_block(5, 'hash 1')
    pprint(block_chain.chain)