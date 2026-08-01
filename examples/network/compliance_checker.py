"""Configuration-compliance checker (educational, std-lib only).

Checks a device config against a set of compliance rules (password policy,
NTP, logging, SNMP) and reports violations. Demonstrates policy-as-code.
Original for system-design-mastery.

Run:  python compliance_checker.py
"""
RULES = [
    ("password", lambda c: "enable secret" in c.lower(), "Missing 'enable secret' (plain password)"),
    ("ntp", lambda c: "ntp server" in c.lower(), "No NTP server configured"),
    ("logging", lambda c: "logging host" in c.lower(), "No syslog logging host"),
    ("snmp", lambda c: "snmp-server community public" not in c.lower(), "Default SNMP community 'public' is insecure"),
    ("ssh", lambda c: "transport input ssh" in c.lower(), "Telnet not restricted to SSH only"),
]

CONFIG = """
hostname sw-core
enable secret $9$mYhAsDfG
!
interface vlan1
 ip address 10.0.0.1 255.255.255.0
!
line vty 0 4
 transport input telnet
!
snmp-server community public RO
!
"""

def main():
    print(f"Checking {len(RULES)} compliance rules:\n")
    violations = 0
    for name, check, desc in RULES:
        passed = check(CONFIG)
        status = "PASS" if passed else "FAIL"
        if not passed: violations += 1
        print(f"  [{status}] {name:10} {desc if not passed else ''}")
    print(f"\n{len(RULES) - violations}/{len(RULES)} rules passed; {violations} violation(s).")

if __name__ == "__main__":
    main()
