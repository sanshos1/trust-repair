# Trust Repair / the kintsugi ledger

This is a record of repair, not a reputation reset. The original incident is frozen first; it remains readable after every remedy and final state.

## The fracture

A claimant names a respondent, two witness wallets, an incident record, and two to eight concrete remedies. Validators fetch and hash-pin the complete bounded incident at case creation. The respondent must accept the plan. Silence cannot be presented as consent.

## The gold

Witness A handles even-numbered seams and Witness B handles odd-numbered seams, alternating for as many as eight remedies. For each seam, validators retrieve the incident and a fresh-origin completion proof, reject any incident digest that differs from the opening baseline, and agree that the exact remedy is complete. Proof digests and witness attribution remain stored.

## The shape after repair

`OPEN → PLAN_ACCEPTED → REPAIRING → RESTORED`

If the window closes before every seam is verified, anyone may preserve the honest `PARTIAL` result. Tests cover complete restoration, alternating witnesses, incident mutation, witness replay, and a forged incident-preservation verdict.

```bash
genvm-lint contracts/contract.py
python -m pytest -q
```

## StudioNet record

- Contract: `0xeCd60E0d76236dFa912041938BC07c5eaa34f6Ee`
- Deployment transaction: `0x5b91d12237447cbf127a99f40232ffce652f26235142484cb5ba4bac1a01c243`
- Verified four-remedy case: `REMEDIATION-1790418066` (`RESTORED`)
- Public interface: https://sanshos1-trust-repair.pages.dev/

The deployed source matches `contracts/contract.py` at commit `08fc70d57de78dd02c6fbd848d744890ca67c6e1`.
