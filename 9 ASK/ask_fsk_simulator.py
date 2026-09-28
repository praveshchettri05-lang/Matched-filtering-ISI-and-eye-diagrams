# -*- coding: utf-8 -*-
"""
================================================================================
  Experiment 9 - ASK and BFSK Simulator
  Digital Communication Laboratory
================================================================================

OBJECTIVES
----------
  1. Generate and detect binary ASK and BFSK passband waveforms.
  2. Compare coherent (correlator-based) and noncoherent (envelope/energy)
     detection strategies.
  3. Vary FSK tone-spacing and observe the orthogonality condition.
  4. Estimate Bit-Error-Rate (BER) vs Eb/N0 curves and compare with theory.

MANDATORY VALIDATION
--------------------
  Inner products of the BFSK basis signals are computed over one bit interval
  to confirm orthogonality when Df * Tb = k/2 (k = 1, 2, …).

AUTHOR : <Your Name>
DATE   : September 2026
Python : 3.9+

DEPENDENCIES
------------
  numpy, scipy, matplotlib
  Install via:  pip install numpy scipy matplotlib
================================================================================
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import hilbert, welch
from itertools import product
import warnings

warnings.filterwarnings("ignore")
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# -----------------------------------------------------------------------------
# GLOBAL STYLE
# -----------------------------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#e6edf3",
    "axes.titlecolor":  "#e6edf3",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "grid.color":       "#21262d",
    "text.color":       "#e6edf3",
    "legend.facecolor": "#161b22",
    "legend.edgecolor": "#30363d",
    "figure.titlesize": 15,
    "axes.titlesize":   11,
    "axes.labelsize":   9,
    "font.family":      "monospace",
})

COLORS = {
    "bit1":    "#58a6ff",
    "bit0":    "#f78166",
    "ask":     "#3fb950",
    "fsk_f1":  "#d2a8ff",
    "fsk_f2":  "#ffa657",
    "noise":   "#8b949e",
    "theory":  "#f0883e",
    "sim":     "#58a6ff",
    "hist1":   "#58a6ff",
    "hist0":   "#f78166",
    "thresh":  "#ffa657",
}

# -----------------------------------------------------------------------------
# 1. SIGNAL PARAMETERS  (edit here to explore)
# -----------------------------------------------------------------------------
class SimParams:
    """Central configuration object -- change any field to re-run."""

    # Bit timing
    Rb      = 1_000          # Bit rate  [bps]
    Tb      = 1 / Rb         # Bit period [s]
    sps     = 200            # Samples per bit (oversampling factor)

    # Carrier / tone frequencies
    fc      = 8_000          # ASK carrier frequency [Hz]
    f1      = 7_000          # BFSK mark  frequency  [Hz]  (bit=1)
    f2      = 9_000          # BFSK space frequency  [Hz]  (bit=0)

    # Modulation index
    ask_A1  = 1.0            # ASK amplitude for bit-1
    ask_A0  = 0.0            # ASK amplitude for bit-0  (OOK)

    # Simulation
    Nbits   = 256            # Number of bits in Monte-Carlo BER run
    SNR_dB_range = np.arange(-4, 15, 1)   # Eb/N0 sweep [dB]

    # Derived
    fs      = Rb * sps       # Sampling frequency [Hz]
    dt      = 1 / fs         # Sampling interval  [s]
    N       = sps            # Samples per bit

p = SimParams()

# -----------------------------------------------------------------------------
# 2. BIT STREAM UTILITIES
# -----------------------------------------------------------------------------

def generate_bits(n: int, seed: int = 42) -> np.ndarray:
    """Return n random binary bits {0,1}."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, n)


def bits_to_nrz(bits: np.ndarray, sps: int) -> np.ndarray:
    """Upsample bits to NRZ waveform (hold each bit for sps samples)."""
    return np.repeat(bits, sps).astype(float)

# -----------------------------------------------------------------------------
# 3. MODULATION FUNCTIONS
# -----------------------------------------------------------------------------

def modulate_ask(bits: np.ndarray, p: SimParams) -> tuple:
    """
    Binary ASK (OOK) modulator.

    s(t) = A_k * cos(2π fc t)
    where A_k ∈ {A1, A0} depending on bit k.

    Returns
    -------
    t   : time axis [s]
    ask : modulated waveform
    """
    N_total = len(bits) * p.N
    t = np.arange(N_total) * p.dt
    carrier = np.cos(2 * np.pi * p.fc * t)

    amp_seq = np.where(np.repeat(bits, p.N) == 1, p.ask_A1, p.ask_A0)
    ask = amp_seq * carrier
    return t, ask


