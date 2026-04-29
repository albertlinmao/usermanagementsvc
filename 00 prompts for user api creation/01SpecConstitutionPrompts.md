# SpecKit Constitution: User Management API

> **Prompt:** `/speckit.constitution Create a SpecKit Constitution for an enterprise-grade User Management API used to provide share user management as shared service at scale. code quality, testing standards, user experience consistency, and performance requirements.`

## 1. Backend & API Governance

### Service Boundaries
**RULE:** Supabase Edge Functions MUST encapsulate business logic. Database functions MUST handle data-intensive operations. Service boundaries MUST align with domain concepts.
**Enforcement:** Architectural review MUST validate service boundary compliance.

### API First Design
**RULE:** All functionality MUST be accessible via API. APIs MUST be designed before implementation. API contracts MUST be versioned and documented.
**Enforcement:** Code review MUST verify API coverage and contract compliance.

### API Versioning & Lifecycle
**RULE:** Semantic versioning REQUIRED for all APIs. Backward compatibility MUST be maintained for at least one major version. Deprecation notices MUST be provided 90 days in advance.
**Enforcement:** Automated tests MUST validate backward compatibility.

### Backward Compatibility Expectations
**RULE:** Breaking changes PROHIBITED without migration path. Client compatibility MUST be maintained. Additive changes are PREFERRED over modifications.
**Enforcement:** Integration tests MUST verify client compatibility.

### Idempotency & Workflow Retries
**RULE:** All state-changing operations MUST be idempotent. Retry logic MUST be implemented for network operations. Duplicate processing MUST be prevented.
**Enforcement:** Unit tests MUST validate idempotency behavior.

### Error Handling Standards
**RULE:** Structured error responses REQUIRED. Error codes MUST be consistent. Sensitive information MUST NOT be exposed in error messages.
**Enforcement:** Security scanning MUST validate error message safety.

### Query Constraints & Pagination
**RULE:** Result sets MUST be paginated. Query limits MUST be enforced. Complex queries MUST be optimized and indexed.
**Enforcement:** Performance testing MUST validate query efficiency.

### Rate Limiting & Abuse Prevention
**RULE:** Rate limiting REQUIRED for all APIs. Request quotas MUST be enforced per user. Suspicious activity MUST trigger alerts.
**Enforcement:** Load testing MUST validate rate limiting effectiveness.

## 2. Data, Storage, and Consistency Rules

### Consistency Trade-offs
**RULE:** Strong consistency REQUIRED for user state. Eventual consistency ACCEPTABLE for analytics and reporting. Read-after-write MUST be guaranteed for user operations.
**Enforcement:** Database testing MUST validate consistency behavior.

### Schema Evolution & Compatibility
**RULE:** Supabase migrations REQUIRED for schema changes. Backward compatibility MUST be maintained. Migration rollback MUST be tested.
**Enforcement:** Database migration testing MUST validate schema changes.

### Data Retention & Deletion
**RULE:** Data retention policies MUST be enforced. User data MUST be deletable on request. Audit logs MUST be retained for compliance periods.
**Enforcement:** Compliance testing MUST validate data handling policies.

### PostgreSQL Data Modeling
**RULE:** Normalized tables REQUIRED for structured data. JSONB columns ACCEPTABLE for flexible schemas. Full-text search MUST use PostgreSQL built-in capabilities.
**Enforcement:** Database review MUST validate modeling decisions.

### Caching Strategies
**RULE:** Supabase Edge Runtime caching REQUIRED for static content. Query result caching MUST be implemented for expensive operations. Cache invalidation MUST be automated.
**Enforcement:** Performance testing MUST validate caching effectiveness.

### Event-Driven Updates
**RULE:** Supabase Realtime REQUIRED for live updates. Database triggers MUST enforce business rules. Event sourcing MUST be used for audit trails.
**Enforcement:** Integration testing MUST validate event-driven behavior.

### Row Level Security (RLS)
**RULE:** RLS policies REQUIRED for all user data. Least privilege access MUST be enforced. Policy testing MUST cover all user roles.
**Enforcement:** Security testing MUST validate RLS policy effectiveness.

### User Identity & State Management
**RULE:** Supabase Auth REQUIRED for all user identity. Onboarding state MUST be stored in Supabase Database. User sessions MUST be managed via Supabase Auth tokens.
**Enforcement:** Security review MUST validate identity management compliance.

## 3. Security & Compliance Constitution

### Authentication & Authorization
**RULE:** Supabase Auth with RBAC REQUIRED. Least privilege access MUST be enforced. Multi-factor authentication REQUIRED for elevated privileges.
**Enforcement:** Security audit MUST validate authentication compliance.

### Corporate IAM Integration
**RULE:** SSO integration REQUIRED via Supabase Auth providers. Corporate directory sync MUST be maintained. User provisioning MUST be automated.
**Enforcement:** Integration testing MUST validate IAM connectivity.

