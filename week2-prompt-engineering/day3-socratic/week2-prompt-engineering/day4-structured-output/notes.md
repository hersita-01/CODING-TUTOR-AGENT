# Day 4 Notes: Structured Outputs

Goal: make tutor replies easy for a future UI or agent loop to parse.

Required shape:

```json
{
  "diagnosis": "One sentence about the likely problem.",
  "hint": "A small nudge without giving the answer.",
  "follow_up_question": "One Socratic question.",
  "confidence": 0.75
}
```

What worked:
- Asking for exact field names reduces messy output.
- `response_format={"type": "json_object"}` helps enforce JSON when the model supports it.
- Keeping each field short makes the tutor more useful for beginners.

What to improve later:
- Validate the JSON with a schema.
- Add a retry if the model returns invalid JSON.
- Include citations once the tutor has document search.