def modulate_bfsk(bits: np.ndarray, p: SimParams) -> tuple:
    """
    Coherent Binary FSK modulator.

    s(t) = cos(2π f_k t)   f_k ∈ {f1, f2}

    Continuous-phase: the phase is accumulated across bit boundaries to
    ensure phase continuity (important for spectral efficiency).

    Returns
    -------
    t    : time axis [s]
    bfsk : modulated waveform
    phase_track : instantaneous phase at each sample
    """
    N_total = len(bits) * p.N
    t = np.arange(N_total) * p.dt

    # Build instantaneous frequency sequence
    freq_seq = np.where(np.repeat(bits, p.N) == 1, p.f1, p.f2)

    # Continuous phase via cumulative integration
    phase = 2 * np.pi * np.cumsum(freq_seq) * p.dt
    bfsk  = np.cos(phase)
    return t, bfsk, phase


# -----------------------------------------------------------------------------
# 4. AWGN CHANNEL
# -----------------------------------------------------------------------------

def add_awgn(signal: np.ndarray, EbN0_dB: float, p: SimParams,
             seed: int = 0) -> np.ndarray:
    """
    Add AWGN with specified Eb/N0.

    For OOK/ASK  : Eb  = A1² * Tb / 2  (average energy per bit)
    For BFSK     : Eb  = Tb / 2         (unit amplitude assumed)
    """
    rng = np.random.default_rng(seed)
    sig_power = np.mean(signal ** 2)

    # Eb from signal power  (Eb = Pavg * Tb, but we keep ratio)
    EbN0_lin = 10 ** (EbN0_dB / 10)
    # Noise variance: sigma² = Eb / (2 * EbN0)  [one-sided spectral density trick]
    #   N0/2 = Eb/(2*EbN0_lin), noise_var = N0/2 * fs/2 -- but for matched
    #   filter we use the simpler: sigma_noise s.t. SNR_bit = EbN0
    Eb = sig_power * p.Tb / p.sps   # approximate per sample -> per bit
    # noise std per sample
    sigma = np.sqrt(Eb / (2 * EbN0_lin * p.dt))
    noise = rng.normal(0, sigma, signal.shape)
    return signal + noise


# -----------------------------------------------------------------------------
# 5. COHERENT CORRELATOR RECEIVER
# -----------------------------------------------------------------------------

def correlator_ask(rx: np.ndarray, bits_tx: np.ndarray,
                   p: SimParams) -> tuple:
    """
    Coherent ASK (OOK) correlator receiver.

    Decision statistic for bit k:
        z_k = ∫₀^Tb  r(t) * cos(2π fc t) dt   ≈ Σ r[n] * cos(2π fc n/fs)

    Threshold = midpoint between expected z for bit-1 and bit-0.

    Returns
    -------
    bits_rx    : detected bits
    stats      : array of decision statistics (one per bit)
    threshold  : decision threshold used
    """
    N = p.N
    t_bit = np.arange(N) * p.dt
    ref   = np.cos(2 * np.pi * p.fc * t_bit)   # correlator reference

    stats = np.zeros(len(bits_tx))
    for k in range(len(bits_tx)):
        seg      = rx[k*N : (k+1)*N]
        stats[k] = np.dot(seg, ref) * p.dt      # numerical integration

    # Threshold: midpoint between expected correlator outputs
    z1 = p.ask_A1 * N * p.dt / 2   # expected for bit-1 (peak of cos² integral)
    z0 = p.ask_A0 * N * p.dt / 2   # expected for bit-0
    threshold = (z1 + z0) / 2

    bits_rx = (stats >= threshold).astype(int)
    return bits_rx, stats, threshold


