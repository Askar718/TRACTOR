function f = rp_fig(w, h)
% RP_FIG  Новый рисунок шириной w и высотой h (см) на белом фоне.
f = figure('Visible', 'off', 'Color', 'w', 'Units', 'centimeters', 'Position', [1 1 w h]);
set(f, 'PaperUnits', 'centimeters', 'PaperSize', [w h], 'PaperPositionMode', 'manual', ...
       'PaperPosition', [0 0 w h], 'InvertHardcopy', 'off');
setappdata(f, 'size_cm', [w h]);
end
