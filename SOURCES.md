# Sources

This file is the single source of truth for citations used across the repository. Each source
has a **stable ID** referenced by chapters (e.g., `S-RFC9112`). Prefer primary sources:
RFCs, academic papers, official vendor/cloud/CNCF/database documentation. Secondary
engineering blogs are included with attribution where useful.

> Last updated: 2026-08-01. URLs were verified at the time of writing; link-check CI
> validates them continuously.

## RFCs and standards

| ID | Title | Reference |
|----|-------|-----------|
| S-RFC9110 | HTTP Semantics | https://www.rfc-editor.org/rfc/rfc9110 |
| S-RFC9112 | HTTP/1.1 Messaging | https://www.rfc-editor.org/rfc/rfc9112 |
| S-RFC9113 | HTTP/2 | https://www.rfc-editor.org/rfc/rfc9113 |
| S-RFC9114 | HTTP/3 | https://www.rfc-editor.org/rfc/rfc9114 |
| S-RFC8446 | TLS 1.3 | https://www.rfc-editor.org/rfc/rfc8446 |
| S-RFC7231 | HTTP/1.1 Semantics and Content (legacy) | https://www.rfc-editor.org/rfc/rfc7231 |
| S-RFC6749 | OAuth 2.0 Authorization Framework | https://www.rfc-editor.org/rfc/rfc6749 |
| S-RFC7515 | JSON Web Signature (JWS) | https://www.rfc-editor.org/rfc/rfc7515 |
| S-RFC7519 | JSON Web Token (JWT) | https://www.rfc-editor.org/rfc/rfc7519 |
| S-RFC7807 | Problem Details for HTTP APIs | https://www.rfc-editor.org/rfc/rfc7807 |
| S-RFC7396 | JSON Merge Patch | https://www.rfc-editor.org/rfc/rfc7396 |
| S-OIDC | OpenID Connect Core 1.0 | https://openid.net/specs/openid-connect-core-1_0.html |
| S-SAML | SAML 2.0 Core | https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.html |

## Semantics and serialization

| ID | Title | Reference |
|----|-------|-----------|
| S-PROTOBUF | Protocol Buffers Encoding | https://protobuf.dev/programming-guides/encoding/ |
| S-AVRO | Apache Avro 1.11 Specification | https://avro.apache.org/docs/1.11.1/specification/ |
| S-JSON | JSON (ECMA-404) | https://www.ecma-international.org/publications-and-standards/standards/ecma-404/ |

## Networking

| ID | Title | Reference |
|----|-------|-----------|
| S-DNS | DNS (RFC 1034/1035) | https://www.rfc-editor.org/rfc/rfc1035 |
| S-TCPUDP | TCP/IP Illustrated overview | https://datatracker.ietf.org/doc/rfc9293/ (TCP) · https://www.rfc-editor.org/rfc/rfc768 (UDP) |
| S-QUIC | QUIC: A UDP-Based Multiplexed Transport | https://www.rfc-editor.org/rfc/rfc9000 |

## Distributed systems theory

| ID | Title | Reference |
|----|-------|-----------|
| S-CAP | Brewer's CAP Theorem (Brewer 2000; Gilbert-Lynch 2002) | https://doi.org/10.1145/343477.343502 |
| S-PACELC | PACELC Theorem (Abadi 2012) | https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf |
| S-RAFT | Raft Consensus Algorithm (Ongaro-Ousterhout 2014) | https://raft.github.io/raft.pdf |
| S-PAXOS | Paxos Made Simple (Lamport 2001) | https://lamport.org/pubs/paxos-simple.pdf |
| S-BYZANTINE | Practical BFT (Castro-Liskov 1999) | https://pmg.csail.mit.edu/papers/osdi99.pdf |
| S-LAMPORT | Time, Clocks, and the Ordering of Events (Lamport 1978) | https://lamport.org/pubs/time-clocks.pdf |
| S-VECTORCLOCK | Vector Clocks (Mattern, Fidge, Schmuck) | https://en.wikipedia.org/wiki/Vector_clock |
| S-DYNAMO | Dynamo: Amazon's Highly Available KV Store (2007) | https://www.allthingsdistributed.com/2007/11/amazons_dynamo.html |
| S-GOSSSIP | Gossip Protocols (SWIM) | https://www.cs.cornell.edu/projects/ladis2009/papers/Ladis2009-final8.pdf |
| S-CRDT | Shapiro et al., CRDTs (2011) | https://hal.inria.fr/inria-00601707/document |

## Database and storage

