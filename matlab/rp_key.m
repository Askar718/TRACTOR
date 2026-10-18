function rp_key(f, pos, items, ncol)
% RP_KEY  Условные обозначения в отдельной области pos = [x y w h] (см) под графиками.
% items — массив ячеек: {подпись, цвет, тип линии ('-', '--', ':' или 'none'), маркер ('none', 'o', ...), тип}
% тип: 'line' — линия/маркер; 'patch' — прямоугольник заливки.
if nargin < 4, ncol = numel(items); end
s = getappdata(f, 'size_cm');
ax = axes('Parent', f, 'Units', 'normalized', 'Position', [pos(1)/s(1) pos(2)/s(2) pos(3)/s(1) pos(4)/s(2)]);
set(ax, 'XLim', [0 pos(3)], 'YLim', [0 pos(4)], 'Visible', 'off', 'NextPlot', 'add');
nrow = ceil(numel(items) / ncol);
cw = pos(3) / ncol;
rh = pos(4) / nrow;
for i = 1:numel(items)
    it = items{i};
    r = floor((i-1) / ncol);
    c = mod(i-1, ncol);
    x = c * cw + 0.1;
    y = pos(4) - (r + 0.5) * rh;
    kind = 'line';
    if numel(it) >= 5, kind = it{5}; end
    if strcmp(kind, 'patch')
        patch(ax, [x x+0.6 x+0.6 x], [y-0.15 y-0.15 y+0.15 y+0.15], it{2}, 'EdgeColor', 'none');
    else
        if ~strcmp(it{3}, 'none')
            plot(ax, [x x+0.7], [y y], 'LineStyle', it{3}, 'Color', it{2}, 'LineWidth', 1.2);
        end
        if ~strcmp(it{4}, 'none')
            mf = it{2};
            if numel(it) >= 6 && strcmp(it{6}, 'hollow'), mf = 'none'; end
            plot(ax, x+0.35, y, 'LineStyle', 'none', 'Marker', it{4}, 'Color', it{2}, ...
                 'MarkerFaceColor', mf, 'MarkerSize', 5, 'LineWidth', 1.0);
        end
    end
    text(x + 0.85, y, it{1}, 'Parent', ax, 'VerticalAlignment', 'middle', ...
         'FontName', 'Times New Roman', 'FontSize', 10);
end
end
