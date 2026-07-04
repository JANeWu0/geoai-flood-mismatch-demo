# LLM Prompt Template: Extract Flood Response Signals

You are extracting structured disaster-response information from short social media posts, news snippets, and official bulletins.

Return JSON only.

Schema:

```json
{
  "locality": "string or null",
  "signal_type": "need | response | mixed | neutral",
  "need_category": "rescue | water_sanitation | shelter | road_access | electricity | food | medical | other | null",
  "response_category": "rescue_team | pump | evacuation | shelter | food_aid | road_clearance | volunteer | official_update | other | null",
  "urgency": "low | medium | high | unknown",
  "evidence_span": "short quote from the input",
  "confidence": 0.0
}
```

Rules:

1. Do not infer a locality unless it is explicitly stated or strongly implied by a known place name.
2. If the text asks for help or reports missing aid, use `need`.
3. If the text reports responders, pumps, shelters, evacuations, or supplies, use `response`.
4. If both are present, use `mixed`.
5. Avoid personal data. Do not copy names, handles, phone numbers, or addresses.

Input:

```text
{{POST_TEXT}}
```
