'use strict';

/**
 * DSP Module — Core digital signal processing for BPSK simulation
 * No external dependencies. Implements RRC filter, convolution, AWGN, BER.
 */
const DSP = (() => {
    let _s = 42;
    function seed(v) { _s = v >>> 0; }
    function random() {
        let t = (_s += 0x6D2B79F5) >>> 0;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
    function randn() {
        let u = random(), v = random();
        while (u === 0) u = random();
        return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
    }

    function designRRC(beta, span, sps) {
        const N = span * sps, h = new Float64Array(2 * N + 1);
        for (let n = -N; n <= N; n++) {
            const t = n / sps, idx = n + N;
            if (t === 0) {
                h[idx] = 1 - beta + 4 * beta / Math.PI;
            } else if (beta > 0 && Math.abs(Math.abs(t) - 1 / (4 * beta)) < 1e-8) {
                h[idx] = (beta / Math.SQRT2) * (
                    (1 + 2 / Math.PI) * Math.sin(Math.PI / (4 * beta)) +
                    (1 - 2 / Math.PI) * Math.cos(Math.PI / (4 * beta)));
            } else {
                const num = Math.sin(Math.PI * t * (1 - beta)) +
                    4 * beta * t * Math.cos(Math.PI * t * (1 + beta));
                const den = Math.PI * t * (1 - (4 * beta * t) ** 2);
                h[idx] = Math.abs(den) < 1e-12 ? (1 - beta + 4 * beta / Math.PI) : num / den;
            }
        }
        const e = Math.sqrt(h.reduce((s, v) => s + v * v, 0));
        for (let i = 0; i < h.length; i++) h[i] /= e;
        return Array.from(h);
    }

    function conv(x, h) {
        const out = new Float64Array(x.length + h.length - 1);
        for (let i = 0; i < x.length; i++) {
            if (x[i] === 0) continue;
            for (let j = 0; j < h.length; j++) out[i + j] += x[i] * h[j];
        }
        return Array.from(out);
    }

    function upsample(x, L) {
        const out = new Float64Array(x.length * L);
        for (let i = 0; i < x.length; i++) out[i * L] = x[i];
        return Array.from(out);
    }

    function bpsk(numBits) {
        const bits = [], syms = [];
        for (let i = 0; i < numBits; i++) {
            const b = random() < 0.5 ? 0 : 1;
            bits.push(b); syms.push(2 * b - 1);
        }
        return { bits, symbols: syms };
    }

    function awgn(sig, EbN0dB) {
        const sigma = Math.sqrt(1 / (2 * 10 ** (EbN0dB / 10)));
        return sig.map(s => s + sigma * randn());
    }

    function channel(sig, ir) {
        return ir.length === 1 && ir[0] === 1 ? sig.slice() : conv(sig, ir);
    }

    function ber(det, ref) {
        const len = Math.min(det.length, ref.length);
        let err = 0;
        for (let i = 0; i < len; i++) if (det[i] !== ref[i]) err++;
        return { ber: len > 0 ? err / len : 0, errors: err, total: len };
    }

    function eyeHeight(sig, sps) {
        const s = [];
        for (let i = 0; i < sig.length; i += sps) s.push(sig[i]);
        const up = s.filter(v => v > 0), lo = s.filter(v => v <= 0);
        if (!up.length || !lo.length) return 0;
        return Math.max(0, Math.min(...up) - Math.max(...lo));
    }

    function erfc(x) {
        const t = 1 / (1 + 0.3275911 * Math.abs(x));
        const p = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 +
            t * (-1.453152027 + t * 1.061405429))));
        const r = p * Math.exp(-x * x);
        return x >= 0 ? r : 2 - r;
    }
    function Q(x) { return 0.5 * erfc(x / Math.SQRT2); }

    return { seed, random, randn, designRRC, conv, upsample, bpsk, awgn, channel, ber, eyeHeight, Q, erfc };
})();