### Employee PII Handling
**RULE:** PII encryption REQUIRED at rest and in transit. Data access MUST be logged. PII exposure MUST be minimized.
**Enforcement:** Compliance audit MUST validate PII handling.

### Secrets Management
**RULE:** Supabase Vault integration REQUIRED for secrets. Environment variables MUST be encrypted. Secret rotation MUST be automated.
**Enforcement:** Security scanning MUST validate secret management.

### Secure Tool Integration
**RULE:** All integrations MUST use OAuth 2.0 or API keys. Token storage MUST be secure. Integration permissions MUST be minimal.
**Enforcement:** Security review MUST validate integration security.

### Logging & Audit Trails
**RULE:** Comprehensive logging REQUIRED for all actions. Audit logs MUST be immutable. Log retention MUST meet compliance requirements.
**Enforcement:** Compliance testing MUST validate audit trail completeness.

### Threat Modeling
**RULE:** Threat models REQUIRED for all features. Security testing MUST be automated. Vulnerability scanning MUST be continuous.
**Enforcement:** Security review MUST validate threat model coverage.

## 4. Reliability, Performance, and Resilience

### Availability Targets & SLOs
**RULE:** 99.9% uptime REQUIRED for core onboarding functions. 99.5% uptime ACCEPTABLE for analytics. SLO breaches MUST trigger automatic alerts.
**Enforcement:** SLO monitoring MUST validate availability targets.

### Performance Expectations
**RULE:** 95th percentile response time < 2 seconds. Database queries < 100ms. Page load time < 3 seconds.
**Enforcement:** Performance monitoring MUST validate response times.

### Graceful Degradation
**RULE:** Core functionality MUST remain available during outages. Cached content MUST serve when live data unavailable. User feedback MUST be provided during degradation.
**Enforcement:** Chaos testing MUST validate degradation behavior.

### Retry & Circuit Breaker Behavior
**RULE:** Exponential backoff REQUIRED for retries. Circuit breakers MUST prevent cascade failures. Retry limits MUST be enforced.
**Enforcement:** Failure simulation testing MUST validate resilience patterns.

### Disaster Recovery & Backup
**RULE:** Automated daily backups REQUIRED. Point-in-time recovery MUST be tested quarterly. Disaster recovery plans MUST be documented.
**Enforcement:** Recovery testing MUST validate backup effectiveness.

### Onboarding Spike Handling
**RULE:** Auto-scaling REQUIRED for load spikes. Queue-based processing REQUIRED for batch operations. Rate limiting MUST prevent overload.
**Enforcement:** Load testing MUST validate spike handling capacity.

## 5. Observability & Operability

### Structured Logging Standards
**RULE:** JSON format REQUIRED for all logs. Correlation IDs MUST be included. Log levels MUST be consistent across services.
**Enforcement:** Log analysis MUST validate structured logging compliance.

### Metrics for Onboarding Health
**RULE:** Completion rates MUST be tracked. Time-to-productivity MUST be measured. User satisfaction MUST be monitored.
**Enforcement:** Dashboard monitoring MUST validate metric collection.

### Distributed Tracing
**RULE:** Request tracing REQUIRED across services. Performance bottlenecks MUST be identifiable. Trace sampling MUST be configurable.
**Enforcement:** Trace analysis MUST validate tracing coverage.

### Alerting Thresholds & Escalation
**RULE:** Critical alerts MUST trigger within 5 minutes. Escalation paths MUST be documented. Alert fatigue MUST be prevented.
**Enforcement:** Incident response testing MUST validate alerting effectiveness.

### Dashboards for Stakeholders
**RULE:** Real-time dashboards REQUIRED for platform health. Business metrics MUST be visible to leaders. Technical metrics MUST be available to engineers.
**Enforcement:** Dashboard validation MUST ensure metric accuracy.

### On-call Readiness & Runbooks
**RULE:** On-call rotation MUST be maintained. Runbooks MUST exist for all incidents. Incident post-mortems MUST be conducted.
**Enforcement:** Incident response testing MUST validate runbook effectiveness.

## 6. Engineering Practices & Delivery Guardrails

### CI/CD Requirements
**RULE:** Automated testing REQUIRED for all changes. Deployment MUST be automated. Rollback capability MUST be tested.
**Enforcement:** Pipeline validation MUST ensure CI/CD compliance.

### Test-Driven Development (TDD)
**RULE:** TDD REQUIRED for all new features. Red-Green-Refactor cycle MUST be followed. Test failures MUST drive development. Production code MUST not be written without failing tests.
**Enforcement:** Code review MUST validate TDD compliance. Test history MUST demonstrate red-to-green progression.

### Testing Strategy
**RULE:** Unit tests REQUIRED for all business logic. Integration tests REQUIRED for service boundaries. End-to-end tests REQUIRED for critical user journeys. Test coverage MUST be ≥90% for critical paths.
**Enforcement:** Test coverage analysis MUST validate testing completeness. Coverage gates MUST block deployments below threshold.

