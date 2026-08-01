"""Upgrade-risk calculator (educational, std-lib only).

Scores an upgrade plan 0-100 from advisory age, advisories, backup, HA-awareness,
dependency, and rollback readiness. Higher = safer. Original for system-design-mastery.

Run:  python upgrade_risk.py
"""
def risk(plan):
    score = 0
    score += 15 if plan.get("backup") else 0
    score += 15 if plan.get("checksum_verified") else 0
    score += 20 if plan.get("ha_aware") else 0
    score += 10 if plan.get("dependencies_checked") else 0
    score += 20 if plan.get("rollback_ready") else 0
    score += 10 if not plan.get("open_advisories") else 0
    score += 10 if plan.get("target_compatible") else 0
    return score

def main():
    plans = [
        {"name":"r1-edge","backup":True,"checksum_verified":True,"ha_aware":True,"dependencies_checked":True,"rollback_ready":True,"open_advisories":False,"target_compatible":True},
        {"name":"fw-core","backup":True,"checksum_verified":False,"ha_aware":False,"dependencies_checked":True,"rollback_ready":True,"open_advisories":True,"target_compatible":True},
        {"name":"sw-old","backup":False,"checksum_verified":False,"ha_aware":False,"dependencies_checked":False,"rollback_ready":False,"open_advisories":True,"target_compatible":False},
    ]
    for p in plans:
        s = risk(p)
        verdict = "GO" if s >= 80 else ("REVIEW" if s >= 50 else "BLOCK")
        print(f"{p['name']:10} safety={s:3}  -> {verdict}")
    print("\nScores are advisory; humans approve; rollback always required.")

if __name__ == "__main__":
    main()
