import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text(encoding="utf-8")
ADDRESS = "0xeCd60E0d76236dFa912041938BC07c5eaa34f6Ee"
EVIDENCE_COMMIT = "ff4a9fc02f79698f7d7ebc589d77d4b9e500b02f"


def account(slot: int):
    match = re.search(
        rf'^ACCOUNT_{slot}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M
    )
    if not match:
        raise RuntimeError(f"Missing GenLayer key for account slot {slot}")
    return create_account(account_private_key=match.group(1).strip())


def send(client, method, args):
    transaction = client.write_contract(
        address=ADDRESS, function_name=method, args=args, value=0
    )
    print(f"{method}_transaction={transaction}", flush=True)
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=transaction,
        status="FINALIZED",
        retries=180,
        interval=5000,
        full_transaction=True,
    )
    leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
    if "MAJORITY_AGREE" not in str(receipt.get("result_name", "")).upper():
        raise RuntimeError(f"{method} did not reach validator agreement")
    if str(leader.get("execution_result", "")).upper() != "SUCCESS":
        raise RuntimeError(f"{method} leader execution failed: {leader}")
    return str(transaction)


claimant, respondent, witness_a, witness_b = [account(slot) for slot in (3, 4, 5, 6)]
clients = {
    "claimant": create_client(chain=studionet, account=claimant),
    "respondent": create_client(chain=studionet, account=respondent),
    "witness_a": create_client(chain=studionet, account=witness_a),
    "witness_b": create_client(chain=studionet, account=witness_b),
}
case_id = f"REMEDIATION-{int(time.time())}"
incident = (
    "https://raw.githubusercontent.com/sanshos1/trust-repair/"
    f"{EVIDENCE_COMMIT}/evidence/incident.txt"
)
proofs = [
    "https://cdn.jsdelivr.net/gh/sanshos1/trust-repair@"
    f"{EVIDENCE_COMMIT}/evidence/archive-restored.txt",
    "https://raw.githack.com/sanshos1/trust-repair/"
    f"{EVIDENCE_COMMIT}/evidence/correction-published.txt",
    "https://github.com/sanshos1/trust-repair/raw/"
    f"{EVIDENCE_COMMIT}/evidence/notice-delivered.txt",
    "https://sanshos1-trust-repair.pages.dev/evidence/remedy-4.txt?v=462fcdc3",
]
remedies = [
    "Restore the public archive",
    "Publish a durable correction",
    "Notify affected readers",
    "Preserve the ordered audit trail",
]

transactions = {}
transactions["openCase"] = send(
    clients["claimant"],
    "open_case",
    [
        case_id,
        respondent.address,
        witness_a.address,
        witness_b.address,
        "Release 41 public accessibility records were removed and must remain visible throughout repair.",
        remedies,
        incident,
        3600,
    ],
)
transactions["acceptPlan"] = send(clients["respondent"], "accept_plan", [case_id])
transactions["remedies"] = []
for index, proof in enumerate(proofs):
    role = "witness_a" if index % 2 == 0 else "witness_b"
    transactions["remedies"].append(
        send(clients[role], "witness_remedy", [case_id, index, proof])
    )

state = clients["claimant"].read_contract(
    address=ADDRESS, function_name="get_case", args=[case_id]
)
if state["state"] != "RESTORED" or int(state["next_remedy"]) != 4:
    raise RuntimeError(f"Unexpected final state: {state}")
if len(state["incident_digest"]) != 64 or len(state["proofs"]) != 4:
    raise RuntimeError(f"Missing digest or proof evidence: {state}")

print(
    json.dumps(
        {
            "caseId": case_id,
            "contractAddress": ADDRESS,
            "state": state["state"],
            "incidentDigest": state["incident_digest"],
            "nextRemedy": int(state["next_remedy"]),
            "roles": {
                "claimant": claimant.address,
                "respondent": respondent.address,
                "witnessA": witness_a.address,
                "witnessB": witness_b.address,
            },
            "transactions": transactions,
            "proofs": state["proofs"],
            "proofDigests": state["digests"],
            "witnessSequence": state["witnesses"],
        },
        default=str,
    ),
    flush=True,
)
