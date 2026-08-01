"""Change-risk assessment worksheet (educational, std-lib only).

Scores a proposed network change on impact, blast radius, rollback, and
maintenance-window factors. Higher = riskier. Demonstrates structured
change-risk evaluation.
Original for system-design-mastery.

Run:  python change_risk_worksheet.py
"""
def assess(change):
    score = 0
    reasons = []
    # blast radius
    if change.get("core_device"): score += 30; reasons.append("affects core device (+30)")
    elif change.get("edge_device"): score += 10; reasons.append("edge device (+10)")
    # change type
    if change.get("routing"): score += 25; reasons.append("routing change (+25)")
    if change.get("firewall"): score += 25; reasons.append("firewall change (+25)")
    if change.get("config"): score += 15; reasons.append("config change (+15)")
    # mitigations
    if not change.get("rollback"): score += 20; reasons.append("no rollback (+20)")
    if not change.get("maintenance_window"): score += 15; reasons.append("outside maintenance window (+15)")
    if change.get("ha_pair"): score -= 10; reasons.append("HA pair (safe) (-10)")
    if change.get("approved"): score -= 10; reasons.append("pre-approved (-10)")
    return max(0, score), reasons

def main():
    changes = [
        {"name": "core-r1 BGP change", "core_device": True, "routing": True, "rollback": True, "maintenance_window": True, "ha_pair": True, "approved": True},
        {"name": "fw1 policy update", "edge_device": True, "firewall": True, "rollback": False, "maintenance_window": False, "approved": False},
        {"name": "sw3 port desc", "edge_device": True, "config": True, "rollback": True, "maintenance_window": True, "approved": True},
    ]
    for c in changes:
        score, reasons = assess(c)
        verdict = "APPROVE" if score < 30 else ("REVIEW" if score < 60 else "REJECT")
        print(f"\n{c['name']}: risk={score} -> {verdict}")
        for r in reasons: print(f"  {r}")

if __name__ == "__main__":
    main()
