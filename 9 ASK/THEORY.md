# Theory — ASK and BFSK Digital Modulation

> **Experiment 9 | Digital Communication Laboratory**

---

## 1. Introduction

**Digital modulation** is the process of encoding a discrete bit stream onto an analogue carrier signal for transmission through a bandpass channel. In this experiment we study two fundamental schemes:

- **ASK — Amplitude Shift Keying** (specifically OOK: On-Off Keying)
- **BFSK — Binary Frequency Shift Keying**

Both are *binary* (M=2) schemes that map one bit per symbol. They are the building blocks of more complex M-ary schemes used in modern communications (APSK, OFDM, etc.).

---

## 2. Signal Space Representation

Every bandpass signal over $[0, T_b]$ can be written as a linear combination of two orthonormal basis functions:

$$
\psi_1(t) = \sqrt{\frac{2}{T_b}}\cos(2\pi f_c t), \quad
\psi_2(t) = \sqrt{\frac{2}{T_b}}\sin(2\pi f_c t)
$$

The inner product (projection) of a signal onto a basis function is the decision statistic.

---

## 3. ASK — Amplitude Shift Keying

### 3.1 Modulated Signal

$$
s_k(t) = A_k \cos(2\pi f_c t), \quad 0 \le t \le T_b
$$

| Bit | Amplitude |
|-----|-----------|
| 1 (mark) | $A_1$ |
| 0 (space) | $A_0 = 0$ (OOK) |

### 3.2 Energy per Bit

$$
E_b = \frac{A_1^2 T_b}{4} \quad \text{(OOK average, assuming equal bit prob.)}
$$

### 3.3 Signal Constellation

OOK has a 1-D constellation on the $\psi_1$ axis:

```
space (0)           mark (1)
    ●─────────────────────●
    0                  √E_b
```

### 3.4 Coherent Receiver

The optimal coherent receiver computes:

$$
z = \int_0^{T_b} r(t)\cos(2\pi f_c t)\,dt
$$

and compares to threshold $\gamma = \frac{A_1 T_b}{4}$.

**Decision rule:**  $\hat{b} = 1$ if $z \ge \gamma$, else $\hat{b} = 0$.

### 3.5 Noncoherent Receiver (Envelope Detector)

Without carrier phase knowledge:

1. Bandpass filter centred at $f_c$
2. Rectify: $e(t) = |r(t) + j\hat{r}(t)|$ where $\hat{r}$ is the Hilbert transform
3. Integrate $e(t)$ over $T_b$
4. Compare to threshold

### 3.6 Bit Error Rate

| Receiver | BER |
|----------|-----|
| Coherent | $P_e = Q\!\left(\sqrt{\dfrac{E_b}{N_0}}\right)$ |
| Noncoherent | $P_e \approx \dfrac{1}{2}e^{-E_b/(4N_0)}$ |

---

## 4. BFSK — Binary Frequency Shift Keying

### 4.1 Modulated Signal

$$
s_k(t) = \cos(2\pi f_k t + \phi_k), \quad f_k \in \{f_1, f_2\}
$$

| Bit | Frequency |
|-----|-----------|
| 1 (mark) | $f_1$ |
| 0 (space) | $f_2$ |

**Continuous-phase BFSK:** The phase $\phi_k$ is inherited from the previous bit boundary, so there are no phase discontinuities:

$$
\phi_k = 2\pi f_{k-1} n_{k} \Delta t \pmod{2\pi}
$$

This is important for spectral compactness.

### 4.2 Signal Space

BFSK signals lie on two separate 1-D axes if they are orthogonal:

```
  φ₂-axis (f2, bit-0)
      ●  (0, √Eb)

  φ₁-axis (f1, bit-1)
      ●  (√Eb, 0)
```

### 4.3 Coherent Receiver — Dual Correlator

Two correlators run in parallel:

$$
z_1 = \int_0^{T_b} r(t)\cos(2\pi f_1 t)\,dt \quad \text{(mark branch)}
$$

$$
z_2 = \int_0^{T_b} r(t)\cos(2\pi f_2 t)\,dt \quad \text{(space branch)}
$$

**Decision rule:** $\hat{b} = 1$ if $z_1 > z_2$, else $\hat{b} = 0$.

### 4.4 Noncoherent Receiver — Energy Detector

The noncoherent version uses squared (envelope-detected) outputs:

$$
E_1 = z_1^2, \quad E_2 = z_2^2
$$

**Decision rule:** $\hat{b} = 1$ if $E_1 > E_2$.

This is equivalent to comparing bandpass filter energies centred at $f_1$ and $f_2$.

### 4.5 Bit Error Rate

| Receiver | BER |
|----------|-----|
| Coherent | $P_e = Q\!\left(\sqrt{\dfrac{E_b}{N_0}}\right)$ |
| Noncoherent | $P_e = \dfrac{1}{2}e^{-E_b/(2N_0)}$ |

> **Key insight:** Noncoherent BFSK ($\frac{1}{2}e^{-E_b/(2N_0)}$) is **better** than noncoherent OOK ($\frac{1}{2}e^{-E_b/(4N_0)}$) by 3 dB. This is because BFSK carries energy in both tones.

