import hashlib


print(hashlib.sha256('test'.encode()).hexdigest())