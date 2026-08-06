# Thesis-aligned LLM annotation prompt

Classify one disaster-related post using only the supplied text and metadata.
Do not infer facts that are not supported by the source.

## Thesis-core output fields

Return strict JSON containing the five analytical fields documented in Thesis
Section 5.2.2, together with basic record metadata:

```json
{
  "post_id": "string",
  "timestamp": "ISO-8601 timestamp or null",
  "language": "language code",
  "location": "specific place, Regional, Unknown, or null",
  "needs_category": "Evacuation | Infrastructure failure | Health risk | Resource request | Information",
  "severity_score": 1,
  "sentiment": "anxiety | anger | desperation | gratitude | neutral | other",
  "summary": "concise source-grounded summary"
}
```

## Optional repository audit fields

The public repository may additionally retain the following fields for
traceability. These are audit additions aligned with the thesis logic; they are
not presented as a verbatim copy of the original thesis schema.

```json
{
  "response_type": "demand | response | information",
  "geocoding_cue": "text span or metadata field supporting the location",
  "confidence": 0.0,
  "rationale": "short source-grounded explanation"
}
```

## Decision rules

1. Do not invent a location. Use `Unknown` when no usable assignment is supported.
2. `location` means usable spatial assignment, not necessarily device GPS.
3. Distinguish digitally visible demand/response information from operational deployment.
4. Use `Health risk` for contamination, sewage, infection, or stagnant-water concerns.
5. Use `Information` for warnings or reporting without a direct need or response action.
6. `severity_score` is ordinal and must lie from 1 to 10.
7. Preserve uncertainty in the optional `confidence` field.
8. Do not retain personal identifiers in the analytical output.
