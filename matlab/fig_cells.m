function fig_cells()
% Состояние элементов батареи.
C = rp_init();
D = rp_read('cells');
f = rp_fig(16.5, 8.0);
ax = rp_ax(f, [1.7, 2.3, 6.5, 5.3]);
plot(ax, D.I, D.dU, '.', 'Color', C.et, 'MarkerSize', 3);
xlim(ax, [-20 240]); ylim(ax, [0 180]);
xlabel(ax, 'Ток батареи I, А'); ylabel(ax, 'Разброс напряжений ΔU, мВ');
rp_comma(ax, 'xy'); rp_panel(ax, 'а)', 1.25);
ax = rp_ax(f, [9.9, 2.3, 6.1, 5.3]);
plot(ax, D.SOC, D.Umin / 1000, '.', 'Color', C.d, 'MarkerSize', 3);
xlim(ax, [40 100]); ylim(ax, [2.9 3.4]);
xlabel(ax, 'SOC, %'); ylabel(ax, {'Наименьшее напряжение', 'элемента, В'});
rp_comma(ax, 'x'); rp_comma(ax, 'y', '%.1f'); rp_panel(ax, 'б)', 1.25);
rp_save(f, 'm_cells');
end