def correlator_bfsk(rx: np.ndarray, bits_tx: np.ndarray,
                    p: SimParams) -> tuple:
    """
    Coherent BFSK correlator receiver (dual correlator / matched filter).

    Two branches:
        z1_k = ∫ r(t) * cos(2π f1 t) dt   -> "mark" branch
        z2_k = ∫ r(t) * cos(2π f2 t) dt   -> "space" branch

    Decision: bit-1 if z1_k > z2_k, else bit-0.

    Returns
    -------
    bits_rx : detected bits
    z1      : mark  correlator outputs
    z2      : space correlator outputs
    """
    N = p.N
    t_bit = np.arange(N) * p.dt
    ref1  = np.cos(2 * np.pi * p.f1 * t_bit)
    ref2  = np.cos(2 * np.pi * p.f2 * t_bit)

    z1 = np.zeros(len(bits_tx))
    z2 = np.zeros(len(bits_tx))

    for k in range(len(bits_tx)):
        seg   = rx[k*N : (k+1)*N]
        z1[k] = np.dot(seg, ref1) * p.dt
        z2[k] = np.dot(seg, ref2) * p.dt

    bits_rx = (z1 >= z2).astype(int)
    return bits_rx, z1, z2

# -----------------------------------------------------------------------------
# 6. NONCOHERENT RECEIVER  (envelope / energy detection)
# -----------------------------------------------------------------------------

def envelope_detector_ask(rx: np.ndarray, bits_tx: np.ndarray,
                           p: SimParams) -> tuple:
    """
    Noncoherent ASK receiver using envelope detection.

    envelope(t) = |analytic_signal(r(t))|
    Decision: threshold on envelope integrated over Tb.
    """
    analytic  = hilbert(rx)
    env       = np.abs(analytic)

    stats     = np.zeros(len(bits_tx))
    for k in range(len(bits_tx)):
        stats[k] = np.mean(env[k*p.N : (k+1)*p.N])

    # Threshold midpoint (no carrier phase knowledge needed)
    threshold = (np.min(stats) + np.max(stats)) / 2
    bits_rx   = (stats >= threshold).astype(int)
    return bits_rx, stats, threshold


def energy_detector_bfsk(rx: np.ndarray, bits_tx: np.ndarray,
                          p: SimParams) -> tuple:
    """
    Noncoherent BFSK receiver using bandpass energy detection.

    Two bandpass filters centred at f1 and f2, then energy comparison.
    Approximated here by squaring the two branch correlator outputs:
        E1_k = z1_k²,   E2_k = z2_k²
    (equivalent to envelope-squared detection for narrowband signals)
    """
    _, z1, z2 = correlator_bfsk(rx, bits_tx, p)
    E1 = z1 ** 2
    E2 = z2 ** 2
    bits_rx = (E1 >= E2).astype(int)
    return bits_rx, E1, E2

# -----------------------------------------------------------------------------
# 7. ORTHOGONALITY VALIDATION  (Mandatory)
# -----------------------------------------------------------------------------

def validate_fsk_orthogonality(p: SimParams,
                                delta_f_values: np.ndarray = None) -> dict:
    """
    Compute inner products  <phi1, phi2> = ∫₀^Tb cos(2π f1 t)*cos(2π f2 t) dt
    for a range of tone-spacings Df = f2 - f1.

    Orthogonality requires  <phi1, phi2> = 0  ↔  Df * Tb = k/2  (k=1,2,…)

    Also computes:
        <phi1, phi1>  and  <phi2, phi2>  (self inner-products / energies)

    Returns a dict with keys: delta_f, inner_prod, phi1_energy, phi2_energy
    """
    t = np.arange(p.N) * p.dt   # one bit interval

    if delta_f_values is None:
        delta_f_values = np.linspace(0, 4 * p.Rb, 500)

    inner  = np.zeros(len(delta_f_values))
    e_phi1 = np.zeros(len(delta_f_values))
    e_phi2 = np.zeros(len(delta_f_values))

    fc_mid = (p.f1 + p.f2) / 2   # use symmetric tones around mid

    for i, df in enumerate(delta_f_values):
        f1_i  = fc_mid - df / 2
        f2_i  = fc_mid + df / 2
        phi1  = np.cos(2 * np.pi * f1_i * t)
        phi2  = np.cos(2 * np.pi * f2_i * t)
        inner[i]  = np.trapezoid(phi1 * phi2, t)
        e_phi1[i] = np.trapezoid(phi1 ** 2,   t)
        e_phi2[i] = np.trapezoid(phi2 ** 2,   t)

    return {
        "delta_f":    delta_f_values,
        "inner_prod": inner,
        "phi1_energy": e_phi1,
        "phi2_energy": e_phi2,
        "Tb":         p.Tb,
    }

# -----------------------------------------------------------------------------
# 8. BER SIMULATION  (Monte-Carlo)
# -----------------------------------------------------------------------------

