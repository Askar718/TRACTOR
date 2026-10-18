function fig_index_mc()
% Распределения комплексного показателя по результатам метода Монте-Карло
% (режимы, выполнимые обеими машинами).
C = rp_init();
S = rp_read('compare_S1');
idx = find(S.feasET & S.feasD);
n = numel(idx);
lab = cell(1, n);
for i = 1:n, j = idx(i); lab{i} = rp_reglab(S.impl(j), S.a(j), S.v(j)); end
sc = {'S1', 'S2'}; lt = {'а)', 'б)'};
f = rp_fig(16.5, 12.6);
for k = 1:2
    X = rp_mat(['mc_' sc{k}]);
    X = X(:, idx);
    ax = rp_ax(f, [2.5 + (k-1)*7.2, 2.6, 6.3, 9.6]);
    patch(ax, [-0.4 0 0 -0.4], [0.4 0.4 n+0.6 n+0.6], [0.99 0.92 0.90], 'EdgeColor', 'none');
    patch(ax, [0 0.4 0.4 0], [0.4 0.4 n+0.6 n+0.6], [0.91 0.95 0.99], 'EdgeColor', 'none');
    for i = 1:n
        x = X(:, i);
        q = [rp_pct(x, 0.05) rp_pct(x, 0.25) rp_pct(x, 0.5) rp_pct(x, 0.75) rp_pct(x, 0.95)];
        if S.impl(idx(i)) == 1, col = C.et; else, col = C.d; end
        plot(ax, [q(1) q(2)], [i i], '-', 'Color', col, 'LineWidth', 1.0);
        plot(ax, [q(4) q(5)], [i i], '-', 'Color', col, 'LineWidth', 1.0);
        patch(ax, [q(2) q(4) q(4) q(2)], [i-0.3 i-0.3 i+0.3 i+0.3], 0.4*col + 0.6, 'EdgeColor', col);
        plot(ax, [q(3) q(3)], [i-0.3 i+0.3], '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.4);
    end
    plot(ax, [0 0], [0.4 n+0.6], '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 0.8);
    set(ax, 'YDir', 'reverse', 'YTick', 1:n, 'YGrid', 'off');
    if k == 1, set(ax, 'YTickLabel', lab); else, set(ax, 'YTickLabel', {}); end
    ylim(ax, [0.4 n + 0.6]); xlim(ax, [-0.4 0.4]); set(ax, 'XTick', -0.4:0.2:0.4);
    xlabel(ax, 'Комплексный показатель I');
    rp_comma(ax, 'x'); rp_panel(ax, lt{k}, 1.2);
end
rp_save(f, 'm_index_mc');
end
