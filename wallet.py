"""
ブロックチェーンアドレスの作成
デジタル署名を行う
"""

import base58
import codecs
import hashlib
import binascii

from ecdsa import NIST256p
from ecdsa import SigningKey

import utils

class Wallet(object):

    def __init__(self):
        # 秘密鍵を生成
        self._private_key = SigningKey.generate(curve=NIST256p)
        # 公開鍵をECDSAで生成
        self._public_key = self._private_key.get_verifying_key()
        # ブロックチェーンアドレスを生成
        self._blockchain_address = self.generate_blockchain_address()

    @property
    def private_key(self):
        return self._private_key.to_string().hex()
    
    @property
    def public_key(self):
        return self._public_key.to_string().hex()
    
    @property
    def blockchain_address(self):
        return self._blockchain_address
    
    # ブロックチェーンアドレスを作成
    # bitcoinのブロックチェーンアドレスの作成方法を流用
    def generate_blockchain_address(self):
        # 公開鍵をbytes型で取得（hexdigest()でハッシュ化すると16進数で生成される）
        public_key_bytes = self._public_key.to_string()
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()

        # 上記のハッシュ値をripemed160のhexにする
        ripemed160_bpk = hashlib.new('ripemd160')
        ripemed160_bpk.update(sha256_bpk_digest)
        ripemed160_bpk_digest = ripemed160_bpk.digest()
        ripemed160_bpk_hex = codecs.encode(ripemed160_bpk_digest, 'hex')

        # network byte をバイナリで生成する
        network_byte = b'00' # 本番ネットでは00をつけるらしい
        network_bitcoin_public_key = network_byte + ripemed160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key, 'hex')

        # ダブルハッシュを生成する(network byteをSHA256で2度hexでハッシュ化する)
        sha256_bpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest() 
        sha256_2_nbpk = hashlib.sha256(sha256_bpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')

        # チェックサムを取得
        checksum = sha256_hex[:8]

        # 公開鍵とチェックサムの連結
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')

        # base58でエンコード
        blockchain_address = base58.b58encode(binascii.unhexlify(address_hex)).decode('utf-8')

        return blockchain_address
    
class Transaction(object):

    def __init__(self, sender_private_key, sender_public_key,
                 sender_blockchain_address, recipient_blockchain_address,
                 value):
        self.sender_private_key = sender_private_key
        self.sender_public_key = sender_public_key
        self.sender_blockchain_address = sender_blockchain_address
        self.recipient_blockchain_address = recipient_blockchain_address
        self.value = value

    # デジタル署名を行う
    def generate_signature(self):
        sha256 = hashlib.sha256()
        transaction = utils.sorted_dict_by_key({
            'sender_blockchain_address': self.sender_blockchain_address,
            'recipient_blockchain_address': self.recipient_blockchain_address,
            'value': float(self.value)
        })
        # トランザクションをSHA256にハッシュ化
        sha256.update(str(transaction).encode('utf-8'))
        message = sha256.digest()

        private_key = SigningKey.from_string(
            bytes().fromhex(self.sender_private_key), curve=NIST256p
        )
        # ハッシュ化したものにデジタル署名をする(hex)
        private_key_sign = private_key.sign(message)
        signature = private_key_sign.hex()

        return signature
    
if __name__ == '__main__':
    wallet = Wallet()
    print(wallet.private_key)
    print(wallet.public_key)
    print(wallet.blockchain_address)

    # デジタル署名の作成
    t = Transaction(wallet.private_key, wallet.public_key, wallet.blockchain_address, 'Bsan', 1.0)
    print(t.generate_signature())