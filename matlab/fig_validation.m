function fig_validation()
% Сопоставление расчётной и измеренной мощности: модель по всем проходам и перекрёстная проверка.
C = rp_init();
D = rp_read('validation');
f = rp_fig(11.0, 10.8);
ax = rp_ax(f, [1.9, 4.5, 8.4, 5.9]);
plot(ax, [6 18], [6 18], '-', 'Color', [0.4 0.4 0.4], 'LineWidth', 0.8);
c = D.impl == 1; t = D.impl == 2;
% перекрёстная проверка – полые маркеры большего размера, под ними – заполненные маркеры модели
plot(ax, D.Pm(c), D.Pcv(c), 'o', 'Color', C.et, 'MarkerFaceColor', 'none', 'MarkerSize', 9, 'LineWidth', 1.0, 'LineStyle', 'none');
plot(ax, D.Pm(t), D.Pcv(t), 's', 'Color', C.d, 'MarkerFaceColor', 'none', 'MarkerSize', 9, 'LineWidth', 1.0, 'LineStyle', 'none');
plot(ax, D.Pm(c), D.Pc(c), 'o', 'Color', C.et, 'MarkerFaceColor', C.et, 'MarkerSize', 4, 'LineStyle', 'none');
plot(ax, D.Pm(t), D.Pc(t), 's', 'Color', C.d, 'MarkerFaceColor', C.d, 'MarkerSize', 4, 'LineStyle', 'none');
xlim(ax, [6 18]); ylim(ax, [6 18]);
xlabel(ax, 'Измеренная мощность, кВт'); ylabel(ax, 'Расчётная мощность, кВт');
rp_comma(ax, 'xy');
rp_key(f, [1.5, 0.1, 9.0, 2.4], {{'культиватор: модель', C.et, 'none', 'o'}, {'фреза: модель', C.d, 'none', 's'}, ...
       {'культиватор: перекрёстная проверка', C.et, 'none', 'o', 'line', 'hollow'}, ...
       {'фреза: перекрёстная проверка', C.d, 'none', 's', 'line', 'hollow'}}, 1);
rp_save(f, 'm_validation');
end
