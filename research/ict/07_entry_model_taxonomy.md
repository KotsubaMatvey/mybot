# Entry Model Taxonomy

## Project Taxonomy

The current project uses Sayx-style execution model names.

Preserve these names:

- Entry Model 1: Sweep -> BOS/MSS -> post-BOS FVG / imbalance.
- Entry Model 2: Sweep -> FVG Inversion / IFVG.
- Entry Model 3: Missed Entry -> Full Fill FVG / retracement -> LTF pickup.

## NotebookLM Naming Conflict

Some NotebookLM notes or ICT summaries may use different labels:

- Model 1 = OB retest.
- Model 2 = FVG entry.
- Model 3 = Turtle Soup + SMT.

Do not rename or replace the current project models with those labels.

If those concepts are useful, map them as supporting components or future strategies, not as replacements for the current Entry Model 1/2/3.

## Common Requirements

All models should carry:

- HTF metadata.
- Sweep or source-zone metadata where relevant.
- Structure and displacement metadata.
- FVG/IFVG/OB lifecycle metadata.
- Timestamp ordering metadata.
- Risk quality metadata.

## Common Rejection Rules

Reject or penalize:

- Opposite strict HTF bias.
- Neutral HTF in strict Model 3.
- Missing HTF context in strict mode.
- Missing required sweep for Model 1 and Model 2.
- Wrong timestamp ordering.
- Wick-only IFVG breach.
- Invalid or tiny risk.
- Ancient unbounded zones.
