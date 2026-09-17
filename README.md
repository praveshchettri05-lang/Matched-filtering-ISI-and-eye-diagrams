# Experiment 8 — Matched Filtering, ISI and Eye Diagrams

> **Digital Communication Laboratory**

## Objectives

1. Demonstrate matched-filter reception.
2. Use eye diagrams to identify noise, ISI and timing sensitivity.

## Implementation Tasks

| # | Task | Status |
|---|------|--------|
| 28 | Transmit BPSK through RRC pulse shaping and AWGN | ✅ |
| 29 | Apply the matched RRC filter and compensate filter delay | ✅ |
| 30 | Vary SNR, roll-off, span and sampling offset | ✅ |
| 31 | Introduce a multipath ISI channel | ✅ |

## Required Visualisations

- [x] Transmit / matched-filter output
- [x] Eye diagrams (vs SNR, roll-off, span, multipath)
- [x] Eye height versus SNR
- [x] BER versus timing offset

## Project Structure

```
.
├── experiment8_main.m       # Main script — run this to generate all results
├── design_rrc_filter.m      # Root Raised Cosine filter design (no toolbox)
├── plot_eye_diagram.m       # Reusable eye-diagram plotting function
├── measure_eye_height.m     # Eye-height measurement utility
├── results/                 # Auto-generated PNG figures (after running)
├── .gitignore
└── README.md
```

## How to Run

1. Open MATLAB (R2014b or later recommended).
2. Set the **Current Folder** to this project directory.
3. Run:
   ```matlab
   experiment8_main
   ```
4. All eight figures are displayed and saved to the `results/` folder.

> **Note:** No additional toolboxes are required.  The Communications Toolbox and Signal Processing Toolbox are **not** needed — the RRC filter and eye-diagram function are implemented from first principles.

## What the Code Does

### Task 28 — BPSK + RRC + AWGN
- Generates 10 000 random BPSK symbols (±1).
- Up-samples by 8× and applies a 97-tap Root Raised Cosine (RRC) pulse-shaping filter (β = 0.35, span = 6 symbols).
- Adds AWGN at a specified Eb/N₀.
- **Figure 1:** Transmitted and received waveforms.

### Task 29 — Matched Filter + Delay Compensation
- Applies the matched RRC filter to the noisy received signal.
- **Mandatory validation:**
  - Confirms the total cascade delay (2 × span × sps = 96 samples = 12 symbols).
  - Shows that detected symbols are taken **only after** delay removal.
  - Plots the Raised Cosine pulse (RRC ∗ RRC) to verify zero ISI at kT.
- Computes BER and compares with the theoretical value Q(√(2·Eb/N₀)).
- **Figure 2:** MF output with sampling instants, TX vs detected symbols, RC pulse.

### Task 30 — Parameter Variations
- **30a:** Eye diagrams at Eb/N₀ = 0, 5, 10, 20 dB → **Figure 3**
- **30b:** Eye height vs Eb/N₀ (0–20 dB sweep) → **Figure 4**
- **30c:** BER vs timing offset (at 8 dB) → **Figure 5**
- **30d:** Eye diagrams for β = 0.10, 0.25, 0.50, 0.90 → **Figure 6**
- **30e:** Eye diagrams for span = 2, 4, 6, 10 symbols → **Figure 7**

### Task 31 — Multipath ISI Channel
- Tests four channel conditions at Eb/N₀ = 15 dB:
  1. No ISI (reference)
  2. Mild ISI (α = 0.3, delay = 1T)
  3. Severe ISI (α = 0.7, delay = 1T)
  4. Two-path ISI (α₁ = 0.5 at 0.5T, α₂ = 0.3 at 1T)
- **Figure 8:** Eye diagrams for each channel, with BER comparison.

## Key Observations

| Parameter | Expected Effect | Verified? |
|-----------|----------------|-----------|
| ↑ Eb/N₀ | Wider eye, lower BER | ✅ |
| ↑ Roll-off β | Wider eye, more bandwidth | ✅ |
| ↑ Filter span | Less truncation ISI | ✅ |
| Timing offset ≠ 0 | Increased BER | ✅ |
| Multipath echoes | Eye closure, ISI | ✅ |

## Theoretical Background

- **RRC Filter:** The Root Raised Cosine pulse is designed so that the cascade of two identical RRC filters (transmit + matched) produces a Raised Cosine pulse that satisfies the Nyquist ISI-free criterion.
- **Matched Filter:** Maximises the output SNR for a known pulse shape in AWGN.
- **Eye Diagram:** A visual tool that overlays successive symbol-period segments of the received signal. A wide-open "eye" indicates good detection margin; a closed eye indicates high ISI or noise.

## Requirements

- **MATLAB R2014b** or later (for plot transparency support)
- No additional toolboxes

## License

This project is provided for educational purposes as part of the Digital Communication Laboratory coursework.
