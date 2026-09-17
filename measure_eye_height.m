function eye_height = measure_eye_height(signal, sps)
%MEASURE_EYE_HEIGHT  Measure vertical eye opening without plotting
%
%   eye_height = measure_eye_height(signal, sps)
%
%   Inputs
%     signal — Real-valued baseband signal (after matched filtering
%              and delay compensation)
%     sps    — Samples per symbol
%
%   Output
%     eye_height — Vertical eye opening at the optimal sampling instant:
%                  min(upper rail) − max(lower rail).
%                  Returns 0 when the eye is fully closed.
%
%   The function down-samples the signal at every sps-th sample
%   (the ideal decision instants) and separates the resulting values
%   into positive (upper rail) and negative (lower rail) clusters.
%
%   Example
%     h = measure_eye_height(rx_filtered, 8);
%
%   See also:  PLOT_EYE_DIAGRAM

signal = signal(:).';                % ensure row vector

% Down-sample at ideal decision instants
samples = signal(1 : sps : end);

% Separate into upper and lower rails
upper = samples(samples > 0);
lower = samples(samples <= 0);

if isempty(upper) || isempty(lower)
    eye_height = 0;
else
    eye_height = min(upper) - max(lower);
    eye_height = max(eye_height, 0);       % clamp to zero
end

end