def ber_simulation(p: SimParams, modulation: str = "ask",
                   detection: str = "coherent",
                   Nbits: int = None, seed_base: int = 1) -> np.ndarray:
    """
    Monte-Carlo BER estimation over the SNR range in p.SNR_dB_range.

    Parameters
    ----------
    modulation : 'ask' | 'bfsk'
    detection  : 'coherent' | 'noncoherent'
    Nbits      : number of bits per SNR point (defaults to p.Nbits)

    Returns
    -------
    ber_sim : array of simulated BER values
    """
    if Nbits is None:
        Nbits = p.Nbits

    ber_sim = np.zeros(len(p.SNR_dB_range))

    for idx, snr_db in enumerate(p.SNR_dB_range):
        errors = 0
        bits_tx = generate_bits(Nbits, seed=seed_base + idx)

        if modulation == "ask":
            _, tx = modulate_ask(bits_tx, p)
        else:
            _, tx, _ = modulate_bfsk(bits_tx, p)

        rx = add_awgn(tx, snr_db, p, seed=seed_base + idx + 1000)

        if modulation == "ask" and detection == "coherent":
            bits_rx, _, _ = correlator_ask(rx, bits_tx, p)
        elif modulation == "ask" and detection == "noncoherent":
            bits_rx, _, _ = envelope_detector_ask(rx, bits_tx, p)
        elif modulation == "bfsk" and detection == "coherent":
            bits_rx, _, _ = correlator_bfsk(rx, bits_tx, p)
        elif modulation == "bfsk" and detection == "noncoherent":
            bits_rx, _, _ = energy_detector_bfsk(rx, bits_tx, p)
        else:
            raise ValueError(f"Unknown combination: {modulation}/{detection}")

        errors      = np.sum(bits_tx != bits_rx)
        ber_sim[idx] = errors / Nbits

    return ber_sim

# -----------------------------------------------------------------------------
# 9. THEORETICAL BER EXPRESSIONS
# -----------------------------------------------------------------------------

def ber_theory(snr_db_arr: np.ndarray, scheme: str) -> np.ndarray:
    """
    Closed-form BER expressions.

    scheme options
    --------------
    'ask_coherent'      : OOK coherent  -> Q(√(Eb/N0))
    'ask_noncoherent'   : OOK noncoherent -> 0.5*exp(-Eb/(4N0))  (approx)
    'bfsk_coherent'     : Q(√(Eb/N0))
    'bfsk_noncoherent'  : 0.5*exp(-Eb/(2N0))
    """
    from scipy.special import erfc

    snr_lin = 10 ** (snr_db_arr / 10)

    def Q(x):
        return 0.5 * erfc(x / np.sqrt(2))

    mapping = {
        "ask_coherent":     lambda r: Q(np.sqrt(r)),
        "ask_noncoherent":  lambda r: 0.5 * np.exp(-r / 4),
        "bfsk_coherent":    lambda r: Q(np.sqrt(r)),
        "bfsk_noncoherent": lambda r: 0.5 * np.exp(-r / 2),
    }

    if scheme not in mapping:
        raise ValueError(f"Unknown scheme '{scheme}'")

    return mapping[scheme](snr_lin)

# -----------------------------------------------------------------------------
# 10. POWER SPECTRAL DENSITY
# -----------------------------------------------------------------------------

def compute_psd(signal: np.ndarray, fs: float, label: str = "Signal") -> dict:
    """Return PSD using Welch's method."""
    f, Pxx = welch(signal, fs=fs, nperseg=512, noverlap=256,
                   window="hann", scaling="density")
    return {"f": f, "Pxx": Pxx, "label": label}

# -----------------------------------------------------------------------------
# 11. VISUALIZATION FUNCTIONS
# -----------------------------------------------------------------------------

