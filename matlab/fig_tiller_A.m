function fig_tiller_A()
% Удельная работа фрезерования в зависимости от скорости.
C = rp_init();
T = rp_read('till_points'); Mo = rp_read('models');
f = rp_fig(12.0, 9.0);
ax = rp_ax(f, [1.9, 2.9, 9.6, 5.8]);
A = [0.08 0.12 0.16];
for j = 1:3
    s = abs(T.a - A(j)) < 1e-6;
    plot(ax, T.v(s), T.A(s), C.mk{j}, 'Color', C.blues(j, :), 'MarkerFaceColor', C.blues(j, :), 'MarkerSize', 5, 'LineStyle', 'none');
    vv = [1.7 3.7];
    plot(ax, vv, Mo.A0 + Mo.A1 * vv + Mo.A2 * A(j), '-', 'Color', C.blues(j, :), 'LineWidth', 1.0);
end
xlim(ax, [1.6 3.8]); ylim(ax, [80 115]);
xlabel(ax, 'Скорость v, км/ч'); ylabel(ax, 'Удельная работа A, кДж/м^3');
rp_comma(ax, 'xy');
items = cell(1, 3);
for j = 1:3, items{j} = {['a = ' rp_num(A(j), 2) ' м'], C.blues(j, :), '-', C.mk{j}}; end
rp_key(f, [0.6, 0.1, 11.0, 0.8], items, 3);
rp_save(f, 'm_tiller_A');
end
