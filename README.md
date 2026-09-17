# Experiment 8 — Matched Filtering, ISI & Eye Diagrams

> **Digital Communication Laboratory · Interactive Web Simulator**

A fully interactive browser-based simulator for Experiment 8. No MATLAB, no toolbox, no installation — just open `index.html` in any modern browser.

## 🚀 Live Demo

1. Clone or download this repository
2. Open **`index.html`** in Chrome, Firefox, Edge, or Safari
3. Adjust parameters with the sliders and explore all 4 tabs

> No server required — runs entirely in the browser using HTML5 Canvas and vanilla JavaScript.

## 📋 What It Covers

| Task | Description | Tab |
|------|-------------|-----|
| 28 | Transmit BPSK through RRC pulse shaping + AWGN | 📡 Signal Chain |
| 29 | Apply matched RRC filter, compensate filter delay | 📡 Signal Chain |
| 30 | Vary SNR, roll-off, span, sampling offset | 📊 Analysis |
| 31 | Introduce multipath ISI channel | 🔀 Multipath ISI |

### Required Visualisations ✅
- [x] Transmit / matched-filter output
- [x] Eye diagrams (interactive, real-time)
- [x] Eye height vs SNR
- [x] BER vs timing offset

### Mandatory Validation ✅
- Confirms total cascade delay = 2 × span × sps
- Shows detected symbols are taken **only after** delay removal
- Compares measured BER with theoretical Q(√(2·Eb/N₀))

## 🎮 Interactive Controls

| Control | Range | Effect |
|---------|-------|--------|
| Eb/N₀ | -2 to 20 dB | Noise level — affects eye opening |
| Roll-off β | 0.05 to 1.0 | Bandwidth vs timing margin trade-off |
| Filter Span | 2 to 12 symbols | RRC truncation — affects ISI |
| Timing Offset | -0.5T to +0.5T | Sampling error — degrades BER |
| Channel | 4 models | AWGN only / mild / severe / two-path ISI |
| Bits | 500–5000 | Simulation length |
| Samples/Symbol | 4, 8, 16 | Oversampling factor |

## 📁 Project Structure

```
├── index.html      # Main page — open this in a browser
├── style.css       # UI styling (responsive layout)
├── dsp.js          # DSP engine (RRC filter, convolution, AWGN, BER)
├── app.js          # Simulator + Canvas plotting + UI logic
├── README.md
└── .gitignore
```

## 🔬 Technical Details

- **RRC Filter:** Designed from the analytical impulse response formula with proper handling of singular points at t=0 and t=±1/(4β). Normalised to unit energy.
- **Eye Diagram:** Overlays 400+ signal traces with transparency on HTML5 Canvas for the classic density-based eye pattern.
- **Noise Calibration:** With unit-energy RRC, noise variance = 1/(2·Eb/N₀) gives exact theoretical BER for BPSK.
- **PRNG:** Seeded Mulberry32 for reproducible results across runs.
- **No Dependencies:** Zero external libraries — pure HTML/CSS/JS.

## 📊 Key Observations

| Parameter | Expected Effect | Verified |
|-----------|----------------|----------|
| ↑ SNR | Wider eye, lower BER | ✅ |
| ↑ Roll-off β | Wider eye, more bandwidth | ✅ |
| ↑ Filter span | Less truncation ISI | ✅ |
| Timing offset ≠ 0 | Increased BER | ✅ |
| Multipath echoes | Eye closure, ISI | ✅ |

## 🌐 Deploy to GitHub Pages

1. Push this repo to GitHub
2. Go to **Settings → Pages → Source → main branch**
3. Your simulator is live at `https://username.github.io/repo-name/`

## Requirements

- Any modern browser (Chrome 60+, Firefox 55+, Edge 79+, Safari 12+)
- No server, no build step, no dependencies

## License

Educational use — Digital Communication Laboratory coursework.
