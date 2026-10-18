function fig_zone_econ()
% Экономическая зона: экономия совокупных затрат ЭТ.
C = rp_init();
E = rp_read('econ_point');
key = {'cult', 'till'}; lt = {'а)', 'б)'};
f = rp_fig(16.5, 9.8);
for k = 1:2
    T = rp_mat(['ze_' key{k} '_T']); c = rp_mat(['ze_' key{k} '_c']); dC = rp_mat(['ze_' key{k} '_dC']);
    ax = rp_ax(f, [1.7 + (k-1)*7.0, 3.3, 5.3, 5.9]);
    cm = rp_field(ax, T, c, -dC, C.div, [-6 6], 12);
    contour(ax, T, c, dC, [0 0], 'LineColor', [0.1 0.1 0.1], 'LineWidth', 1.4);
    plot(ax, E.T_year, E.c_D, 'kp', 'MarkerFaceColor', 'k', 'MarkerSize', 9);
    xlim(ax, [min(T) max(T)]); ylim(ax, [min(c) max(c)]);
    set(ax, 'XGrid', 'off', 'YGrid', 'off', 'Layer', 'top', 'XTick', 300:300:1500);
    xlabel(ax, 'Годовая загрузка, ч'); ylabel(ax, 'Цена дизельного топлива, тг/л');
    rp_comma(ax, 'xy'); rp_panel(ax, lt{k}, 1.2);
end
rp_cbar(f, [14.4, 3.3, 0.35, 5.9], cm, [-6 6], -6:2:6, '%d', 'Экономия ЭТ, тыс. тг/га');
rp_key(f, [1.5, 0.1, 13.0, 0.7], {{'равенство совокупных затрат', [0.1 0.1 0.1], '-', 'none'}, ...
       {'условия октября 2026 г.', [0.1 0.1 0.1], 'none', 'p'}}, 2);
rp_save(f, 'm_zone_econ');
end
