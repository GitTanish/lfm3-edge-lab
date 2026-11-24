# Benchmark results

18 measurements across 8 configurations.

| Experiment | Quant | Spec | Ctx | Workload | Prefill tok/s | Decode tok/s | IQR | Accept % | RSS MB |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | json | 21.95 | 9.53 | 0.52 | — | 1326.0 |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | tool | 22.45 | 10.91 | 0.3 | — | 1320.5 |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | reasoning | 21.4 | 8.9 | 0.91 | — | 1118.8 |
| QAD-Q4_0-2K | Q4_0 | none | 2048 | prose | 21.22 | 11.01 | 0.52 | — | 1118.2 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | json | 13.51 | 9.79 | 1.12 | — | 1377.8 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | tool | 14.92 | 9.63 | 0.67 | — | 1186.9 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | reasoning | 15.25 | 11.26 | 0.84 | — | 1198.4 |
| PTQ-Q4_K_M-2K | Q4_K_M | none | 2048 | prose | 13.67 | 9.52 | 1.47 | — | 1162.3 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | json | 16.1 | 6.63 | 0.87 | — | 2065.4 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | tool | 20.62 | 8.64 | 0.17 | — | 1907.2 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | reasoning | 24.16 | 9.29 | 0.28 | — | 1917.7 |
| PTQ-Q8_0-2K | Q8_0 | none | 2048 | prose | 23.94 | 9.38 | 0.18 | — | 1911.0 |
| QAD-Q4_0-4K | Q4_0 | none | 4096 | json | 18.69 | 8.98 | 0.44 | — | 1353.2 |
| QAD-Q4_0-8K | Q4_0 | none | 8192 | json | 25.64 | 12.0 | 0.14 | — | 1408.4 |
| QAD-Q4_0-16K | Q4_0 | none | 16384 | json | 25.95 | 11.96 | 0.21 | — | 1517.5 |
| QAD-Q4_0-32K | Q4_0 | none | 32768 | json | 25.43 | 12.02 | 0.39 | — | 1737.2 |
| QAD-Q4_0-ngram | Q4_0 | ngram-simple | 2048 | json | 26.5 | 12.27 | 0.08 | — | 1588.2 |
| QAD-Q4_0-ngram | Q4_0 | ngram-simple | 2048 | tool | 23.06 | 15.57 | 0.13 | 49.1 | 1665.6 |
