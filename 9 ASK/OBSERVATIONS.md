# Observations & Interpretations — Experiment 9

> **Instructions:** Before running each parameter variation, write your **expected** physical effect. After simulation, write what you **observed**. Then state whether they agree, and if not, explain the discrepancy.

---

## Experiment 9A — Passband Waveform Inspection (Fig 1)

### Expected
_Before running:_

> ASK: The carrier should be present only during bit-1 and absent (zero amplitude) during bit-0.  
> BFSK: The waveform should switch between two clearly different frequencies at each bit boundary. Continuous-phase BFSK should show no phase jump at transitions.

### Observed
_After running:_

> [Fill in your observations here — does the ASK waveform match expected? Count cycles per bit to confirm f1 and f2 for BFSK.]

### Agreement
- [ ] Agrees with theory
- [ ] Partially agrees — discrepancy: ___________
- [ ] Does not agree — reason: ___________

---

## Experiment 9B — Power Spectra (Fig 2)

### Expected

> **ASK PSD:** Should show a main lobe centred at fc = 8000 Hz with bandwidth ≈ 2Rb = 2000 Hz, plus a discrete spectral line at fc (due to OOK DC bias).  
> **BFSK PSD:** Should show two lobes, one centred at f1 = 7000 Hz and one at f2 = 9000 Hz. The separation should equal Δf = 2000 Hz.

### Observed
> [How wide is the ASK main lobe? Is the spectral line visible? Do the two BFSK lobes overlap?]

### Agreement
- [ ] Agrees with theory
- [ ] Partially agrees — discrepancy: ___________
- [ ] Does not agree — reason: ___________

---

## Experiment 9C — Correlator Outputs (Fig 3)

### Expected

> **ASK:** Bit-1 outputs should cluster around a positive value (~A1·Tb/2 ≈ 0.5·10⁻³). Bit-0 outputs should cluster near 0. Noise spreads each cluster.  
> **BFSK:** For bit-1, z1 >> z2. For bit-0, z2 >> z1. The two traces should cross only due to noise.

### Observed
> [Do you see two distinct levels in ASK? How much overlap is there? For BFSK, are the two branch outputs well separated?]

### Agreement
- [ ] Agrees with theory
- [ ] Partially agrees — discrepancy: ___________
- [ ] Does not agree — reason: ___________

---

## Experiment 9D — Decision-Statistic Histograms (Fig 4)

### Expected

> Each histogram should show two peaks — one for bit-0, one for bit-1. The decision threshold sits between them. At high Eb/N0, peaks are narrow and well-separated → low BER. At low Eb/N0, peaks are wide and overlap → high BER.

### Observed (at Eb/N0 = 8 dB)
> [Are the two peaks clearly separated? Is there overlap? Where does the threshold fall?]

### Test
> Calculate the theoretical overlap area = Q(√(SNR_per_bit)) and compare to observed error rate.

### Agreement
- [ ] Agrees with theory
- [ ] Partially agrees — discrepancy: ___________
- [ ] Does not agree — reason: ___________

---

## Experiment 9E — BER Curves (Fig 5)

### Expected

| Scheme | At Eb/N0 = 8 dB | At Eb/N0 = 12 dB |
|--------|-----------------|------------------|
| ASK Coherent | ≈ 1.5 × 10⁻³ | ≈ 2 × 10⁻⁵ |
| ASK Noncoherent | worse by ~1-2 dB | worse by ~1-2 dB |
| BFSK Coherent | same as ASK Coh | same as ASK Coh |
| BFSK Noncoherent | ≈ 3 dB better than ASK Noncoh | ≈ 3 dB better |

### Observed
> [Read off approximate BER values from Fig 5. Do they match the table above?]

### Discrepancy Analysis
> If simulated BER diverges from theory, likely causes:
> 1. **Finite sample size** (Nbits too low) — increase to 10 000
> 2. **Threshold not optimal** — check the threshold formula in the code
> 3. **SNR definition mismatch** — verify Eb computation

### Agreement
- [ ] Agrees with theory within Monte-Carlo variance
- [ ] Partially agrees — discrepancy: ___________
- [ ] Does not agree — reason: ___________

---

## Experiment 9F — FSK Orthogonality Validation (Fig 6) [MANDATORY]

### Mandatory Inner Product Calculation

