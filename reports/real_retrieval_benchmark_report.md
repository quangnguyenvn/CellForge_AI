# Real Retrieval Benchmark Report

This benchmark validates retrieval over Gemini-extracted real-paper evidence, not the mock corpus.

## Summary

- Cases: `12`
- Paper recall@5: `1.0`
- Claim recall@5: `1.0`
- Paper MRR: `1.0`
- Claim MRR: `1.0`
- Hard negative rate@5: `0.15`

## Cases

| Case | Paper recall | Claim recall | Paper MRR | Claim MRR | Retrieved papers | Retrieved claims |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| real_ret_001 | 1.000 | 1.000 | 1.000 | 1.000 | real:P044, real:P086, real:P075, real:P123, real:P096 | real:C044_01, real:C086_01, real:C075_01, real:C107_01, real:C123_01 |
| real_ret_002 | 1.000 | 1.000 | 1.000 | 1.000 | real:P075, real:P044, real:P086, real:P110, real:P096 | real:C075_01, real:C086_01, real:C044_01, real:C110_01, real:C096_01 |
| real_ret_003 | 1.000 | 1.000 | 1.000 | 1.000 | real:P081, real:P110, real:P099, real:P096, real:P086 | real:C081_01, real:C107_01, real:C099_01, real:C096_01, real:C086_01 |
| real_ret_004 | 1.000 | 1.000 | 1.000 | 1.000 | real:P086, real:P044, real:P110, real:P075, real:P096 | real:C086_01, real:C075_01, real:C044_01, real:C110_01, real:C107_01 |
| real_ret_005 | 1.000 | 1.000 | 1.000 | 1.000 | real:P096, real:P110, real:P099, real:P075, real:P107 | real:C096_01, real:C099_01, real:C110_01, real:C107_02, real:C075_01 |
| real_ret_006 | 1.000 | 1.000 | 1.000 | 1.000 | real:P099, real:P110, real:P107, real:P086, real:P081 | real:C099_01, real:C107_02, real:C107_01, real:C086_01, real:C081_01 |
| real_ret_007 | 1.000 | 1.000 | 1.000 | 1.000 | real:P107, real:P099, real:P110, real:P096, real:P081 | real:C107_01, real:C107_02, real:C099_01, real:C110_01, real:C044_01 |
| real_ret_008 | 1.000 | 1.000 | 1.000 | 1.000 | real:P107, real:P099, real:P110, real:P096, real:P086 | real:C107_02, real:C099_01, real:C110_01, real:C096_01, real:C107_01 |
| real_ret_009 | 1.000 | 1.000 | 1.000 | 1.000 | real:P110, real:P096, real:P086, real:P075, real:P044 | real:C110_01, real:C096_01, real:C086_01, real:C075_01, real:C107_02 |
| real_ret_010 | 1.000 | 1.000 | 1.000 | 1.000 | real:P123, real:P075, real:P044, real:P086, real:P107 | real:C123_01, real:C075_01, real:C044_01, real:C086_01, real:C096_01 |
| real_ret_011 | 1.000 | 1.000 | 1.000 | 1.000 | real:P096, real:P110, real:P099, real:P081, real:P107 | real:C110_01, real:C099_01, real:C096_01, real:C081_01, real:C107_02 |
| real_ret_012 | 1.000 | 1.000 | 1.000 | 1.000 | real:P086, real:P075, real:P044, real:P110, real:P096 | real:C086_01, real:C075_01, real:C044_01, real:C123_01, real:C110_01 |
