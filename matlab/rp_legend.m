function lg = rp_legend(ax, h, labels, pos, orient)
% RP_LEGEND  Легенда в заданном положении [x y w h] (см) вне поля графика.
if nargin < 5, orient = 'horizontal'; end
lg = legend(ax, h, labels, 'Orientation', orient);
set(lg, 'FontName', 'Times New Roman', 'FontSize', 10, 'Box', 'off');
if nargin > 3 && ~isempty(pos)
    f = get(ax, 'Parent');
    s = getappdata(f, 'size_cm');
    set(lg, 'Units', 'normalized', 'Position', [pos(1)/s(1) pos(2)/s(2) pos(3)/s(1) pos(4)/s(2)]);
end
rp_fix(ax);
end
