# Trust Repair / the kintsugi ledger

This is a record of repair, not a reputation reset. The original incident is frozen first; it remains readable after every remedy and final state.

## The fracture

A claimant names a respondent, two independent witness wallets, an immutable incident record, and two to eight concrete remedies. The respondent must accept the plan. Silence cannot be presented as consent.

## The gold

Witnesses work in order and may attest only once. For each seam, validators retrieve the original incident and a fresh-origin completion proof. They independently agree that the exact remedy is complete and that the incident was not rewritten. Proof digests and witness attribution remain stored.

## The shape after repair

`OPEN → PLAN_ACCEPTED → REPAIRING → RESTORED`

If the window closes before every seam is verified, anyone may preserve the honest `PARTIAL` result. Tests cover complete restoration, witness replay, and a forged incident-preservation verdict.

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```

Deployment coordinates are added only after the reviewed source, live lifecycle, and public kintsugi interface agree.
