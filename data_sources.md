# Data Sources

## Candidate Nodes (27 nodes)
All candidate nodes were provided directly in the assessment Setup Guide
(ASSESSMENT_04_SETUP_GUIDE.md) as pre-seeded SQL data.

The nodes represent synthetic clinical data for a fictional hospital
(Supra Multi-Specialty Hospital) created by Astroum AI / BRAHMO for
assessment purposes. No external clinical data sources were used.

## Node Types and Origins
| Type | Count | Source |
|------|:-----:|--------|
| CONSTRAINT | 6 | Provided in Setup Guide seed SQL |
| DECISION | 8 + 1 stale | Provided in Setup Guide seed SQL |
| ANTI_PATTERN | 4 | Provided in Setup Guide seed SQL |
| FACT | 8 | Provided in Setup Guide seed SQL |

## Token Counting
tiktoken library with `cl100k_base` encoding — open source, Apache 2.0 license.