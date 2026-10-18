function fig_balance()
% Распределение энергии и времени по видам работ.
C = rp_init();
B = rp_mat('balance_noh');
cols = [C.et; C.d; C.gray; C.g; C.y; 0.75 0.75 0.75; 0.92 0.92 0.92];
names = {'рабочий ход', 'развороты', 'переезды', 'гидросистема', 'вращение ротора', 'замеры', 'стоянка'};
ses = {'Культиватор, 15.09', 'Фреза, 14.10', 'Фреза, 15.10'};
f = rp_fig(16.5, 7.8);
data = {B(:, 1:7), B(:, 8:14) / 60};
xl = {'Энергия, кВт·ч', 'Время, ч'};
lt = {'а)', 'б)'};
for k = 1:2
    ax = rp_ax(f, [3.4 + (k-1)*6.8, 2.9, 5.6, 4.4]);
    h = barh(ax, 1:3, data{k}, 0.6, 'stacked');
    for j = 1:7, set(h(j), 'FaceColor', cols(j, :), 'EdgeColor', 'w', 'LineWidth', 0.5); end
    set(ax, 'YDir', 'reverse', 'YTick', 1:3, 'YGrid', 'off');
    if k == 1, set(ax, 'YTickLabel', ses); else, set(ax, 'YTickLabel', {}); end
    ylim(ax, [0.4 3.6]);
    xlabel(ax, xl{k});
    rp_comma(ax, 'x');
    rp_panel(ax, lt{k}, 1.15);
end
items = cell(1, 7);
for j = 1:7, items{j} = {names{j}, cols(j, :), 'none', 'none', 'patch'}; end
rp_key(f, [0.4 0.05 16.0 1.1], items, 4);
rp_save(f, 'm_balance');
end
