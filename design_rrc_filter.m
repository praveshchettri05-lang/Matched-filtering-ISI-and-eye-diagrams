function h = design_rrc_filter(beta, span, sps)
%DESIGN_RRC_FILTER  Root Raised Cosine (RRC) filter — no toolbox required
%
%   h = design_rrc_filter(beta, span, sps)
%
%   Inputs
%     beta  — Roll-off factor  (0 < beta <= 1)
%     span  — One-sided filter span in symbol periods
%             Total filter length = 2*span*sps + 1 taps
%     sps   — Samples per symbol (oversampling factor)
%
%   Output
%     h     — Filter coefficients, normalised to unit energy
%             so that  sum(h.^2) == 1.
%
%   The impulse response follows the standard RRC definition:
%
%       h(t) = [sin(pi·t(1-β)) + 4β·t·cos(pi·t(1+β))]
%              / [pi·t · (1 - (4β·t)²)]
%
%   with closed-form limits at the two singular points t = 0 and
%   |t| = 1/(4β).
%
%   Example
%     h = design_rrc_filter(0.35, 6, 8);   % 97-tap RRC filter
%
%   See also:  CONV, FILTER

% -----------------------------------------------------------------------
%  Validate inputs
% -----------------------------------------------------------------------
if beta < 0 || beta > 1
    error('design_rrc_filter:beta', 'Roll-off factor beta must be in [0, 1].');
end
if span < 1 || sps < 1
    error('design_rrc_filter:param', 'span and sps must be positive integers.');
end

% -----------------------------------------------------------------------
%  Compute sample times
% -----------------------------------------------------------------------
N = span * sps;                % half the filter order
n = -N : N;                   % symmetric sample indices
t = n / sps;                  % normalised time (symbol periods)

h = zeros(size(t));

for i = 1:length(t)
    ti = t(i);

    if ti == 0
        % ---- Limit at t = 0 ----
        h(i) = 1 - beta + 4*beta/pi;

    elseif beta > 0 && abs(abs(ti) - 1/(4*beta)) < 1e-8
        % ---- Limit at |t| = 1/(4*beta) ----
        h(i) = (beta / sqrt(2)) * ...
               ( (1 + 2/pi)*sin(pi/(4*beta)) + ...
                 (1 - 2/pi)*cos(pi/(4*beta)) );

    else
        % ---- General formula ----
        numerator   = sin(pi*ti*(1 - beta)) + ...
                      4*beta*ti * cos(pi*ti*(1 + beta));
        denominator = pi*ti * (1 - (4*beta*ti)^2);

        if abs(denominator) < 1e-12
            % Extra numerical guard (should not normally trigger)
            h(i) = 1 - beta + 4*beta/pi;
        else
            h(i) = numerator / denominator;
        end
    end
end

% -----------------------------------------------------------------------
%  Normalise to unit energy
% -----------------------------------------------------------------------
h = h / sqrt(sum(h.^2));

end