| ID | Title | Reference |
|----|-------|-----------|
| S-SPANNER | Spanner: Google's Globally-Distributed Database (2012) | https://research.google/pubs/pub39966/ |
| S-BIGTABLE | Bigtable: A Distributed Storage System (2006) | https://research.google/pubs/pub27898/ |
| S-CHASH | Consistent Hashing and Random Trees (Karger et al. 1997) | https://www.akamai.com/site/en/documents/research-paper/consistent-hashing-and-random-trees-distributed-caching-protocols-for-relieving-hot-spots-on-the-world-wide-web-technical-publication.pdf |
| S-PG-INDEX | PostgreSQL Indexes Documentation | https://www.postgresql.org/docs/current/indexes.html |
| S-PG-CDC | PostgreSQL Logical Replication | https://www.postgresql.org/docs/current/logical-replication.html |
| S-MYSQL-REPL | MySQL Replication | https://dev.mysql.com/doc/refman/8.0/en/replication.html |
| S-CASSANDRA | Apache Cassandra Architecture | https://cassandra.apache.org/doc/latest/architecture/ |
| S-KAFKA | Kafka Design Documentation | https://kafka.apache.org/documentation/#design |
| S-ES | Elasticsearch Guide | https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html |
| S-REDIS | Redis Documentation | https://redis.io/docs/ |
| S-SNOWFLAKE | Twitter Snowflake (epoch + worker + sequence) | https://github.com/twitter-archive/snowflake |
| S-UUID | RFC 4122 (UUID) | https://www.rfc-editor.org/rfc/rfc4122 |

## Cloud-native and platform

| ID | Title | Reference |
|----|-------|-----------|
| S-K8S | Kubernetes Documentation | https://kubernetes.io/docs/home/ |
| S-OTEL | OpenTelemetry Specification | https://opentelemetry.io/docs/specs/otel/ |
| S-ISTIO | Istio Service Mesh | https://istio.io/latest/docs/ |
| S-ARMENTR | Armory / CNCF GitOps principles (OpenGitOps) | https://opengitops.dev/ |
| S-SLO | Google SRE — SLOs and error budgets | https://sre.google/sre-book/service-level-objectives/ |
| S-CHAOSENG | Principles of Chaos Engineering | https://principlesofchaos.org/ |
| S-STRIDE | OWASP Threat Modeling (STRIDE) | https://owasp.org/www-community/Threat_Modeling |
| S-OWASPAPI | OWASP API Security Top 10 | https://owasp.org/API-Security/editions/2023/en/0x11-t10/ |

## Architecture and resilience patterns

| ID | Title | Reference |
|----|-------|-----------|
| S-DDD | Domain-Driven Design reference (Evans/Vernon, summarised) | https://www.domainlanguage.com/ddd/ |
| S-CQRS | CQRS (Fowler, Martin Fowler's catalog) | https://martinfowler.com/bliki/CQRS.html |
| S-STRANGLER | Strangler Fig Application (Fowler) | https://martinfowler.com/bliki/StranglerFigApplication.html |
| S-BULKHEAD | Bulkhead pattern (Microsoft Azure docs) | https://learn.microsoft.com/azure/architecture/patterns/bulkhead |
| S-CIRCUIT | Circuit Breaker (Fowler) | https://martinfowler.com/bliki/CircuitBreaker.html |
| S-RETRY | Retry guidance (AWS Well-Architected) | https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/reliability-pillar.retry.html |
| S-EXACTLYONCE | Kafka Exactly-Once Semantics | https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/ |

## Analytics and ML/LLM

| ID | Title | Reference |
|----|-------|-----------|
| S-MAPREDUCE | MapReduce (Dean-Ghemawat 2004) | https://research.google/pubs/pub62/ |
| S-LAMBDA | Lambda Architecture (Marz) | https://www.databricks.com/glossary/lambda-architecture |
| S-VECTORDB | Vector databases overview (Pinecone learning) | https://www.pinecone.io/learn/vector-database/ |
| S-RAG | Retrieval-Augmented Generation (Lewis et al. 2020) | https://arxiv.org/abs/2005.11401 |

## General

| ID | Title | Reference |
|----|-------|-----------|
| S-CC | Contributor Covenant 2.1 | https://www.contributor-covenant.org/version/2/1/code_of_conduct/ |
| S-WA | AWS Well-Architected Framework | https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html |
| S-AZUREWA | Microsoft Azure Well-Architected Framework | https://learn.microsoft.com/azure/architecture/framework/ |
| S-GCPSRE | Google SRE Book | https://sre.google/sre-book/table-of-contents/ |
