# S2: Find what the report missed

**Area:** firmware. **Type:** judge. **Points:** 15. Optional.

The engine's report is not complete. The image has at least three security problems that the report does not
mention. Three proven ones earn full marks.

## What to do

Look through the image. Write what you find in `answers/S2-missed.json`:

```json
{
  "title": "Short name of the problem",
  "severity": "critical, high, medium or low",
  "path": "the file in the image that shows it",
  "shows": "what the file shows",
  "reason": "why it matters, in one or two sentences"
}
```

Add the most important ones to your review report.

## Done means

- Each entry has a file in the image that shows it.
- You list what you are sure of. A long list of guesses scores lower than a short list of proven problems.
- Each entry is a problem the report does not have. A worse side of a finding it already has belongs in
  your S1 reason.
