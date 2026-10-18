function fig_session()
% Запись сессии с культиватором: мощность и степень заряженности батареи.
C = rp_init();
D = rp_read('session_C');
f = rp_fig(16.5, 10.0);
ax1 = rp_ax(f, [1.7 4.6 14.3 5.0]);
plot(ax1, D.t_min, D.P, '-', 'Color', C.et, 'LineWidth', 0.6);
xlim(ax1, [0 160]); ylim(ax1, [0 20]); set(ax1, 'XTickLabel', {});
ylabel(ax1, 'Мощность P, кВт');
rp_comma(ax1, 'y');
ax2 = rp_ax(f, [1.7 1.3 14.3 2.8]);
plot(ax2, D.t_min, D.SOC, '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.2);
xlim(ax2, [0 160]); ylim(ax2, [40 100]); set(ax2, 'YTick', 40:20:100);
xlabel(ax2, 'Время от начала записи, мин'); ylabel(ax2, 'SOC, %');
rp_save(f, 'm_session');
end
