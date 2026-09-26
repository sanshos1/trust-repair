import argparse
import base64
import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / "accounts.env").read_text(encoding="utf-8")
ADDRESS = "0xeCd60E0d76236dFa912041938BC07c5eaa34f6Ee"
INCIDENT = (
    "https://sanshos1-trust-repair.pages.dev/evidence/"
    "mutable-incident.txt?proof=6110128"
)
PROOF = (
    "https://cdn.jsdelivr.net/gh/sanshos1/trust-repair@"
    "ff4a9fc02f79698f7d7ebc589d77d4b9e500b02f/evidence/archive-restored.txt"
)


def account(slot: int):
    match = re.search(
        rf'^ACCOUNT_{slot}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M
    )
    if not match:
        raise RuntimeError(f"Missing GenLayer key for account slot {slot}")
    return create_account(account_private_key=match.group(1).strip())


def wait(client, transaction):
    receipt = client.wait_for_transaction_receipt(
        transaction_hash=transaction,
        status="FINALIZED",
        retries=180,
        interval=5000,
        full_transaction=True,
    )
    leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
    return receipt, leader


def decoded_result(leader):
    for key in ("result", "output", "return_data", "error"):
        value = leader.get(key)
        if isinstance(value, dict):
            payload = value.get("payload")
            if isinstance(payload, str):
                return payload
            value = value.get("raw")
        if not isinstance(value, str):
            continue
        try:
            return base64.b64decode(value).decode("utf-8", errors="replace").lstrip("\x01")
        except Exception:
            return value
    return ""


parser = argparse.ArgumentParser()
parser.add_argument("phase", choices=("open", "attempt", "inspect", "peek"))
parser.add_argument("case_id", nargs="?")
parser.add_argument("transaction", nargs="?")
args = parser.parse_args()

claimant, respondent, witness_a, witness_b = [account(slot) for slot in (3, 4, 5, 6)]

if args.phase == "open":
    case_id = f"MUTATION-{int(time.time())}"
    claimant_client = create_client(chain=studionet, account=claimant)
    transaction = claimant_client.write_contract(
        address=ADDRESS,
        function_name="open_case",
        args=[
            case_id,
            respondent.address,
            witness_a.address,
            witness_b.address,
            "Release 52 removed a public accessibility record.",
            ["Restore the public record", "Publish a correction"],
            INCIDENT,
            3600,
        ],
        value=0,
    )
    print(f"open_case_transaction={transaction}", flush=True)
    receipt, leader = wait(claimant_client, transaction)
    if str(leader.get("execution_result", "")).upper() != "SUCCESS":
        raise RuntimeError(f"open_case failed: {leader}")
    respondent_client = create_client(chain=studionet, account=respondent)
    acceptance = respondent_client.write_contract(
        address=ADDRESS, function_name="accept_plan", args=[case_id], value=0
    )
    print(f"accept_plan_transaction={acceptance}", flush=True)
    _, accept_leader = wait(respondent_client, acceptance)
    if str(accept_leader.get("execution_result", "")).upper() != "SUCCESS":
        raise RuntimeError(f"accept_plan failed: {accept_leader}")
    state = claimant_client.read_contract(
        address=ADDRESS, function_name="get_case", args=[case_id]
    )
    print(
        json.dumps(
            {
                "caseId": case_id,
                "incidentDigest": state["incident_digest"],
                "state": state["state"],
                "openCase": str(transaction),
                "acceptPlan": str(acceptance),
            }
        ),
        flush=True,
    )
elif args.phase == "attempt":
    if not args.case_id:
        raise RuntimeError("attempt phase requires case_id")
    witness_client = create_client(chain=studionet, account=witness_a)
    transaction = witness_client.write_contract(
        address=ADDRESS,
        function_name="witness_remedy",
        args=[args.case_id, 0, PROOF],
        value=0,
    )
    print(f"mutation_attempt_transaction={transaction}", flush=True)
    receipt, leader = wait(witness_client, transaction)
    error = decoded_result(leader)
    result = {
        "caseId": args.case_id,
        "transaction": str(transaction),
        "status": receipt.get("status_name"),
        "consensus": receipt.get("result_name"),
        "leaderExecution": leader.get("execution_result"),
        "error": error,
    }
    print(json.dumps(result), flush=True)
    if str(leader.get("execution_result", "")).upper() == "SUCCESS":
        raise RuntimeError("Mutated incident was unexpectedly accepted")
    if "incident baseline changed" not in error:
        raise RuntimeError(f"Unexpected rejection reason: {error}")
elif args.phase == "inspect":
    if not args.transaction:
        raise RuntimeError("inspect phase requires case_id and transaction")
    witness_client = create_client(chain=studionet, account=witness_a)
    receipt, leader = wait(witness_client, args.transaction)
    print(
        json.dumps(
            {
                "caseId": args.case_id,
                "transaction": args.transaction,
                "status": receipt.get("status_name"),
                "consensus": receipt.get("result_name"),
                "leaderExecution": leader.get("execution_result"),
                "error": decoded_result(leader),
            }
        ),
        flush=True,
    )
else:
    if not args.transaction:
        raise RuntimeError("peek phase requires case_id and transaction")
    witness_client = create_client(chain=studionet, account=witness_a)
    print(
        json.dumps(
            witness_client.get_transaction(transaction_hash=args.transaction),
            default=str,
        ),
        flush=True,
    )
