function varargout = plot_eye_diagram(signal, sps, symbols_per_trace, title_str)
%PLOT_EYE_DIAGRAM  Reusable eye-diagram plotter — no toolbox required
%
%   plot_eye_diagram(signal, sps, symbols_per_trace, title_str)
%   eye_height = plot_eye_diagram(...)
%
%   Inputs
%     signal            — Real-valued baseband signal (row or column vector)
%     sps               — Samples per symbol
%     symbols_per_trace — Number of symbol periods per overlay trace
%                         (use 2 for a standard two-UI eye)
%     title_str         — Title string for the axes
%
%   Output (optional)
%     eye_height — Measured vertical eye opening at the optimal
%                  sampling instant:  min(upper rail) − max(lower rail).
%                  Returns 0 when the eye is fully closed.
%
%   The function overlays up to 500 traces of the signal, each offset
%   by one symbol period.  Traces are drawn with partial transparency
%   so that the density pattern of a real eye diagram is visible.
%
%   Example
%     plot_eye_diagram(rx_matched, 8, 2, 'BPSK Eye Diagram');
%
%   See also:  DESIGN_RRC_FILTER, MEASURE_EYE_HEIGHT

% -----------------------------------------------------------------------
%  Parameters
% -----------------------------------------------------------------------
MAX_TRACES  = 500;          % cap for plotting speed
TRACE_COLOR = [0 0 0.8];   % dark blue
TRACE_ALPHA = 0.12;        % transparency (requires R2014b+)
LINE_WIDTH  = 0.4;

% -----------------------------------------------------------------------
%  Prepare traces
% -----------------------------------------------------------------------
signal     = signal(:).';                        % ensure row vector
trace_len  = symbols_per_trace * sps;            % samples per trace
num_avail  = floor((length(signal) - trace_len) / sps);
num_traces = min(num_avail, MAX_TRACES);

t_axis = (0 : trace_len-1) / sps;               % x-axis in symbol periods

% -----------------------------------------------------------------------
%  Draw overlaid traces
% -----------------------------------------------------------------------
hold on;
center_samples = zeros(1, num_traces);           % for eye-height measurement
valid_count    = 0;

for k = 0 : num_traces-1
    start_idx = k * sps + 1;
    end_idx   = start_idx + trace_len - 1;

    if end_idx > length(signal)
        break;
    end

    trace = signal(start_idx : end_idx);
    plot(t_axis, trace, ...
         'Color', [TRACE_COLOR, TRACE_ALPHA], ...
         'LineWidth', LINE_WIDTH);

    % Sample at the centre of the trace (optimal decision point)
    centre_idx = sps + 1;                        % = 1 symbol period in
    if centre_idx <= trace_len
        valid_count = valid_count + 1;
        center_samples(valid_count) = trace(centre_idx);
    end
end
hold off;

% -----------------------------------------------------------------------
%  Annotate
% -----------------------------------------------------------------------
xlabel('Time (symbol periods)');
ylabel('Amplitude');
title(title_str);
grid on;

% -----------------------------------------------------------------------
%  Measure eye height
% -----------------------------------------------------------------------
center_samples = center_samples(1:valid_count);

if valid_count > 0
    upper = center_samples(center_samples > 0);
    lower = center_samples(center_samples <= 0);

    if ~isempty(upper) && ~isempty(lower)
        eye_h = min(upper) - max(lower);
        eye_h = max(eye_h, 0);
    else
        eye_h = 0;
    end
else
    eye_h = 0;
end

if nargout >= 1
    varargout{1} = eye_h;
end

end
