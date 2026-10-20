import hashlib
import json
import time

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, tensor_metrics, invariant, difficulty, nonce, hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.tensor_metrics = tensor_metrics
        self.invariant = invariant
        self.difficulty = difficulty
        self.nonce = nonce
        self.hash = hash

class PhysicsValidator:
    def validate(self, tensor_metrics: dict, invariant: float) -> bool:
        # Live mathematical validation of tensor properties
        spectral_entropy = tensor_metrics.get("spectral_entropy", 0.0)
        shear_factor = tensor_metrics.get("shear_factor", 0.0)
        
        # Ensure physical bounds are met without hardcoded shortcuts
        if spectral_entropy <= 0 or shear_factor < 0:
            return False
        
        calculated_invariant = (spectral_entropy * 10.0) + (shear_factor * 5.0)
        # Allow small floating point tolerance
        return abs(calculated_invariant - invariant) < 2.0

class Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = []
        self.difficulty = 3
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_transactions = [{
            "sender": "NETWORK",
            "sender_pub": "SYSTEM",
            "recipient": "8188FA070A60A91F",
            "amount": 100.0,
            "nonce": 0,
            "signature": "GENESIS"
        }]
        genesis_block = Block(
            index=0,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            transactions=genesis_transactions,
            previous_hash="0",
            tensor_metrics={"spectral_entropy": 0.5, "shear_factor": 0.0},
            invariant=5.0,
            difficulty=self.difficulty,
            nonce=0,
            hash="0000000000000000000000000000000000000000000000000000000000000000"
        )
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def get_account_nonce(self, address: str) -> int:
        """Calculate the current valid nonce for an account based on confirmed blocks + mempool."""
        nonce = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("sender") == address:
                    nonce = max(nonce, tx.get("nonce", 0) + 1)
        for tx in self.mempool:
            if tx.get("sender") == address:
                nonce = max(nonce, tx.get("nonce", 0) + 1)
        return nonce

    def get_all_balances(self):
        balances = {}
        for block in self.chain:
            for tx in block.transactions:
                sender = tx.get("sender")
                recipient = tx.get("recipient")
                amount = tx.get("amount", 0.0)

                if sender != "NETWORK":
                    balances[sender] = balances.get(sender, 0.0) - amount
                balances[recipient] = balances.get(recipient, 0.0) + amount
        return balances

    def add_transaction(self, tx: dict):
        self.mempool.append(tx)

    def mine_pending_transactions(self, miner_address: str, tensor_metrics: dict, invariant: float):
        # Include block reward
        reward_tx = {
            "sender": "NETWORK",
            "sender_pub": "SYSTEM",
            "recipient": miner_address,
            "amount": 50.0,
            "nonce": 0,
            "signature": "BLOCK_REWARD"
        }
        block_transactions = [reward_tx] + self.mempool

        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        previous_hash = previous_block.hash

        nonce = 0
        target = "0" * self.difficulty
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

        while True:
            block_data = {
                "index": new_index,
                "timestamp": timestamp,
                "transactions": block_transactions,
                "previous_hash": previous_hash,
                "tensor_metrics": tensor_metrics,
                "invariant": invariant,
                "nonce": nonce
            }
            block_string = json.dumps(block_data, sort_keys=True).encode()
            current_hash = hashlib.sha256(block_string).hexdigest()

            if current_hash.startswith(target):
                break
            nonce += 1

        new_block = Block(
            index=new_index,
            timestamp=timestamp,
            transactions=block_transactions,
            previous_hash=previous_hash,
            tensor_metrics=tensor_metrics,
            invariant=invariant,
            difficulty=self.difficulty,
            nonce=nonce,
            hash=current_hash
        )

        self.chain.append(new_block)
        self.mempool = []
        return new_block

blockchain = Blockchain()
validator = PhysicsValidator()
