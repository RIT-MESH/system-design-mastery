# AI Evaluation Plan

> Define what "good" means for an AI feature and how to measure it before and after release.

## Scope
- Feature: 
- Model(s) and versions: 
- Date of baselines: 

## Metrics
- Retrieval: recall@k, nDCG, metadata/ACL correctness
- Generation: groundedness, answer correctness, citation accuracy, hallucination rate
- Ops: TTFT, TPOT, tokens/s, cost/request, error rate
- Safety: refusal rate, unauthorized-action attempts (0), prompt-injection pass rate

## Test sets
- Golden set (labeled): 
- Regression set: 
- Adversarial set (injection, PII): 

## Gates
- Release requires: groundedness >= _ , hallucination <= _ , latency p99 <= _ , cost <= _
- Rollback trigger: any gate regressed beyond threshold

## Cadence
- Pre-release eval + continuous eval on a sample + monthly full eval
