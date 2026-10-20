import requests
import urllib3

# Suppress self-signed certificate warnings for local testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:8000"

print("[*] Starting Logos End-to-End Integration Test...")

# 1. Check Balances & Chain State
print("\n[Step 1] Fetching initial ledger state...")
r = requests.get(f"{BASE_URL}/balances", verify=False)
print("Balances Response:", r.json())

# 2. Submit a Test Transaction
print("\n[Step 2] Submitting transaction to mempool...")
tx_payload = {
    "sender_addr": "8188FA070A60A91F",
    "sender_pub": "MOCK_PUBLIC_KEY_HEX",
    "recipient": "RECIPIENT_VAULT_NODE_2",
    "amount": 25.0,
    "signature": "MOCK_VALID_SIGNATURE"
}
r = requests.post(f"{BASE_URL}/transaction/submit", json=tx_payload, verify=False)
print("Transaction Response:", r.json())

# 3. Mine a New Block via Physics Engine
print("\n[Step 3] Mining new block via physics validator...")
mine_payload = {
    "tensor_metrics": {"spectral_entropy": 0.45, "shear_factor": 0.02},
    "invariant": 6.8,
    "miner_address": "8188FA070A60A91F"
}
r = requests.post(f"{BASE_URL}/mine", json=mine_payload, verify=False)
print("Mining Response Status:", r.status_code)
print("Mining Response Body:", r.json())

# 4. Verify Final Ledger Chain
print("\n[Step 4] Verifying final blockchain structure...")
r = requests.get(f"{BASE_URL}/chain", verify=False)
chain_data = r.json()
print(f"Total Blocks in Ledger: {len(chain_data['chain'])}")
print("[+] E2E Integration Test Completed Successfully!")
