function fig_energy_ha()
% Удельный расход энергии из батареи в зависимости от глубины обработки.
C = rp_init();
R = rp_read('regimes');
f = rp_fig(16.5, 9.4);
V = {[3.6 4.5 5.4], [1.8 2.7 3.6]};
lt = {'а)', 'б)'};
yl = {[14 34], [24 60]};
for k = 1:2
    ax = rp_ax(f, [1.7 + (k-1)*8.2, 3.5, 6.5, 5.6]);
    for j = 1:3
        s = R.impl == k & abs(R.v - V{k}(j)) < 1e-6;
        [aa, o] = sort(R.a_mean(s) * 100); ee = R.e(s); ci = R.e_ci(s);
        eb = errorbar(ax, aa, ee(o), ci(o), ['-' C.mk{j}]);
        set(eb, 'Color', C.oranges(j, :), 'MarkerFaceColor', C.oranges(j, :), 'MarkerSize', 5, 'LineWidth', 1.1);
    end
    xlim(ax, [7 17]); ylim(ax, yl{k});
    xlabel(ax, 'Глубина обработки a, см'); ylabel(ax, 'Удельный расход e, кВт·ч/га');
    rp_comma(ax, 'xy');
    rp_panel(ax, lt{k}, 1.25);
    items = cell(1, 3);
    for j = 1:3, items{j} = {['v = ' rp_num(V{k}(j), 1) ' км/ч'], C.oranges(j, :), '-', C.mk{j}}; end
    rp_key(f, [0.9 + (k-1)*8.2, 0.15, 7.4, 0.9], items, 2);
end
rp_save(f, 'm_energy_ha');
end
