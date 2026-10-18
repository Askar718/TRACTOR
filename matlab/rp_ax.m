function ax = rp_ax(f, pos)
% RP_AX  Оси в заданном положении [слева снизу ширина высота] в сантиметрах.
s = getappdata(f, 'size_cm');
ax = axes('Parent', f, 'Units', 'normalized', ...
          'Position', [pos(1)/s(1) pos(2)/s(2) pos(3)/s(1) pos(4)/s(2)]);
set(ax, 'FontName', 'Times New Roman', 'FontSize', 10, 'Box', 'on', 'TickDir', 'in', ...
        'XGrid', 'on', 'YGrid', 'on', 'GridLineStyle', '-', 'Layer', 'top', 'NextPlot', 'add');
setappdata(ax, 'pos_cm', pos);
end
