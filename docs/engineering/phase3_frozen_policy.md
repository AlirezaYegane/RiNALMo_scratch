# Phase 3 Frozen Policy

Until explicitly changed for a paper-scale launch, the launch candidate should preserve:
- MLM masking behavior
- 1024-token pretraining crop path
- one-per-cluster-per-epoch sampling
- warmup + cosine learning-rate scheduling
- gradient clipping
- checkpoint + resume-safe runtime behavior

This file freezes the intended launch policy at the end of Phase 2.