### Feature Flag & Rollout Practices
**RULE:** Feature flags REQUIRED for all deployments. Gradual rollout REQUIRED for high-risk changes. Kill switches MUST be available.
**Enforcement:** Rollout validation MUST ensure flag effectiveness.

### Environment Promotion
**RULE:** Environment parity MUST be maintained. Promotion MUST be automated. Configuration MUST be externalized.
**Enforcement:** Environment testing MUST validate promotion safety.

### Code Ownership & Review
**RULE:** Code ownership MUST be clearly defined. Peer review REQUIRED for all changes. Security review REQUIRED for sensitive changes.
**Enforcement:** Review process validation MUST ensure quality standards.

### Documentation Standards
**RULE:** API documentation MUST be auto-generated. Code comments REQUIRED for complex logic. Architecture decisions MUST be documented.
**Enforcement:** Documentation validation MUST ensure accuracy and completeness.

## 7. Decision-Making & Exception Handling

### Architectural Decision Process
**RULE:** ADRs REQUIRED for significant decisions. Technical review MUST validate decisions. Decision rationale MUST be documented.
**Enforcement:** ADR review MUST validate decision quality.

### Approval Authorities
**RULE:** Architecture board approval REQUIRED for major changes. Security team approval REQUIRED for security decisions. Product team approval REQUIRED for user-facing changes.
**Enforcement:** Approval tracking MUST validate authority compliance.

### Exception Request Process
**RULE:** Formal exception requests REQUIRED for constitutional violations. Business justification MUST be provided. Time limits MUST be enforced for exceptions.
**Enforcement:** Exception tracking MUST validate request compliance.

### Decision Traceability
**RULE:** All decisions MUST be traceable to requirements. Impact analysis MUST be conducted. Stakeholder approval MUST be documented.
**Enforcement:** Decision audit MUST validate traceability completeness.

### Transparency & Communication
**RULE:** Decisions MUST be communicated to affected teams. Rationale MUST be shared publicly. Feedback channels MUST be available.
**Enforcement:** Communication validation MUST ensure stakeholder awareness.

## 8. Validation & Enforcement

### Automated Checks
**RULE:** Constitutional compliance MUST be automated. Static analysis MUST validate code compliance. Security scanning MUST validate security compliance.
**Enforcement:** Automated validation MUST prevent non-compliant deployments.

### Design Review Gates
**RULE:** Architecture review REQUIRED for all designs. Security review REQUIRED for all changes. Performance review REQUIRED for scaling changes.
**Enforcement:** Review validation MUST ensure gate effectiveness.

### CI/CD Enforcement
**RULE:** Compliance tests MUST block deployments. Quality gates MUST be enforced. Security scans MUST be mandatory.
**Enforcement:** Pipeline validation MUST ensure enforcement effectiveness.

### Governance Audits
**RULE:** Quarterly compliance audits REQUIRED. Architecture reviews MUST be scheduled. Security assessments MUST be conducted.
**Enforcement:** Audit tracking MUST ensure review completeness.

### Compliance Ownership
**RULE:** Clear ownership REQUIRED for all compliance areas. Compliance responsibilities MUST be documented. Accountability MUST be enforced.
**Enforcement:** Ownership validation MUST ensure responsibility clarity.

### Amendments & Versioning
**RULE:** Constitutional amendments REQUIRE documented rationale. Version changes MUST follow semantic versioning. Change communication MUST be comprehensive.
**Enforcement:** Amendment tracking MUST ensure change visibility.

## Architecture & Integration Standards

### Supabase-Centric Architecture
**ALLOWED:** Supabase Auth, Database, Storage, Edge Functions, Realtime as core platform services.  
**DISCOURAGED:** Direct database connections bypassing Supabase pools, custom authentication systems.  
**PROHIBITED:** Non-Supabase databases for primary storage, external authentication providers not integrated through Supabase.

### Backend Service Boundaries
**ALLOWED:** Supabase Edge Functions for business logic, PostgreSQL functions for data-intensive operations.  
**DISCOURAGED:** External microservices for core onboarding logic, custom API gateways.  
**PROHIBITED:** Direct database writes from external services, bypassing Supabase security layers.

### API-first Approach
**ALLOWED:** RESTful APIs through Supabase Edge Functions, GraphQL via Supabase PostgREST.  
**DISCOURAGED:** SOAP APIs, custom authentication schemes.  
**PROHIBITED:** Unversioned APIs, breaking changes without migration path.

### Integration Patterns
**ALLOWED:** Webhook-based integrations, Supabase Realtime subscriptions, scheduled Edge Functions.  
**DISCOURAGED:** Synchronous integrations blocking user workflows, polling-based data sync.  
**PROHIBITED:** Direct database access from external systems, unauthenticated API calls.

### Data Ownership & Boundaries
**ALLOWED:** Row Level Security (RLS) for data access control, tenant isolation via RLS policies.  
**DISCOURAGED:** Shared data without clear ownership, cross-tenant data access.  
**PROHIBITED:** Bypassing RLS policies, direct database access with elevated privileges.
