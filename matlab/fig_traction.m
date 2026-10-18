function fig_traction()
% Удельное тяговое сопротивление культиватора и кривая буксования.
C = rp_init();
T = rp_read('cult_points'); Sc = rp_read('slip_curve'); Mo = rp_read('models');
f = rp_fig(16.5, 10.6);
ax = rp_ax(f, [1.7, 4.6, 6.1, 5.6]);
A = [0.08 0.11 0.14];
for j = 1:3
    s = abs(T.a - A(j)) < 1e-6;
    plot(ax, T.v2(s), T.k(s), C.mk{j}, 'Color', C.blues(j, :), 'MarkerFaceColor', C.blues(j, :), 'MarkerSize', 5, 'LineStyle', 'none');
end
xx = [0.8 2.5];
plot(ax, xx, Mo.k0 + Mo.eps * xx, '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.1);
xlim(ax, xx); ylim(ax, [32 42]);
xlabel(ax, 'Квадрат скорости v^2, м^2/с^2'); ylabel(ax, 'Удельное сопротивление k, кН/м^2');
rp_comma(ax, 'xy'); rp_panel(ax, 'а)', 1.75);
items = {};
for j = 1:3, items{end+1} = {['a = ' rp_num(A(j), 2) ' м'], C.blues(j, :), 'none', C.mk{j}}; end
items{end+1} = {'k = k_0 + εv^2', [0.1 0.1 0.1], '-', 'none'};
rp_key(f, [1.2, 0.1, 6.8, 1.9], items, 1);

ax = rp_ax(f, [9.7, 4.6, 6.2, 5.6]);
plot(ax, Sc.phi, Sc.slip, '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.1);
plot(ax, T.phi, T.slip, 'o', 'Color', C.et, 'MarkerFaceColor', C.et, 'MarkerSize', 5, 'LineStyle', 'none');
plot(ax, T.phiD, T.slipD, 's', 'Color', C.d, 'MarkerSize', 5, 'LineStyle', 'none', 'LineWidth', 1.0);
plot(ax, [0 0.6], Mo.slip_max * [1 1], '--', 'Color', [0.75 0.10 0.10], 'LineWidth', 1.0);
xlim(ax, [0 0.6]); ylim(ax, [0 25]);
xlabel(ax, {'Коэффициент использования', 'сцепного веса φ'}); ylabel(ax, 'Буксование δ, %');
rp_comma(ax, 'xy'); rp_panel(ax, 'б)', 1.75);
items = {{'опыт, ЭТ (1300 кг)', C.et, 'none', 'o'}, {'расчёт, Д (1140 кг)', C.d, 'none', 's'}, ...
         {'аппроксимация', [0.1 0.1 0.1], '-', 'none'}, {'δ = 16 % (ГОСТ 27021)', [0.75 0.10 0.10], '--', 'none'}};
rp_key(f, [9.2, 0.1, 6.8, 1.9], items, 1);
rp_save(f, 'm_traction');
end