def plot_passband_waveforms(bits: np.ndarray, p: SimParams) -> plt.Figure:
    """
    Figure 1 -- Passband Waveforms
    Rows: bit stream | ASK | BFSK  (first 8 bits shown)
    """
    view_bits = min(8, len(bits))
    vb        = bits[:view_bits]
    t_ask, ask     = modulate_ask(vb, p)
    t_bfsk, bfsk, _ = modulate_bfsk(vb, p)
    nrz           = bits_to_nrz(vb, p.N)
    t_nrz         = np.arange(len(nrz)) * p.dt

    fig, axes = plt.subplots(3, 1, figsize=(14, 7), sharex=True)
    fig.suptitle("Figure 1 -- Passband Waveforms (First 8 Bits)", y=1.01)

    # Bit stream
    axes[0].step(t_nrz * 1e3, nrz, color=COLORS["bit1"], linewidth=1.5, where="post")
    axes[0].set_ylabel("Bit Value")
    axes[0].set_ylim(-0.3, 1.3)
    axes[0].set_title("Baseband Bit Stream")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    for k in range(view_bits):
        axes[0].text((k + 0.5) * p.Tb * 1e3, 1.1, str(vb[k]),
                     ha="center", va="center", fontsize=9, color=COLORS["bit1"])

    # ASK
    axes[1].plot(t_ask * 1e3, ask, color=COLORS["ask"], linewidth=0.8)
    axes[1].set_ylabel("Amplitude")
    axes[1].set_title(f"ASK -- OOK  (fc={p.fc} Hz, A1={p.ask_A1}, A0={p.ask_A0})")
    axes[1].grid(True, linestyle="--", alpha=0.4)

    # BFSK
    axes[2].plot(t_bfsk * 1e3, bfsk, color=COLORS["fsk_f1"], linewidth=0.8)
    axes[2].set_ylabel("Amplitude")
    axes[2].set_xlabel("Time [ms]")
    axes[2].set_title(
        f"BFSK -- Continuous Phase  (f1={p.f1} Hz -> bit-1, f2={p.f2} Hz -> bit-0)")
    axes[2].grid(True, linestyle="--", alpha=0.4)

    # Shade bit regions
    for ax in axes[1:]:
        for k in range(view_bits):
            color = COLORS["bit1"] if vb[k] == 1 else COLORS["bit0"]
            ax.axvspan(k * p.Tb * 1e3, (k + 1) * p.Tb * 1e3,
                       alpha=0.05, color=color)

    plt.tight_layout()
    return fig


def plot_power_spectra(bits: np.ndarray, p: SimParams) -> plt.Figure:
    """
    Figure 2 -- Power Spectral Density comparison: ASK vs BFSK.
    """
    _, ask       = modulate_ask(bits, p)
    _, bfsk, _   = modulate_bfsk(bits, p)

    psd_ask  = compute_psd(ask,  p.fs, "ASK")
    psd_bfsk = compute_psd(bfsk, p.fs, "BFSK")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Figure 2 -- Power Spectral Density")

    for ax, psd, color, title in zip(
        axes,
        [psd_ask, psd_bfsk],
        [COLORS["ask"], COLORS["fsk_f1"]],
        ["ASK (OOK) Power Spectrum", "BFSK Power Spectrum"]
    ):
        ax.semilogy(psd["f"], psd["Pxx"], color=color, linewidth=1.0)
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("PSD [V²/Hz]")
        ax.set_title(title)
        ax.set_xlim(0, p.fs / 2)
        ax.grid(True, linestyle="--", alpha=0.4)

    # Mark tone frequencies
    for f_mark, label in [(p.fc, f"fc={p.fc}"),
                           (p.f1,  f"f1={p.f1}"),
                           (p.f2,  f"f2={p.f2}")]:
        for ax_i, ax in enumerate(axes):
            if ax_i == 0 and f_mark != p.fc:
                continue
            if ax_i == 1 and f_mark == p.fc:
                continue
            ax.axvline(f_mark, color=COLORS["thresh"], linestyle="--",
                       linewidth=0.8, alpha=0.7, label=label)
    for ax in axes:
        ax.legend(fontsize=8)

    plt.tight_layout()
    return fig


