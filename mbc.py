from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

global tx_id
from datetime import datetime
import hashlib
import json

tx_id = 0


class Transaction:
    def __init__(self, sender, receiver, amount):
        global tx_id
        self.txid = tx_id
        tx_id = tx_id + 1
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        h = SHA256.new(self.get_json().encode('UTF-8'))
        signer = pkcs1_15.new(sender)
        self.signature = signer.sign(h)

    def get_json(self):
        x = {
            "id": self.txid,
            "sender": self.sender.publickey().exportKey(format("OpenSSH")).decode(),
            "receiver": self.receiver,
            "amount": self.amount
        }
        return json.dumps(x)


class Block:
    def __init__(self, pre_hash, nonce, time, transactions):
        self.previoushash = pre_hash
        self.nonce = nonce
        self.difficulty = 4
        self.time = time
        self.transactions = transactions
        self.calculateHash()
        self.mine()

    def get_json(self):
        tx_s = []
        for i in range(len(self.transactions)):
            tx_s.append(self.transactions[i].get_json())

        j = {"previous_hash": self.previoushash,
             "nonce": self.nonce,
             "time": self.time,
             "transactions": tx_s
             }

        return json.dumps(j)

    def mine(self):
        print("Mining...")
        while (1):
            self.nonce = self.nonce + 1
            self.calculateHash()
            # print(self.current_hash)
            if self.current_hash[0:self.difficulty] == "0" * self.difficulty:
                return self.calculateHash()

    def calculateHash(self):
        self.current_hash = hashlib.md5(self.get_json().encode("utf-8")).hexdigest()


mbchain = []


class User:
    def __init__(self):
        self.key = RSA.generate(1024)
        self.id = str(self.key.publickey().exportKey(format("OpenSSH")))
        self.balance = int(0)

    def myfunc(self):
        print("Hello my name is " + self.name)

    def make_transaction(self, receiver_pub_id, amount):
        if (self.balance < amount):
            print("you havent sufficient amount in your balance")
            return False
        t = Transaction(self.key, receiver_pub_id, amount)
        verifier = pkcs1_15.new(self.key)
        v_hash = SHA256.new()
        v_hash.update(t.get_json().encode('UTF-8'))
        try:
            verifier.verify(v_hash, t.signature)
            user = get_user_from_id(receiver_pub_id)
            user.balance = user.balance + amount
            self.balance = self.balance - amount
            return t
        except ValueError:
            print("Transaction is not valid !")
            return 0


u1 = User();
u1.balance = 100 #for first transaction
u2 = User();
u3 = User();
u4 = User();
u5 = User()
users = [u1, u2, u3, u4, u5]
print(type(users[0]))


def get_user_from_id(id):
    for i in range(len(users)):
        k = users[i].key.publickey().exportKey(format("OpenSSH")).decode()
        if (k == id):
            return users[i]


all_transactions = []

res = u1.make_transaction(u2.key.publickey().exportKey(format("OpenSSH")).decode(), 50)
if (res != 0):
    all_transactions.append(res)

res = u2.make_transaction(u3.key.publickey().exportKey(format("OpenSSH")).decode(), 30)
if (res != 0):
    all_transactions.append(res)

res = u3.make_transaction(u4.key.publickey().exportKey(format("OpenSSH")).decode(), 20)
if (res != 0):
    all_transactions.append(res)

res = u4.make_transaction(u5.key.publickey().exportKey(format("OpenSSH")).decode(), 10)
if (res != 0):
    all_transactions.append(res)

res = u5.make_transaction(u1.key.publickey().exportKey(format("OpenSSH")).decode(), 5)
if (res != 0):
    all_transactions.append(res)

res = u2.make_transaction(u3.key.publickey().exportKey(format("OpenSSH")).decode(), 3)
if (res != 0):
    all_transactions.append(res)
res = u1.make_transaction(u4.key.publickey().exportKey(format("OpenSSH")).decode(), 6)
if (res != 0):
    all_transactions.append(res)
res = u1.make_transaction(u4.key.publickey().exportKey(format("OpenSSH")).decode(), 4)
if (res != 0):
    all_transactions.append(res)

b1_tra = all_transactions[0:2]
b2_tra = all_transactions[2:4]
b3_tra = all_transactions[5:6]

genesis_Block = Block(0, 0, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), all_transactions[0:1])
mbchain.append(genesis_Block)

b1 = Block(mbchain[len(mbchain) - 1].current_hash, 0, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), b1_tra)
mbchain.append(b1)

b2 = Block(mbchain[len(mbchain) - 1].current_hash, 0, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), b2_tra)
mbchain.append(b2)

b3 = Block(mbchain[len(mbchain) - 1].current_hash, 0, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), b3_tra)
mbchain.append(b3)
