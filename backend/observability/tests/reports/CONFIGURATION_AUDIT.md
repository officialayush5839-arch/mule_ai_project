# Phase 2: Configuration Verification

## Objective
Verify SigNoz configuration.

## Evidence
Inspected `backend/observability/config/otel_config.py`.
OTEL_EXPORTER_OTLP_ENDPOINT, SIGNOZ_API_KEY, SIGNOZ_SERVICE_NAME are read from env.

## Status
**VERIFIED**