For the default parameters: $f_1 = 7000$ Hz, $f_2 = 9000$ Hz, $T_b = 1$ ms, $\Delta f \cdot T_b = 2$.

$$
\langle\phi_1, \phi_2\rangle = \int_0^{T_b} \cos(2\pi \cdot 7000 \cdot t)\cos(2\pi \cdot 9000 \cdot t)\,dt
$$

**Analytical result** (using product-to-sum):

$$
= \frac{1}{2}\int_0^{10^{-3}} \cos(2\pi \cdot 2000 \cdot t)\,dt
+ \frac{1}{2}\int_0^{10^{-3}} \cos(2\pi \cdot 16000 \cdot t)\,dt
$$

$$
= \frac{1}{2} \cdot \frac{\sin(2\pi \cdot 2000 \cdot 10^{-3})}{2\pi \cdot 2000}
+ \frac{1}{2} \cdot \frac{\sin(2\pi \cdot 16000 \cdot 10^{-3})}{2\pi \cdot 16000}
$$

$$
= \frac{\sin(4\pi)}{4\pi \cdot 2000} + \frac{\sin(32\pi)}{4\pi \cdot 16000}
= \frac{0}{...} + \frac{0}{...} = 0
$$

✅ **Orthogonal** because $\Delta f \cdot T_b = 2 = k/2$ with $k = 4$.

### Self Inner Products (Signal Energies)

$$
\langle\phi_1, \phi_1\rangle = \int_0^{T_b} \cos^2(2\pi f_1 t)\,dt
= \frac{T_b}{2} = 5 \times 10^{-4} \text{ s}
$$

$$
\langle\phi_2, \phi_2\rangle = \frac{T_b}{2} = 5 \times 10^{-4} \text{ s}
$$

### Observed (from Fig 6 console output)
> [Copy the printed table here after running the simulator]

### Agreement
- [ ] Computed inner products match analytical calculation
- [ ] Fig 6 shows zeros at Δf·Tb = k/2

---

## Experiment 9G — Tone Spacing Effect on BER (Fig 7)

### Expected

> At **orthogonal** spacings (Δf·Tb = 0.5, 1.0, 1.5, 2.0), the BER should be at its **minimum** for that Eb/N0.  
> At **non-orthogonal** spacings (Δf·Tb = 0.25, 0.75), the dual correlator has cross-interference between branches → BER increases.

### Observed
> [Do the bars at 0.5 and 1.0 show lower BER than 0.25 and 0.75?]

### Agreement
- [ ] Agrees with theory
- [ ] Partially agrees — discrepancy: ___________
- [ ] Does not agree — reason: ___________

---

## Summary Table

| Experiment | Physical Effect | Agrees with Theory? |
|------------|-----------------|---------------------|
| 9A Waveforms | Amplitude / frequency switching | |
| 9B Spectra | Spectral width and tone locations | |
| 9C Correlator outputs | Separation of bit classes | |
| 9D Histograms | Distribution overlap → BER | |
| 9E BER curves | Coherent > Noncoherent, BFSK vs ASK | |
| 9F Orthogonality | IP = 0 at Δf·Tb = k/2 | |
| 9G Tone spacing | BER minimum at orthogonal Δf | |

---

## Design Choices and Diagnostic Notes

### Threshold Selection
The coherent ASK threshold is set to the midpoint of the expected correlator outputs for bit-1 and bit-0. This is the **ML (Maximum Likelihood) threshold** for equal-prior, equal-noise conditions.

### Non-orthogonal BFSK Diagnostic
If BFSK BER is unexpectedly high:
1. Check `Δf·Tb` from console output — should be k/2.
2. Run Fig 6 and verify inner product is ≈ 0 at the chosen spacing.
3. If non-zero, reduce Δf to the next orthogonal value.

### Finite-Length BER Variance
The standard deviation of the simulated BER estimate is approximately:

$$
\sigma_{BER} \approx \sqrt{\frac{P_e(1-P_e)}{N_{\text{bits}}}}
$$

For $N_{\text{bits}} = 256$ and $P_e = 10^{-3}$: $\sigma_{BER} \approx 2 \times 10^{-3}$ — meaning at low BER, you may see zero errors in 256 bits even at moderate SNR. Increase to 10 000 bits for accuracy below $10^{-3}$.
