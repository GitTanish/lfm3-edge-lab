# Benchmark results

18 measurements across 8 configurations.

| Experiment | Quant | Spec | Ctx | Workload | Prefill tok/s | Decode tok/s | Accept | RSS MB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | json | 78.22 | 8.12 | — | 1318.4 |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | tool | 83.86 | 8.78 | — | 1329.9 |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | reasoning | 64.0 | 10.08 | — | 1339.7 |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | prose | 53.21 | 9.96 | — | 1347.7 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | json | 68.9 | 12.99 | — | 1370.2 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | tool | 77.58 | 12.94 | — | 1382.0 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | reasoning | 58.83 | 12.95 | — | 1391.7 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | prose | 47.89 | 13.36 | — | 1399.7 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | json | 56.67 | 8.97 | — | 2113.2 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | tool | 66.8 | 9.15 | — | 2124.7 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | reasoning | 47.44 | — | — | 2134.4 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | prose | 34.1 | 9.07 | — | 2137.1 |
| QAD-Q4_0-4K | Q4_0 | none | 4096 | json | 91.48 | 11.4 | — | 1345.6 |
| QAD-Q4_0-8K | Q4_0 | none | 8192 | json | 86.13 | 11.4 | — | 1400.2 |
| QAD-Q4_0-16K | Q4_0 | none | 16384 | json | 88.89 | 11.2 | — | 1510.4 |
| QAD-Q4_0-32K | Q4_0 | none | 32768 | json | 91.83 | 11.47 | — | 1729.6 |
| QAD-Q4_0-ngram | Q4_0 | ngram-simple | 2048 | json | 92.16 | 7.99 | 0.026 | 1634.0 |
| QAD-Q4_0-ngram | Q4_0 | ngram-simple | 2048 | tool | 103.99 | 16.3 | 0.598 | 1648.6 |
