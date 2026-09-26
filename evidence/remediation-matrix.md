# Steward remediation matrix

| Steward requirement | Code path | Targeted proof | Status |
| --- | --- | --- | --- |
| Anchor incident content or digest when opening a case | `open_case` fetches the complete bounded incident and stores `incident_digest`. | Live case `MUTATION-1790418423` stored baseline `256819…c5ed`. | Verified on StudioNet |
| Verify every later incident fetch against the baseline | `_check` compares the freshly fetched incident digest with `incident_digest` before evaluating a remedy. | Mutation transaction `0xedd923…15551` finalized as an expected negative-path rollback: the leader and three active validators returned `[EXPECTED] incident baseline changed`; two validators were cancelled after quorum. | Verified rejection on StudioNet |
| Make every accepted remedy count reachable | `witness_remedy` assigns even indexes to Witness A and odd indexes to Witness B, allowing 2 to 8 ordered remedies. | Live case `REMEDIATION-1790418066` completed A/B/A/B and reached `RESTORED`. | Verified on StudioNet |
| Preserve a complete lifecycle | The respondent accepts, witnesses alternate, and deadline expiry remains permissionless. | Six lifecycle transactions finalized with majority agreement; see `network-run.json`. | Verified on StudioNet |

The focused surface test passes and `genvm-lint` passes all three checks. The legacy direct `gltest` runner currently fails in its SDK calldata decoder before loading this contract, so it is not represented as a passing contract test.
