function fig_zone_tech(sc)
% Технологическая зона: допустимые режимы и комплексный показатель.
C = rp_init();
R = rp_read('regimes');
key = {'cult', 'till'};
f = rp_fig(16.5, 11.0);
lt = {'а)', 'б)'};
for k = 1:2
    A = rp_mat(['zt_' key{k} '_A']) * 100;
    V = rp_mat(['zt_' key{k} '_V']);
    I = rp_mat(['zt_' key{k} '_I_' sc]);
    mE = rp_mat(['zt_' key{k} '_mrg_ET']); mD = rp_mat(['zt_' key{k} '_mrg_D']); mC = rp_mat(['zt_' key{k} '_mrg_cont']);
    both = min(mE, mD);                 % >= 0: режим выполним обеими машинами
    onlyE = min(mE, -mD);               % >= 0: режим выполним только электротрактором
    ax = rp_ax(f, [1.7 + (k-1)*7.0, 4.5, 5.3, 5.5]);
    cm = rp_field(ax, V, A, I, C.div, [-0.3 0.3], 12, both, onlyE, C.only);
    contour(ax, V, A, mE, [0 0], 'LineColor', C.et, 'LineWidth', 2.0);
    contour(ax, V, A, mD, [0 0], 'LineColor', C.d, 'LineWidth', 2.0, 'LineStyle', '--');
    contour(ax, V, A, mC, [0 0], 'LineColor', [0.1 0.1 0.1], 'LineWidth', 1.0, 'LineStyle', ':');
    Im = I; Im(both < 0) = NaN;
    if any(Im(:) < 0) && any(Im(:) > 0)
        contour(ax, V, A, Im, [0 0], 'LineColor', [0.1 0.1 0.1], 'LineWidth', 1.2);
    end
    s = R.impl == k;
    plot(ax, R.v(s), R.a(s) * 100, 'k+', 'MarkerSize', 7, 'LineWidth', 1.0);
    xlim(ax, [min(V) max(V)]); ylim(ax, [min(A) max(A)]);
    set(ax, 'XGrid', 'off', 'YGrid', 'off', 'Layer', 'top');
    xlabel(ax, 'Скорость v, км/ч'); ylabel(ax, 'Глубина обработки a, см');
    rp_comma(ax, 'xy'); rp_panel(ax, lt{k}, 1.2);
end
rp_cbar(f, [14.4, 4.5, 0.35, 5.5], cm, [-0.3 0.3], -0.3:0.1:0.3, '%.1f', 'Комплексный показатель I');
items = {{'граница режимов ЭТ', C.et, '-', 'none'}, {'граница режимов Д', C.d, '--', 'none'}, ...
         {'граница длительного режима ЭТ', [0.1 0.1 0.1], ':', 'none'}, {'граница I = 0', [0.1 0.1 0.1], '-', 'none'}, ...
         {'режимы, выполнимые только ЭТ', C.only, 'none', 'none', 'patch'}, {'опытные режимы', [0.1 0.1 0.1], 'none', '+'}};
rp_key(f, [1.0, 0.1, 14.5, 1.9], items, 2);
rp_save(f, ['m_zone_tech_' sc]);
end
