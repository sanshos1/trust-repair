# Steward remediation matrix

| Steward requirement | Code path | Targeted proof | Status |
| --- | --- | --- | --- |
| Anchor incident content or digest when opening a case | `open_case` fetches the complete bounded incident and stores `incident_digest`. | `test_incident_mutation_is_rejected` changes the incident after opening and expects the baseline guard. | Pending execution |
| Verify every later incident fetch against the baseline | `_check` compares the freshly fetched incident digest with `incident_digest` before evaluating a remedy. | Live mutation rejection will be recorded after deployment. | Pending deployment |
| Make every accepted remedy count reachable | `witness_remedy` assigns even indexes to Witness A and odd indexes to Witness B, allowing 2 to 8 ordered remedies. | `test_four_remedies_restore_with_alternating_witnesses` exercises A/B/A/B through `RESTORED`. | Pending execution |
| Preserve a complete lifecycle | The respondent accepts, witnesses alternate, and deadline expiry remains permissionless. | A new StudioNet lifecycle will be recorded after deployment. | Pending deployment |
