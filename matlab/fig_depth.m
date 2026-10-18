function fig_depth()
% Фактическая глубина обработки в зависимости от заданной.
C = rp_init();
D = rp_read('depth');
f = rp_fig(16.5, 9.6);
L = {[6 16], [6 18]};
lt = {'а)', 'б)'};
for k = 1:2
    ax = rp_ax(f, [1.7 + (k-1)*8.1, 3.7, 6.3, 5.4]);
    x = L{k};
    patch(ax, [x(1) x(2) x(2) x(1)], [x(1)-1 x(2)-1 x(2)+1 x(1)+1], [0.88 0.93 0.98], 'EdgeColor', 'none');
    plot(ax, x, x, '-', 'Color', [0.3 0.3 0.3], 'LineWidth', 0.8);
    s = D.impl == k;
    vv = unique(D.v_plan(s));
    for j = 1:numel(vv)
        q = s & abs(D.v_plan - vv(j)) < 1e-6;
        eb = errorbar(ax, D.a_plan(q) * 100 + (j - 2) * 0.35, D.a_cm(q), D.sd_cm(q), C.mk{j});
        set(eb, 'Color', C.oranges(j, :), 'MarkerFaceColor', C.oranges(j, :), 'MarkerSize', 4, 'LineStyle', 'none');
    end
    xlim(ax, x); ylim(ax, x);
    xlabel(ax, 'Заданная глубина, см'); ylabel(ax, 'Фактическая глубина, см');
    rp_panel(ax, lt{k}, 1.2);
    items = cell(1, numel(vv));
    for j = 1:numel(vv)
        items{j} = {['v = ' rp_num(vv(j), 1) ' км/ч'], C.oranges(j, :), 'none', C.mk{j}};
    end
    rp_key(f, [1.0 + (k-1)*8.1, 0.1, 7.4, 1.1], items, 2);
end
rp_save(f, 'm_depth');
end
