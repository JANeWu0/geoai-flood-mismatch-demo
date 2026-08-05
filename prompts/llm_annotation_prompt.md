# Fixed LLM annotation prompt

Classify one disaster-related post using only the supplied text and metadata.

Return strict JSON with the following fields:

```json
{
  "post_id": "string",
  "timestamp": "ISO-8601 timestamp or null",
  "language": "language code",
  "category": "Evacuation and entrapment | Infrastructure disruption | Health risk | Resource request | Information",
  "response_type": "demand | response | information",
  "place_mention": "explicit place name or null",
  "geocoding_cue": "text span or metadata field supporting the location",
  "confidence": 0.0,
  "rationale": "short source-grounded explanation"
}
```

Decision rules:

1. Do not invent a location.
2. Distinguish digitally visible demand/response information from operational deployment.
3. Use `Health risk` for contamination, sewage, infection, or stagnant-water health concerns.
4. Use `Information` for general warnings or reporting without a direct need or response action.
5. Preserve uncertainty in `confidence`.
6. Do not retain personal identifiers in the analytical output.
