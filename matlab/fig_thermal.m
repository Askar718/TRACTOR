function fig_thermal()
% Тепловой режим двигателя хода.
C = rp_init();
D = rp_read('thermal_T1'); F = rp_read('thermal_fit'); Mo = rp_read('models');
R = mean(F.R_K_per_kW);
f = rp_fig(16.5, 9.4);
ax = rp_ax(f, [1.7, 3.5, 7.2, 5.4]);
plot(ax, D.t_min, D.T, '-', 'Color', C.et, 'LineWidth', 1.5);
plot(ax, D.t_min, D.Tm, '--', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.1);
xlim(ax, [0 150]); ylim(ax, [10 40]);
xlabel(ax, 'Время, мин'); ylabel(ax, 'Температура двигателя хода, °C');
rp_comma(ax, 'xy'); rp_panel(ax, 'а)', 1.25);
rp_key(f, [0.9, 0.1, 7.8, 0.9], {{'измерение', C.et, '-', 'none'}, {'модель', [0.1 0.1 0.1], '--', 'none'}}, 2);
ax = rp_ax(f, [10.6, 3.5, 5.7, 5.4]);
Pp = linspace(0, 17.5, 50);
Ta = [10 25 40];
for j = 1:3
    plot(ax, Pp, Ta(j) + R * (Pp - Mo.P_aux), '-', 'Color', C.oranges(j, :), 'LineWidth', 1.3);
end
xlim(ax, [0 17.5]); ylim(ax, [0 100]);
xlabel(ax, 'Длительная мощность P, кВт'); ylabel(ax, 'Установившаяся температура, °C');
rp_comma(ax, 'xy'); rp_panel(ax, 'б)', 1.25);
ang = atand(R * (5.4 / 100) / (5.7 / 17.5));   % наклон линий на рисунке, градусы
for j = 1:3
    x0 = 1.0;
    text(x0, Ta(j) + R * (x0 - Mo.P_aux) + 2.5, ['T_{окр} = ' num2str(Ta(j)) ' °C'], 'Parent', ax, ...
         'FontSize', 9.5, 'Color', C.oranges(j, :), 'Rotation', ang, ...
         'HorizontalAlignment', 'left', 'VerticalAlignment', 'bottom');
end
rp_save(f, 'm_thermal');
end
