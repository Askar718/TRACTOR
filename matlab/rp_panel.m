function rp_panel(ax, txt, dy)
% RP_PANEL  Обозначение части рисунка («а)», «б)») под осями на расстоянии dy, см.
if nargin < 3, dy = 1.25; end
pos = getappdata(ax, 'pos_cm');
text(0.5, -dy/pos(4), txt, 'Parent', ax, 'Units', 'normalized', 'HorizontalAlignment', 'center', ...
     'VerticalAlignment', 'top', 'FontName', 'Times New Roman', 'FontSize', 11);
end
