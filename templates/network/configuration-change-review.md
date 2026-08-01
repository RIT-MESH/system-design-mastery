# Configuration Change Review (Network-AI)

> Template for reviewing a proposed or detected configuration change (drift).

## Change identity
- **Device / site:** 
- **Change source:** planned | drift-detected | emergency
- **Diff (current vs baseline):** 
- **Classifier result:** authorized | unauthorized | error | policy-violation
- **Risk score:** 0–100
- **Impacted services:** 

## Review
- **Intent / justification:** 
- **Policy compliance:** pass | fail
- **Approver:** 
- **Action:** approve | remediate | rollback | ticket
- **Audit reference:** 

## Safety
- Auto-remediation is NOT default; requires approval.
- Secrets/PII redacted from stored diffs.
