function fig_diesel()
% Модель расхода топлива дизельного аналога (ASAE D497.7).
C = rp_init();
Mo = rp_read('models'); S = rp_read('compare_S1');
Pn = Mo.P_pto_nom;
X = linspace(0.1, 1, 100);
f = rp_fig(16.5, 9.4);
ax = rp_ax(f, [1.7, 3.5, 6.5, 5.4]);
plot(ax, X * Pn, Mo.sfc_a * X * Pn + Mo.sfc_b * Pn, '-', 'Color', C.d, 'LineWidth', 1.4);
plot(ax, S.PD(S.impl == 1), S.Q(S.impl == 1), 'o', 'Color', [0.1 0.1 0.1], 'MarkerSize', 5, 'LineStyle', 'none');
plot(ax, S.PD(S.impl == 2), S.Q(S.impl == 2), 's', 'Color', [0.1 0.1 0.1], 'MarkerSize', 5, 'LineStyle', 'none');
xlim(ax, [0 17]); ylim(ax, [0 6]);
xlabel(ax, 'Мощность на входе трансмиссии P, кВт'); ylabel(ax, 'Часовой расход топлива Q, л/ч');
rp_comma(ax, 'xy'); rp_panel(ax, 'а)', 1.25);
ax = rp_ax(f, [9.9, 3.5, 6.4, 5.4]);
plot(ax, X, 1000 * Mo.rho_D * (Mo.sfc_a + Mo.sfc_b ./ X), '-', 'Color', C.d, 'LineWidth', 1.4);
plot(ax, S.X(S.impl == 1), 1000 * Mo.rho_D * (Mo.sfc_a + Mo.sfc_b ./ S.X(S.impl == 1)), 'o', 'Color', [0.1 0.1 0.1], 'MarkerSize', 5, 'LineStyle', 'none');
plot(ax, S.X(S.impl == 2), 1000 * Mo.rho_D * (Mo.sfc_a + Mo.sfc_b ./ S.X(S.impl == 2)), 's', 'Color', [0.1 0.1 0.1], 'MarkerSize', 5, 'LineStyle', 'none');
xlim(ax, [0 1]); ylim(ax, [200 800]);
xlabel(ax, 'Загрузка X = P/P_{ВОМ ном}'); ylabel(ax, 'Удельный расход топлива, г/(кВт·ч)');
rp_comma(ax, 'xy'); rp_panel(ax, 'б)', 1.25);
items = {{'модель ASAE D497.7', C.d, '-', 'none'}, {'режимы с культиватором', [0.1 0.1 0.1], 'none', 'o', 'line', 'hollow'}, ...
         {'режимы с фрезой', [0.1 0.1 0.1], 'none', 's', 'line', 'hollow'}};
rp_key(f, [0.9, 0.15, 15.4, 0.7], items, 3);
rp_save(f, 'm_diesel');
end
