# Experiment 9 — ASK & BFSK Simulator

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-orange?logo=numpy)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-green)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Digital Communication Laboratory — Experiment 9**  
> A complete, self-contained Python simulator for **Binary ASK (OOK)** and **Binary FSK (BFSK)** modulation, channel, and detection, with all required visualisations and the mandatory orthogonality validation.

---

## Table of Contents

1. [Overview](#overview)  
2. [Theory](#theory)  
3. [Features](#features)  
4. [Project Structure](#project-structure)  
5. [Installation](#installation)  
6. [Quick Start](#quick-start)  
7. [Simulation Parameters](#simulation-parameters)  
8. [Generated Figures](#generated-figures)  
9. [Mandatory Validation](#mandatory-validation)  
10. [Observation & Interpretation](#observation--interpretation)  
11. [How the Code Works](#how-the-code-works)  
12. [BER Formulae Reference](#ber-formulae-reference)  
13. [FAQ](#faq)  
14. [License](#license)

---

## Overview

This simulator covers every step of a digital communication chain:

```
Bit Stream → Modulator → AWGN Channel → Receiver → BER Estimation
```

Two modulation schemes are implemented:

| Scheme | Description |
|--------|-------------|
| **ASK** | On-Off Keying (OOK): amplitude is `A1` for bit-1, `0` for bit-0 |
| **BFSK** | Binary FSK: frequency is `f1` for bit-1, `f2` for bit-0 (continuous phase) |

Two receiver types are compared:

| Receiver | ASK | BFSK |
|----------|-----|------|
| **Coherent** | Single correlator + threshold | Dual correlator, decide max |
| **Noncoherent** | Envelope detector | Energy detector (squared correlators) |

---

## Theory

### 1 · ASK (On-Off Keying)

$$
s(t) = A_k \cos(2\pi f_c t), \quad A_k \in \{A_1, 0\}, \quad 0 \le t \le T_b
$$

The coherent receiver correlates with $\cos(2\pi f_c t)$:

$$
z = \int_0^{T_b} r(t)\cos(2\pi f_c t)\,dt
$$

**BER (Coherent OOK):**

$$
P_e = Q\!\left(\sqrt{\frac{E_b}{N_0}}\right)
$$

**BER (Noncoherent OOK — approximate):**

$$
P_e \approx \tfrac{1}{2}\exp\!\left(-\frac{E_b}{4N_0}\right)
$$

---

### 2 · BFSK (Binary Frequency Shift Keying)

$$
s_k(t) = \cos(2\pi f_k t + \phi_k), \quad f_k \in \{f_1, f_2\}
$$

With *continuous-phase* BFSK the phase $\phi_k$ is inherited from the previous bit to ensure no abrupt phase jumps (better spectral efficiency).

**BER (Coherent BFSK):**

$$
P_e = Q\!\left(\sqrt{\frac{E_b}{N_0}}\right)
$$

**BER (Noncoherent BFSK):**

$$
P_e = \tfrac{1}{2}\exp\!\left(-\frac{E_b}{2N_0}\right)
$$

---

### 3 · Orthogonality Condition

Two BFSK basis signals are orthogonal when their inner product over one bit interval is zero:

$$
\langle \phi_1, \phi_2 \rangle
= \int_0^{T_b} \cos(2\pi f_1 t)\cos(2\pi f_2 t)\,dt
= \frac{T_b}{2}\,\text{sinc}\!\left[(f_1-f_2)T_b\right]\cos\!\left[\pi(f_1+f_2)T_b\right]
$$

This equals **zero** when:

$$
\boxed{\Delta f \cdot T_b = \frac{k}{2}, \quad k = 1, 2, 3, \ldots}
$$

The minimum tone spacing for orthogonality is $\Delta f = \frac{R_b}{2}$.

---

## Features

- ✅ **Passband waveform generation** — ASK and continuous-phase BFSK  
- ✅ **AWGN channel** — parameterised by Eb/N0  
- ✅ **Coherent correlator receiver** — ASK (single) and BFSK (dual)  
- ✅ **Noncoherent receiver** — envelope (ASK) and energy/squared-envelope (BFSK)  
- ✅ **Power Spectral Density** via Welch's method  
- ✅ **Correlator output time traces** per bit  
- ✅ **Decision-statistic histograms** — visualise class overlap  
- ✅ **Monte-Carlo BER curves** vs Eb/N0 with theoretical overlay  
- ✅ **Mandatory orthogonality validation** — tabulated inner products  
- ✅ **Tone-spacing BER sweep** — observe degradation away from orthogonal Δf  
- ✅ All parameters in one `SimParams` class for easy experimentation  

---

## Project Structure

```
9 ASK/
├── ask_fsk_simulator.py      ← Main simulation script (all-in-one)
├── README.md                 ← This file
├── THEORY.md                 ← Detailed derivations and background
├── OBSERVATIONS.md           ← Observation & interpretation template
├── requirements.txt          ← Python package requirements
├── LICENSE                   ← MIT License
└── figures/                  ← Auto-generated output PNGs
    ├── fig1_passband_waveforms.png
    ├── fig2_power_spectra.png
    ├── fig3_correlator_outputs.png
    ├── fig4_decision_histograms.png
    ├── fig5_ber_curves.png
    ├── fig6_orthogonality.png
    └── fig7_tone_spacing_ber.png
```

---

## Installation

### Prerequisites

- Python 3.9 or later  
- `pip` (usually bundled with Python)

### Steps

```bash
# 1. Clone or download this folder
git clone https://github.com/<your-username>/ask-fsk-simulator.git
cd ask-fsk-simulator

# 2. (Recommended) Create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Quick Start

```bash
python ask_fsk_simulator.py
```

The script will:

1. Print simulation parameters and the orthogonality table  
2. Run Monte-Carlo BER simulations (~30 s on a modern laptop)  
3. Display all 7 figures  
4. Save PNGs to the current directory  

---

## Simulation Parameters

All parameters live in the `SimParams` class at the top of `ask_fsk_simulator.py`.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `Rb` | 1 000 bps | Bit rate |
| `sps` | 200 | Samples per bit (oversampling) |
| `fc` | 8 000 Hz | ASK carrier frequency |
| `f1` | 7 000 Hz | BFSK mark frequency (bit = 1) |
| `f2` | 9 000 Hz | BFSK space frequency (bit = 0) |
| `ask_A1` | 1.0 | ASK amplitude for bit-1 |
| `ask_A0` | 0.0 | ASK amplitude for bit-0 (OOK) |
| `Nbits` | 256 | Bits per BER Monte-Carlo run |
| `SNR_dB_range` | −4 … 14 dB | Eb/N0 sweep range |

**Example — change to minimum-shift BFSK (Δf·Tb = 0.5):**

```python
p.f1 = 7_500   # Hz
p.f2 = 8_500   # Hz
# Δf = 1000 Hz = Rb, so Δf·Tb = 1.0  (still orthogonal, k=2)
```

---

## Generated Figures

| Figure | Title | What to observe |
|--------|-------|-----------------|
| **Fig 1** | Passband Waveforms | Amplitude switching (ASK) vs frequency switching (BFSK) |
| **Fig 2** | Power Spectra | ASK has spectral components at fc only; BFSK at f1 and f2 |
| **Fig 3** | Correlator Outputs | Decision statistics per bit; separation vs noise |
| **Fig 4** | Decision Histograms | Overlap of bit-0/bit-1 distributions → BER |
| **Fig 5** | BER Curves | Coherent better than noncoherent; theory vs simulation |
| **Fig 6** | Orthogonality | Inner product zeros at Δf·Tb = k/2 |
| **Fig 7** | Tone-Spacing BER | Lower BER near orthogonal spacings |

---

## Mandatory Validation

The simulator automatically computes and prints:

```
┌──────────────────────────────────────────────┐
│  BFSK Orthogonality Condition Verification   │
│  ⟨φ₁, φ₂⟩ at Δf = k·Rb/2                   │
├───────┬─────────────┬────────────────────────┤
│  k    │ Δf·Tb       │ ⟨φ₁,φ₂⟩               │
├───────┼─────────────┼────────────────────────┤
│  1    │ 0.5         │ ≈ 0.0  ✓ ORTHOGONAL    │
│  2    │ 1.0         │ ≈ 0.0  ✓ ORTHOGONAL    │
│  3    │ 1.5         │ ≈ 0.0  ✓ ORTHOGONAL    │
│  4    │ 2.0         │ ≈ 0.0  ✓ ORTHOGONAL    │
│  5    │ 2.5         │ ≈ 0.0  ✓ ORTHOGONAL    │
└───────┴─────────────┴────────────────────────┘
```

---

## Observation & Interpretation

Fill in [OBSERVATIONS.md](OBSERVATIONS.md) **before and after** running each parameter variation.

| Experiment | Expected | Observed | Agreement? |
|------------|----------|----------|------------|
| ASK coherent BER | $Q(\sqrt{E_b/N_0})$ | From Fig 5 | |
| BFSK at Δf·Tb=0.5 | Orthogonal (IP≈0) | From Fig 6 | |
| Δf reduced (non-orthogonal) | BER ↑ | From Fig 7 | |

---

## How the Code Works

```
ask_fsk_simulator.py
│
├── SimParams          — all configurable parameters
├── generate_bits()    — random bit stream
├── bits_to_nrz()      — NRZ upsampling
│
├── modulate_ask()     — OOK passband waveform
├── modulate_bfsk()    — continuous-phase BFSK waveform
│
├── add_awgn()         — AWGN channel (Eb/N0 parameterised)
│
├── correlator_ask()        — coherent ASK receiver
├── correlator_bfsk()       — coherent BFSK dual-correlator
├── envelope_detector_ask() — noncoherent ASK (Hilbert envelope)
├── energy_detector_bfsk()  — noncoherent BFSK (squared correlators)
│
├── validate_fsk_orthogonality() — inner product sweep + table
├── ber_simulation()             — Monte-Carlo BER
├── ber_theory()                 — analytical BER expressions
├── compute_psd()                — Welch PSD
│
└── plot_*()           — one function per figure
```

---

## BER Formulae Reference

| Scheme | BER Formula |
|--------|-------------|
| ASK Coherent | $Q\!\left(\sqrt{E_b/N_0}\right)$ |
| ASK Noncoherent | $\tfrac{1}{2}e^{-E_b/(4N_0)}$ |
| BFSK Coherent | $Q\!\left(\sqrt{E_b/N_0}\right)$ |
| BFSK Noncoherent | $\tfrac{1}{2}e^{-E_b/(2N_0)}$ |

Where $Q(x) = \frac{1}{2}\text{erfc}\!\left(\frac{x}{\sqrt{2}}\right)$

> **Note:** ASK and coherent BFSK have the same BER formula, but ASK's average energy per bit is *lower* (OOK transmits nothing for bit-0), so at the same Eb/N0 they perform equivalently. Noncoherent BFSK has a 3 dB advantage over noncoherent ASK.

---

## FAQ

**Q: Why does the BER simulation differ slightly from theory?**  
A: Finite sample size (Nbits=256). Increase `p.Nbits` to 10 000+ for tighter agreement at the cost of longer runtime.

**Q: What is continuous-phase BFSK?**  
A: The phase is accumulated continuously across bit boundaries — no discontinuities. This reduces spectral sidelobes. Set `p.sps` high enough that the phase integration is accurate.

**Q: How do I change the bit rate?**  
A: Change `p.Rb`. The script automatically recomputes `Tb`, `fs`, and all derived quantities.

**Q: How do I save figures to a subfolder?**  
A: Change the `path = f"{name}.png"` line in `main()` to `path = f"figures/{name}.png"` and create the `figures/` directory first.

---

## License

MIT © 2026 — see [LICENSE](LICENSE).
