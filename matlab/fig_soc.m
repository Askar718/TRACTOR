function fig_soc()
% Степень заряженности в зависимости от отданного заряда.
C = rp_init();
Mo = rp_read('models');
f = rp_fig(12.0, 9.0);
ax = rp_ax(f, [1.9, 2.9, 9.6, 5.8]);
names = {'C', 'T1', 'T2'}; cols = [C.et; C.d; C.g]; mk = {'o', 's', '^'};
for k = 1:3
    D = rp_read(['soc_' names{k}]);
    plot(ax, D.Ah, D.SOC, '-', 'Color', cols(k, :), 'LineWidth', 0.9);
    % маркеры со сдвигом между сериями, чтобы совпадающие линии были различимы
    q = (3 + 5 * (k - 1)):15:max(D.Ah);
    idx = arrayfun(@(x) find(D.Ah >= x, 1), q);
    plot(ax, D.Ah(idx), D.SOC(idx), mk{k}, 'Color', cols(k, :), 'MarkerFaceColor', 'w', ...
         'MarkerSize', 5, 'LineWidth', 1.1, 'LineStyle', 'none');
end
xx = [0 170];
plot(ax, xx, 98 - xx / Mo.C_Ah * 100, '--', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.0);
xlim(ax, xx); ylim(ax, [40 100]);
xlabel(ax, 'Отданный заряд Q, А·ч'); ylabel(ax, 'SOC по данным BMS, %');
items = {{'15.09 (культиватор)', C.et, '-', 'o', 'line', 'hollow'}, {'14.10 (фреза)', C.d, '-', 's', 'line', 'hollow'}, ...
         {'15.10 (фреза)', C.g, '-', '^', 'line', 'hollow'}, {'расчёт при C = 304 А·ч', [0.1 0.1 0.1], '--', 'none'}};
rp_key(f, [0.6, 0.1, 11.0, 1.0], items, 2);
rp_save(f, 'm_soc');
end
