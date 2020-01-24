import hashlib
import json
import logging
from uuid import uuid4

from app.utils.heap import Singleton

LOG = logging.getLogger(__name__)


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.transaction_id = uuid4()
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Block:
    def __init__(self):
        self.block_id = uuid4()
        self.transactions = []
        self.prev_hash = b'0'
        self.hash = None

    def _make_hash(self):
        # hash is create with usage of transactions and previous hash
        result = '\n'.join(self.transactions).encode() + self.prev_hash
        hash = hashlib.sha256(result)
        self.hash = hash.hexdigest().encode()


class RewardsChain(metaclass=Singleton):
    def __init__(self):
        self.blockchain_id = uuid4()
        self.blocks = []
        self.pending_transactions = []

    def _make_block(self):
        b = Block()

        if len(self.blocks) == 0:
            b.prev_hash = b'0'
        else:
            b.prev_hash = self.blocks[-1].hash

        for t in self.pending_transactions:
            b.transactions.append(t.to_json())
        b._make_hash()

        del self.pending_transactions[::]

        self.blocks.append(b)


def test_block():
    chain = RewardsChain()

    for i in range(20):
        chain.pending_transactions.append(Transaction('mike', 'paul', i))

    chain._make_block()

    for i in range(20):
        chain.pending_transactions.append(Transaction('mike', 'paul', i))

    chain._make_block()

    for i in range(20):
        chain.pending_transactions.append(Transaction('mike', 'paul', i))

    chain._make_block()

    for bl in chain.blocks:
        print("block id : {}, with hash : {}, and previous: {}\n".format(bl.block_id, bl.hash, bl.prev_hash))

    assert chain.blocks[0].prev_hash == b'0'
    assert chain.blocks[0].hash == chain.blocks[1].prev_hash
    assert chain.blocks[1].hash == chain.blocks[2].prev_hash


def test_singleton():
    b = RewardsChain()
    print(b.blockchain_id)
    b2 = RewardsChain()
    print(b2.blockchain_id)
    b3 = RewardsChain()
    print(b3.blockchain_id)
    assert b.blockchain_id == b2.blockchain_id == b3.blockchain_id
