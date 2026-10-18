function rp_cbar(f, pos, cmap, lims, ticks, fmt, label)
% RP_CBAR  Цветовая шкала в отдельной области pos = [x y w h] (см) с подписью справа.
s = getappdata(f, 'size_cm');
ax = axes('Parent', f, 'Units', 'normalized', 'Position', [pos(1)/s(1) pos(2)/s(2) pos(3)/s(1) pos(4)/s(2)]);
n = size(cmap, 1);
y = linspace(lims(1), lims(2), n + 1);
for i = 1:n
    patch(ax, [0 1 1 0], [y(i) y(i) y(i+1) y(i+1)], cmap(i, :), 'EdgeColor', 'none');
end
set(ax, 'XLim', [0 1], 'YLim', lims, 'XTick', [], 'YAxisLocation', 'right', 'Box', 'on', ...
        'FontName', 'Times New Roman', 'FontSize', 9.5, 'TickDir', 'in', 'Layer', 'top');
set(ax, 'YTick', ticks);
lab = cell(1, numel(ticks));
for i = 1:numel(ticks)
    v = ticks(i); if abs(v) < 1e-12, v = 0; end
    lab{i} = strrep(strrep(sprintf(fmt, v), '.', ','), '-', '−');
end
set(ax, 'YTickLabel', lab);
c = rp_canvas(f);
text(pos(1) + pos(3) + 1.25, pos(2) + pos(4)/2, label, 'Parent', c, 'Rotation', 90, ...
     'HorizontalAlignment', 'center', 'VerticalAlignment', 'middle', 'FontSize', 10);
end
