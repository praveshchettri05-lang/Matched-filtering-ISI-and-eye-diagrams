# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] — 2026-09-27

### Added
- `ask_fsk_simulator.py` — complete ASK and BFSK simulation pipeline
  - Binary ASK (OOK) modulator with configurable A1 and A0
  - Continuous-phase BFSK modulator
  - AWGN channel with Eb/N0 parameterisation
  - Coherent correlator receivers (ASK single, BFSK dual)
  - Noncoherent receivers (envelope detector, energy detector)
  - Power spectral density via Welch method
  - Monte-Carlo BER estimation
  - Theoretical BER overlays
  - FSK orthogonality validation (mandatory)
  - Tone-spacing BER sweep
  - 7 publication-quality figures (dark theme)
- `README.md` — full documentation with installation, theory, and figure guide
- `THEORY.md` — derivations of ASK and BFSK BER, orthogonality condition
- `OBSERVATIONS.md` — structured observation & interpretation template
- `requirements.txt` — Python dependencies
- `LICENSE` — MIT licence
- `CHANGELOG.md` — this file
- `.gitignore` — ignores venv, pycache, PNG outputs

---

## [Unreleased]

### Planned
- Interactive Jupyter notebook version
- M-ary FSK extension (4-FSK, 8-FSK)
- QPSK and QAM comparison
- Matched filter receiver implementation
- Eye diagram generation

---

*Format follows [Keep a Changelog](https://keepachangelog.com/).*
