# Phase 3 Launch Checklist

## Data readiness
- [ ] Full raw-source registration completed on the actual host
- [ ] data/raw/manifest.json exists and passes integrity checks
- [ ] LMDB build corresponds to the intended launch corpus
- [ ] cluster metadata is available for the intended launch dataset

## Runtime readiness
- [ ] Clean install in the active environment
- [ ] PYTHONPATH / bootstrap path verified
- [ ] GPU visibility verified on the target H200 device(s)
- [ ] Disk capacity checked for checkpoints and logs
- [ ] Checkpoint restore verified from last.ckpt
- [ ] run_summary.json is written correctly

## Training-policy freeze
- [ ] MLM masking path remains enabled
- [ ] crop path remains enabled
- [ ] cluster-aware sampling remains enabled
- [ ] warmup + cosine scheduler remains enabled
- [ ] gradient clipping remains enabled

## Validation gates
- [ ] tiny pretrain run passed
- [ ] subset pretrain run passed
- [ ] GPU dryrun passed
- [ ] at least one longer dryrun completed on the intended H200 path

## Launch decision
- [ ] Candidate launch approved
- [ ] Full paper-scale launch approved
