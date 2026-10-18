function fig_power_v()
% Мощность, потребляемая от батареи, в зависимости от скорости (опыт и модель).
C = rp_init();
R = rp_read('regimes');  M = rp_read('curves_power');  Mo = rp_read('models');
f = rp_fig(16.5, 9.4);
X = {[3.2 5.8], [1.5 3.9]};
A = {[0.08 0.11 0.14], [0.08 0.12 0.16]};
lt = {'а)', 'б)'};
for k = 1:2
    ax = rp_ax(f, [1.6 + (k-1)*8.1, 3.5, 6.6, 5.6]);
    h = zeros(1, 4);
    for j = 1:3
        a = A{k}(j);
        s = M.impl == k & abs(M.a - a) < 1e-6;
        plot(ax, M.v(s), M.P(s), '-', 'Color', C.blues(j, :), 'LineWidth', 1.0);
        s = R.impl == k & abs(R.a - a) < 1e-6;
        eb = errorbar(ax, R.v_mean(s), R.P(s), R.P_ci(s), C.mk{j});
        set(eb, 'Color', C.blues(j, :), 'MarkerFaceColor', C.blues(j, :), 'MarkerSize', 5, 'LineStyle', 'none');
        h(j) = eb;
    end
    h(4) = plot(ax, X{k}, Mo.P_lim * [1 1], '--', 'Color', [0.75 0.10 0.10], 'LineWidth', 1.0);
    xlim(ax, X{k}); ylim(ax, [5 19]);
    set(ax, 'YTick', 6:2:18);
    xlabel(ax, 'Скорость v, км/ч'); ylabel(ax, 'Мощность P, кВт');
    rp_comma(ax, 'xy');
    rp_panel(ax, lt{k}, 1.25);
    items = {};
    for j = 1:3
        items{end+1} = {['a = ' rp_num(A{k}(j), 2) ' м'], C.blues(j, :), '-', C.mk{j}};
    end
    items{end+1} = {'предел 17,5 кВт', [0.75 0.10 0.10], '--', 'none'};
    rp_key(f, [0.9 + (k-1)*8.1, 0.1, 7.4, 1.0], items, 2);
end
rp_save(f, 'm_power_v');
end