def plot_correlator_outputs(bits: np.ndarray, p: SimParams,
                             EbN0_dB: float = 10) -> plt.Figure:
    """
    Figure 3 -- Correlator Output Statistics.
    Shows z1 and z2 per bit for BFSK coherent receiver.
    """
    _, ask       = modulate_ask(bits, p)
    _, bfsk, _   = modulate_bfsk(bits, p)

    rx_ask  = add_awgn(ask,  EbN0_dB, p, seed=7)
    rx_bfsk = add_awgn(bfsk, EbN0_dB, p, seed=8)

    _, ask_stats, ask_thresh = correlator_ask(rx_ask, bits, p)
    _, z1, z2                = correlator_bfsk(rx_bfsk, bits, p)

    bit_idx = np.arange(len(bits))

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    fig.suptitle(f"Figure 3 -- Correlator Outputs  (Eb/N0 = {EbN0_dB} dB)")

    # ASK correlator output
    ax = axes[0]
    ax.stem(bit_idx[bits == 1], ask_stats[bits == 1],
            linefmt=COLORS["bit1"], markerfmt=f"o", basefmt="gray",
            label="Bit-1 output")
    ax.stem(bit_idx[bits == 0], ask_stats[bits == 0],
            linefmt=COLORS["bit0"], markerfmt=f"s", basefmt="gray",
            label="Bit-0 output")
    ax.axhline(ask_thresh, color=COLORS["thresh"], linestyle="--",
               linewidth=1.5, label=f"Threshold = {ask_thresh:.4f}")
    ax.set_xlabel("Bit Index")
    ax.set_ylabel("Correlator Output z")
    ax.set_title("ASK Coherent Correlator Output")
    ax.legend(fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.4)

    # BFSK dual correlator output
    ax = axes[1]
    ax.plot(bit_idx, z1, "o-", color=COLORS["fsk_f1"], markersize=3,
            linewidth=0.7, label=f"z1 (f1={p.f1} Hz branch)")
    ax.plot(bit_idx, z2, "s-", color=COLORS["fsk_f2"], markersize=3,
            linewidth=0.7, label=f"z2 (f2={p.f2} Hz branch)")
    ax.set_xlabel("Bit Index")
    ax.set_ylabel("Correlator Output")
    ax.set_title("BFSK Coherent Dual-Correlator Output  (bit-1 -> z1>z2)")
    ax.legend(fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    return fig


def plot_decision_histograms(bits: np.ndarray, p: SimParams,
                              EbN0_dB: float = 8) -> plt.Figure:
    """
    Figure 4 -- Decision-Statistic Histograms.
    Separates distributions for bit-0 and bit-1 classes to visualize overlap.
    """
    _, ask       = modulate_ask(bits, p)
    _, bfsk, _   = modulate_bfsk(bits, p)
    rx_ask  = add_awgn(ask,  EbN0_dB, p, seed=11)
    rx_bfsk = add_awgn(bfsk, EbN0_dB, p, seed=12)

    _, ask_stats, ask_thresh = correlator_ask(rx_ask, bits, p)
    _, z1, z2                = correlator_bfsk(rx_bfsk, bits, p)
    bfsk_stat = z1 - z2      # positive -> decide bit-1

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Figure 4 -- Decision-Statistic Histograms  (Eb/N0 = {EbN0_dB} dB)")

    for ax, stats, thresh, title, mod in zip(
        axes,
        [ask_stats, bfsk_stat],
        [ask_thresh, 0.0],
        ["ASK Correlator Output", "BFSK  z1 − z2  Statistic"],
        ["ask", "bfsk"]
    ):
        bins = 40
        ax.hist(stats[bits == 1], bins=bins, density=True, alpha=0.7,
                color=COLORS["hist1"], label="Bit-1 (mark)")
        ax.hist(stats[bits == 0], bins=bins, density=True, alpha=0.7,
                color=COLORS["hist0"], label="Bit-0 (space)")
        ax.axvline(thresh, color=COLORS["thresh"], linestyle="--",
                   linewidth=2, label=f"Decision threshold = {thresh:.4f}")
        ax.set_xlabel("Decision Statistic")
        ax.set_ylabel("Probability Density")
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    return fig


def plot_ber_curves(p: SimParams) -> plt.Figure:
    """
    Figure 5 -- BER vs Eb/N0 Curves.
    Simulated (Monte-Carlo) + theoretical for all four combinations.
    """
    print("\n  [BER] Running Monte-Carlo simulations ... (may take ~20 s)")

    results = {}
    schemes = [
        ("ask",  "coherent",    "ASK Coherent"),
        ("ask",  "noncoherent", "ASK Noncoherent"),
        ("bfsk", "coherent",    "BFSK Coherent"),
        ("bfsk", "noncoherent", "BFSK Noncoherent"),
    ]

    for mod, det, label in schemes:
        key = f"{mod}_{det}"
        print(f"    -> {label} ...")
        results[key] = {
            "sim":    ber_simulation(p, mod, det, Nbits=p.Nbits),
            "theory": ber_theory(p.SNR_dB_range, key),
            "label":  label,
        }

    line_styles = ["-o", "-s", "--^", "--v"]
    sim_colors  = ["#58a6ff", "#3fb950", "#d2a8ff", "#ffa657"]
    th_colors   = ["#1f6feb", "#238636", "#8957e5", "#fb8f44"]

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.suptitle("Figure 5 -- BER vs Eb/N0 Curves")

    for i, (mod, det, label) in enumerate(schemes):
        key  = f"{mod}_{det}"
        snrs = p.SNR_dB_range
        # Simulated
        valid = results[key]["sim"] > 0
        ax.semilogy(snrs[valid], results[key]["sim"][valid],
                    line_styles[i], color=sim_colors[i],
                    markersize=5, linewidth=1.2,
                    label=f"{label} (Sim)")
        # Theoretical
        ax.semilogy(snrs, results[key]["theory"],
                    color=th_colors[i], linestyle=":",
                    linewidth=2, alpha=0.8,
                    label=f"{label} (Theory)")

    ax.set_xlabel("Eb/N0 [dB]")
    ax.set_ylabel("Bit Error Rate (BER)")
    ax.set_title("Simulated vs Theoretical BER")
    ax.legend(fontsize=8, loc="lower left")
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.set_ylim(1e-5, 1)
    ax.set_xlim(p.SNR_dB_range[0], p.SNR_dB_range[-1])

    plt.tight_layout()
    return fig


def plot_orthogonality(p: SimParams) -> plt.Figure:
    """
    Figure 6 -- FSK Orthogonality Validation.
    Inner product <phi1, phi2> vs tone-spacing Df.
    """
    ortho = validate_fsk_orthogonality(p)
    df    = ortho["delta_f"]
    ip    = ortho["inner_prod"]

    # Normalised inner product
    ip_norm = ip / (ortho["phi1_energy"] + 1e-20) * 2  # ≈ 2*<phi1,phi2>/<phi1,phi1>

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    fig.suptitle("Figure 6 -- BFSK Orthogonality Validation  (Mandatory)")

    # Raw inner product
    ax = axes[0]
    ax.plot(df / p.Rb, ip, color=COLORS["fsk_f1"], linewidth=1.2)
    ax.axhline(0, color="white", linewidth=0.5, linestyle="--")

    # Mark first few zero crossings (Df = k*Rb/2)
    for k in range(1, 9):
        df_zero = k * p.Rb / 2
        ax.axvline(df_zero / p.Rb, color=COLORS["thresh"],
                   linestyle=":", linewidth=1, alpha=0.8)
        ax.text(df_zero / p.Rb, ax.get_ylim()[1] * 0.8 if ax.get_ylim()[1] != 0 else 0.04,
                f"df*Tb={k/2:.1f}", rotation=90, fontsize=7, color=COLORS["thresh"],
                va="top")

    ax.set_xlabel("Normalised Tone Spacing  Df / Rb")
    ax.set_ylabel("Inner Product  <phi1, phi2>  [s]")
    ax.set_title("Inner Product of BFSK Basis Signals vs. Tone Spacing")
    ax.grid(True, linestyle="--", alpha=0.4)

    # Normalised
    ax2 = axes[1]
    ax2.plot(df / p.Rb, ip_norm, color=COLORS["ask"], linewidth=1.2)
    ax2.axhline(0, color="white", linewidth=0.5, linestyle="--")
    ax2.set_xlabel("Normalised Tone Spacing  Df / Rb")
    ax2.set_ylabel("Normalised Inner Product  2<phi1,phi2> / <phi1,phi1>")
    ax2.set_title("Normalised Orthogonality Check  (zero = orthogonal)")
    ax2.grid(True, linestyle="--", alpha=0.4)

    # Print table of zero crossings
    print("\n  +----------------------------------------------+")
    print("  |  BFSK Orthogonality Condition Verification   |")
    print("  |  <phi1, phi2> at Df = k*Rb/2                   |")
    print("  +-------+-------------+------------------------+")
    print("  |  k    | df*Tb       | <phi1,phi2>               |")
    print("  +-------+-------------+------------------------+")

    for k in range(1, 6):
        df_test = k * p.Rb / 2
        idx     = np.argmin(np.abs(ortho["delta_f"] - df_test))
        ip_val  = ortho["inner_prod"][idx]
        orth_ok = "[OK] ORTHOGONAL" if abs(ip_val) < 1e-4 else "[FAIL]"
        print(f"  |  {k:<5d}| {k/2:<12.1f}| {ip_val:+.6e}  {orth_ok}  |")

    print("  +-------+-------------+------------------------+\n")

    plt.tight_layout()
    return fig


def plot_tone_spacing_ber(p: SimParams) -> plt.Figure:
    """
    Figure 7 -- Effect of Tone Spacing on BER.
    Simulates BER at fixed Eb/N0=8dB for different Df values.
    """
    print("\n  [Tone-Spacing BER] Sweeping Df ... (may take ~15 s)")

    df_norm_arr = np.array([0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
    fixed_snr   = 8.0
    ber_vals    = []

    bits_tx = generate_bits(256, seed=99)

    for df_norm in df_norm_arr:
        df    = df_norm * p.Rb
        f_mid = (p.f1 + p.f2) / 2
        f1_t  = f_mid - df / 2
        f2_t  = f_mid + df / 2

        # Temporarily override freq
        p_tmp    = SimParams()
        p_tmp.f1 = f1_t
        p_tmp.f2 = f2_t

        _, bfsk, _ = modulate_bfsk(bits_tx, p_tmp)
        rx         = add_awgn(bfsk, fixed_snr, p_tmp, seed=55)
        bits_rx, _, _ = correlator_bfsk(rx, bits_tx, p_tmp)
        ber_vals.append(np.mean(bits_tx != bits_rx))

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle(f"Figure 7 -- BER vs. Tone Spacing  (Eb/N0 = {fixed_snr} dB fixed)")

    ax.bar([f"{v:.2f}" for v in df_norm_arr], ber_vals,
           color=COLORS["fsk_f1"], edgecolor=COLORS["fsk_f2"], linewidth=0.8)

    # Mark orthogonal spacings
    orth_norms = [0.5, 1.0, 1.5, 2.0]
    for on in orth_norms:
        if on in df_norm_arr:
            idx = list(df_norm_arr).index(on)
            ax.annotate("Orthogonal", xy=(idx, ber_vals[idx]),
                        xytext=(idx, ber_vals[idx] + 0.02),
                        arrowprops=dict(arrowstyle="->", color=COLORS["thresh"]),
                        fontsize=8, color=COLORS["thresh"], ha="center")

    ax.set_xlabel("Normalised Tone Spacing  Df / Rb")
    ax.set_ylabel("BER")
    ax.set_title("BER Sensitivity to FSK Tone Spacing")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    return fig

# -----------------------------------------------------------------------------
# 12. MAIN  -- Run & Save All Figures
# -----------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Experiment 9 -- ASK and BFSK Simulator")
    print("=" * 60)
    print(f"\n  Parameters:")
    print(f"    Rb     = {p.Rb} bps")
    print(f"    fs     = {p.fs} Hz  ({p.sps} samples/bit)")
    print(f"    fc     = {p.fc} Hz  (ASK carrier)")
    print(f"    f1/f2  = {p.f1} / {p.f2} Hz  (BFSK tones)")
    print(f"    df*Tb  = {abs(p.f2 - p.f1) / p.Rb:.2f}  "
          f"({'orthogonal' if abs(p.f2-p.f1) % (p.Rb/2) < 1 else 'NOT orthogonal'})")
    print(f"    Nbits  = {p.Nbits} per BER point\n")

    bits = generate_bits(p.Nbits, seed=42)

    figs = []

    print("  [1/7] Generating passband waveforms ...")
    figs.append(("fig1_passband_waveforms",     plot_passband_waveforms(bits, p)))

    print("  [2/7] Computing power spectra ...")
    figs.append(("fig2_power_spectra",          plot_power_spectra(bits, p)))

    print("  [3/7] Plotting correlator outputs ...")
    figs.append(("fig3_correlator_outputs",     plot_correlator_outputs(bits, p, EbN0_dB=10)))

    print("  [4/7] Drawing decision-statistic histograms ...")
    figs.append(("fig4_decision_histograms",    plot_decision_histograms(bits, p, EbN0_dB=8)))

    print("  [5/7] Running BER simulations ...")
    figs.append(("fig5_ber_curves",             plot_ber_curves(p)))

    print("  [6/7] Validating FSK orthogonality ...")
    figs.append(("fig6_orthogonality",          plot_orthogonality(p)))

    print("  [7/7] Sweeping tone spacing ...")
    figs.append(("fig7_tone_spacing_ber",       plot_tone_spacing_ber(p)))

    print("\n  Saving figures to PNG ...")
    for name, fig in figs:
        path = f"{name}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"    Saved: {path}")

    print("\n  Displaying figures ...")
    pass  # plt.show() disabled for headless run

    print("\n  Done. All figures saved.\n")


if __name__ == "__main__":
    main()
