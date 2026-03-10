# RiNALMo Hardening Audit — Phase 1 / Subphase 1

## 1. Audit Scope
This document records the frozen upstream baseline and the initial engineering audit before any major refactor.

## 2. Upstream Baseline
- Repository: lbcb-sci/RiNALMo
- Frozen branch: upstream/main
- Frozen commit: 2c2c5c14a5ae609d8c560a5d9ca32e51e0288955
- Local freeze tag: freeze/upstream-main-20260310
- Audit date: 2026-03-10

## 3. Current Top-Level Structure
Observed at repository root:
- ft_schedules/
- imgs/
- rinalmo/
- LICENSE
- README.md
- environment.yml
- pyproject.toml
- train_expression_level.py
- train_ncrna_classification.py
- train_ribosome_loading.py
- train_sec_struct_prediction.py
- train_splice_site_prediction.py
- train_translation_efficiency.py

## 4. Current Python Package Structure
Observed inside `rinalmo/`:
- data/
- model/
- resources/
- utils/
- config.py
- pretrained.py

Observed inside `rinalmo/model/`:
- attention.py
- downstream.py
- model.py
- modules.py
- rope.py

## 5. Components Classified as KEEP (for now)
These parts are treated as baseline scientific implementation and will not be rewritten in Subphase 1:
- rinalmo/model/attention.py
- rinalmo/model/model.py
- rinalmo/model/modules.py
- rinalmo/model/rope.py
- rinalmo/data/alphabet.py
- rinalmo/pretrained.py
- ft_schedules/*

## 6. Components Classified as AUDIT-ONLY (for now)
These parts are not rewritten yet, but will likely be refactored later:
- train_sec_struct_prediction.py
- train_splice_site_prediction.py
- train_ribosome_loading.py
- train_translation_efficiency.py
- train_expression_level.py
- train_ncrna_classification.py
- rinalmo/model/downstream.py
- rinalmo/config.py
- rinalmo/utils/*
- most task/data glue code

## 7. Missing Engineering Layers
The following engineering layers are not clearly present in the current repo layout:
- tests/
- configs/
- scripts/ops/
- docs/engineering/
- centralized training runtime abstraction
- centralized checkpoint/resume abstraction
- centralized experiment config system

## 8. Immediate Risks Identified
- Training/evaluation entrypoints are script-centric and top-level.
- Repository structure is research-oriented rather than production-oriented.
- No obvious standardized engineering docs directory is present.
- No obvious top-level automated test layout is present.

## 9. Subphase 1 Output
This subphase is complete when:
- upstream baseline is frozen
- hardening branch exists
- AUDIT.md exists
- DECISIONS.md exists
