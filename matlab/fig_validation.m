function fig_validation()
% Сопоставление расчётной и измеренной мощности.
C = rp_init();
D = rp_read('validation');
f = rp_fig(10.0, 9.0);
ax = rp_ax(f, [1.9, 2.9, 7.6, 5.8]);
plot(ax, [6 18], [6 18], '-', 'Color', [0.4 0.4 0.4], 'LineWidth', 0.8);
plot(ax, D.Pm(D.impl == 1), D.Pc(D.impl == 1), 'o', 'Color', C.et, 'MarkerFaceColor', C.et, 'MarkerSize', 5, 'LineStyle', 'none');
plot(ax, D.Pm(D.impl == 2), D.Pc(D.impl == 2), 's', 'Color', C.d, 'MarkerFaceColor', C.d, 'MarkerSize', 5, 'LineStyle', 'none');
xlim(ax, [6 18]); ylim(ax, [6 18]);
xlabel(ax, 'Измеренная мощность, кВт'); ylabel(ax, 'Расчётная мощность, кВт');
rp_key(f, [0.8, 0.1, 9.0, 0.8], {{'культиватор', C.et, 'none', 'o'}, {'фреза', C.d, 'none', 's'}}, 2);
rp_save(f, 'm_validation');
end