---

## 5. Orthogonality Condition

### 5.1 Inner Product

Two signals $\phi_1(t) = \cos(2\pi f_1 t)$ and $\phi_2(t) = \cos(2\pi f_2 t)$ are **orthogonal** over $[0, T_b]$ when:

$$
\langle \phi_1, \phi_2 \rangle
= \int_0^{T_b} \cos(2\pi f_1 t)\cos(2\pi f_2 t)\,dt = 0
$$

### 5.2 Analytical Evaluation

Using the product-to-sum identity:

$$
\cos A \cos B = \frac{1}{2}[\cos(A-B) + \cos(A+B)]
$$

$$
\langle \phi_1, \phi_2 \rangle
= \frac{1}{2}\int_0^{T_b}\cos(2\pi\Delta f\, t)\,dt
+ \frac{1}{2}\int_0^{T_b}\cos(2\pi(f_1+f_2)t)\,dt
$$

For large $f_1+f_2$ (high carrier), the second term $\approx 0$. The first term:

$$
= \frac{T_b}{2}\,\text{sinc}(\Delta f \cdot T_b)\,\cos(\pi \Delta f \cdot T_b)
= \frac{T_b}{2}\,\text{sinc}(\Delta f \cdot T_b)\,\cos(\pi \Delta f \cdot T_b)
$$

More precisely:

$$
\frac{1}{2}\int_0^{T_b}\cos(2\pi\Delta f\, t)\,dt
= \frac{\sin(2\pi\Delta f\, T_b)}{4\pi\Delta f}
= \frac{T_b}{2}\,\text{sinc}(2\Delta f T_b)
$$

This is **zero** when:

$$
\boxed{\Delta f \cdot T_b = \frac{k}{2}, \quad k = 1, 2, 3, \ldots}
$$

### 5.3 Minimum Tone Spacing

The minimum spacing for orthogonality is:

$$
\Delta f_{\min} = \frac{1}{2T_b} = \frac{R_b}{2}
$$

This is achieved by **Minimum Shift Keying (MSK)**, which is the spectrally most efficient form of BFSK.

### 5.4 Why Orthogonality Matters

- **Optimal detection:** The dual correlator produces zero inter-tone interference only when signals are orthogonal.
- **BER optimality:** The theoretical BER formula $Q(\sqrt{E_b/N_0})$ assumes orthogonal signalling.
- **Non-orthogonal BFSK** introduces a bias term in the decision statistics, raising the error floor.

---

## 6. AWGN Channel Model

The received signal:

$$
r(t) = s(t) + n(t)
$$

where $n(t)$ is **Additive White Gaussian Noise** (AWGN):

- Zero mean: $\mathbb{E}[n(t)] = 0$
- Power spectral density: $S_n(f) = N_0/2$ (two-sided, W/Hz)
- Variance per sample: $\sigma^2 = N_0/2 \cdot f_s$

The **signal-to-noise ratio** is expressed as:

$$
\frac{E_b}{N_0} = \frac{\text{Energy per bit}}{\text{Noise spectral density}}
$$

---

## 7. Power Spectral Density

### ASK (OOK) PSD

OOK has a PSD with discrete lines at $\pm f_c$ plus a continuous component (sinc-shaped main lobe):

$$
S_{OOK}(f) = \frac{A_1^2 T_b^2 R_b^2}{16}\left[\text{sinc}^2\!\left(\frac{f-f_c}{R_b}\right) + \text{sinc}^2\!\left(\frac{f+f_c}{R_b}\right)\right]
+ \frac{A_1^2}{16}\left[\delta(f-f_c) + \delta(f+f_c)\right]
$$

The discrete lines appear because half the time (bit-0 = 0 V), there is a DC bias.

### BFSK PSD

For random data, the BFSK PSD has two sinc-shaped lobes centred at $f_1$ and $f_2$. With continuous-phase BFSK the sidelobes are suppressed compared to discontinuous-phase BFSK.

---

## 8. Decision Statistics and Histograms

When bit-1 is transmitted through AWGN, the coherent ASK correlator output is:

$$
z | b=1 \sim \mathcal{N}\!\left(\frac{A_1 T_b}{2},\, \frac{N_0}{4}\right)
$$

$$
z | b=0 \sim \mathcal{N}\!\left(0,\, \frac{N_0}{4}\right)
$$

The **overlap** of these Gaussians determines the error probability. As $E_b/N_0$ increases, the means move further apart (signal gets stronger) while the variance (set by noise) decreases — the histograms separate, and BER drops.

---

## 9. References

1. Haykin, S. (2001). *Communication Systems* (4th ed.). Wiley.
2. Proakis, J. G. & Salehi, M. (2007). *Digital Communications* (5th ed.). McGraw-Hill.
3. Sklar, B. (2001). *Digital Communications: Fundamentals and Applications* (2nd ed.). Prentice Hall.
4. Couch, L. W. (2013). *Digital and Analog Communication Systems* (8th ed.). Pearson.

---

*This document accompanies `ask_fsk_simulator.py` — Experiment 9, Digital Communication Laboratory.*
