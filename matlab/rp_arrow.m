function rp_arrow(ax, x1, y1, x2, y2, col)
% RP_ARROW  Стрелка из (x1, y1) в (x2, y2) в единицах осей (см).
if nargin < 6, col = [0.3 0.3 0.3]; end
plot(ax, [x1 x2], [y1 y2], '-', 'Color', col, 'LineWidth', 0.8);
L = hypot(x2 - x1, y2 - y1);
ux = (x2 - x1) / L; uy = (y2 - y1) / L;
a = 0.22; b = 0.09;
px = [x2, x2 - a*ux + b*uy, x2 - a*ux - b*uy];
py = [y2, y2 - a*uy - b*ux, y2 - a*uy + b*ux];
patch(ax, px, py, col, 'EdgeColor', col);
end
