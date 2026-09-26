import json
import re
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text(encoding="utf-8")
match = re.search(
    r'^ACCOUNT_3_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M
)
if not match:
    raise RuntimeError("Missing ACCOUNT_3_GENLAYER_PRIVATE_KEY")

account = create_account(account_private_key=match.group(1).strip())
client = create_client(chain=studionet, account=account)
transaction = client.deploy_contract(
    code=(ROOT / "contracts" / "contract.py").read_text(encoding="utf-8"), args=[]
)
print(f"deployment_transaction={transaction}", flush=True)
receipt = client.wait_for_transaction_receipt(
    transaction_hash=transaction,
    status="FINALIZED",
    retries=180,
    interval=5000,
    full_transaction=True,
)
leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
address = receipt.get("data", {}).get("contract_address")
if not address:
    address = receipt.get("to_address") or receipt.get("recipient")
if "MAJORITY_AGREE" not in str(receipt.get("result_name", "")).upper():
    raise RuntimeError("Deployment did not reach validator agreement")
if str(leader.get("execution_result", "")).upper() != "SUCCESS":
    raise RuntimeError("Deployment leader execution failed")
print(
    json.dumps(
        {
            "contractAddress": address,
            "deploymentTransaction": str(transaction),
            "wallet": account.address,
            "status": receipt.get("status_name"),
            "consensus": receipt.get("result_name"),
            "leaderExecution": leader.get("execution_result"),
        },
        default=str,
    ),
    flush=True,
)
