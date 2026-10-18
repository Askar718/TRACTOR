function ax = rp_canvas(f)
% RP_CANVAS  Оси во весь рисунок с единицами в сантиметрах (для схем).
s = getappdata(f, 'size_cm');
ax = axes('Parent', f, 'Units', 'normalized', 'Position', [0 0 1 1]);
set(ax, 'XLim', [0 s(1)], 'YLim', [0 s(2)], 'Visible', 'off', 'NextPlot', 'add');
end
