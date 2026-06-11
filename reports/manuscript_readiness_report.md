# CellForge AI Manuscript Readiness Report

Status: `blocked_pending_human_validation`

The manuscript draft was not generated because no validated evidence items are currently allowed for manuscript use. This is intentional: CellForge AI should not convert extraction artifacts into paper claims until a human verifies them against the PDFs.

## Blocking Items

- `val:001` `real:C099_01` (critical): capacity retention = `89%` from `real:P099`
- `val:002` `real:C107_01` (critical): carbon purity = `exceeding 99.99%` from `real:P107`
- `val:003` `real:C107_02` (critical): reversible capacity = `353 mAh/g` from `real:P107`
- `val:004` `real:C110_01` (high): capacity retention = `99.1 %` from `real:P110`
- `val:005` `real:C075_01` (high): capacity retention = `77.7 %` from `real:P075`

## How To Unblock

1. Open `reports/validation_checklist.md`.
2. Verify each critical/high claim against the source PDF.
3. Update `data/validation_queue.json`: set `validation_status` to `validated` or `corrected`, and `allowed_in_manuscript` to `true` only for claims that passed.
4. Re-run `python scripts\generate_manuscript_draft.py --validated-only`.
