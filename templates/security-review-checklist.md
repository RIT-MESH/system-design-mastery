# Security Review Checklist

> Applied to every design and PR. Vendor-neutral; vendor specifics are noted separately.

## Identity & access
- [ ] Authentication mechanism defined (session/token/OAuth2/OIDC/SAML).
- [ ] Authorization model defined (RBAC/ABAC/PBAC); default-deny.
- [ ] Token/session lifecycle: issuance, rotation, revocation, expiry.
- [ ] Least privilege enforced for service-to-service calls.

## Transport & data protection
- [ ] TLS everywhere (in transit); mTLS for high-trust internal paths.
- [ ] Encryption at rest with documented KMS and key rotation.
- [ ] Secrets managed by a secret manager, not config files or env in plaintext.
- [ ] Certificates have automated rotation; expiry monitored.

## Input & API
- [ ] Input validation at the boundary (type, size, format, semantics).
- [ ] Rate limiting and throttling on public endpoints.
- [ ] OWASP API Security Top 10 reviewed (S-OWASPAPI).
- [ ] Idempotency keys validated and scoped to the caller.

## Multi-tenancy & isolation
- [ ] Tenant data isolation enforced (separate DB/schema/row-level + RLS).
- [ ] Resource isolation (bulkheads) prevents noisy-neighbor and cross-tenant exhaustion.
- [ ] No tenant identifier taken purely from client input without server validation.

## Audit & privacy
- [ ] Audit logs for security-relevant events, tamper-evident and retained.
- [ ] PII classified; masking and minimization applied in logs/responses.
- [ ] Data retention and deletion satisfy regulatory requirements.
- [ ] Privacy-by-design: collect only what is needed.

## Threat modeling & supply chain
- [ ] STRIDE (S-STRIDE) applied to the design; threats enumerated with mitigations.
- [ ] Zero-trust assumption documented for internal networks.
- [ ] Dependencies pinned and scanned; SBOM where applicable.
- [ ] DDoS and WAF strategy noted for public surfaces.
