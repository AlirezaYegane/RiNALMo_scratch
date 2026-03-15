# Pre-Booking Data Audit

## Goal
Verify which canonical pretraining raw sources are actually present on server before any booked H200 run.

## Canonical raw sources found
- RNAcentral: /Datasets/mh/bio/rinalmo/original/rnacentral_active.fasta
  - records: 30,191,670
- Rfam: /Datasets/mh/bio/rinalmo/original/Rfam.fa
  - records: 3,132,784

## Canonical raw total
- TOTAL_CANONICAL_RAW: 33,324,454

## Important finding
A previous 66.5M count was invalid for reporting because it double-counted original and p_length derivatives:
- /Datasets/mh/bio/rinalmo/p_length/rnacentral_active.fasta
- /Datasets/mh/bio/rinalmo/p_length/Rfam.fa

These derivative files must not be counted as separate raw sources.

## Inventory interpretation
- nt appears in the current inventory search at:
  - /Datasets/mh/bio/rinalmo/original/nt
- Ensembl release-109 ncRNA has not been found in the current inventory.

## Conclusion
Data inventory for present canonical sources is partially validated:
- RNAcentral present
- Rfam present
- nt present in inventory
- Ensembl not found

Therefore, full paper-faithful source completeness is not yet satisfied.
Booked pretraining execution must remain blocked until data completeness and booking gates are resolved.
