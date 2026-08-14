# Hindi Corpus Integration

Hindi is now a first-class category in ProX-AI.

## Collection Strategy
- Targets: 150M tokens of high-quality Hindi text.
- Heuristics: Uses Unicode block detection (`\u0900-\u097F`) coupled with stop-word verification (`है`, `और`, `में`, etc.) to distinguish Hindi from other Devanagari scripts (Marathi, Nepali).

## Code-Switching Support
The pipeline natively supports code-switched text (e.g., "Python एक programming language है।") by validating the relative density of Devanagari characters against the full string length.
