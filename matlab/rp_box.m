function rp_box(ax, x, y, w, h, txt, fc, fs, fw)
% RP_BOX  Прямоугольник со скруглёнными углами и текстом по центру (единицы — см).
if nargin < 7, fc = [0.94 0.94 0.94]; end
if nargin < 8, fs = 9; end
if nargin < 9, fw = 'normal'; end
rectangle('Parent', ax, 'Position', [x y w h], 'Curvature', [min(0.25, 0.4/w) min(0.4, 0.4/h)], ...
          'FaceColor', fc, 'EdgeColor', [0.35 0.35 0.35], 'LineWidth', 0.7);
text(x + w/2, y + h/2, txt, 'Parent', ax, 'HorizontalAlignment', 'center', ...
     'VerticalAlignment', 'middle', 'FontName', 'Times New Roman', 'FontSize', fs, 'FontWeight', fw);
end
