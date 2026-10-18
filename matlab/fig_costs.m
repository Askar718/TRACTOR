function fig_costs()
% Структура удельных совокупных затрат.
C = rp_init();
S = rp_read('compare_S1');
sel = [1 0.08 3.6; 1 0.11 4.5; 2 0.08 2.7; 2 0.12 2.7];
M = []; lab = {};
for i = 1:4
    r = find(S.impl == sel(i,1) & abs(S.a - sel(i,2)) < 1e-6 & abs(S.v - sel(i,3)) < 1e-6);
    M(end+1, :) = [S.lab_ET(r) S.en_ET(r) S.rm_ET(r) S.cap_ET(r)] / 1000;
    lab{end+1} = ['ЭТ, ' rp_reglab(sel(i,1), sel(i,2), sel(i,3))];
    M(end+1, :) = [S.lab_D(r) S.en_D(r) S.rm_D(r) S.cap_D(r)] / 1000;
    lab{end+1} = ['Д, ' rp_reglab(sel(i,1), sel(i,2), sel(i,3))];
end
cols = [C.gray; C.g; C.y; C.v];
f = rp_fig(16.5, 10.2);
ax = rp_ax(f, [3.6, 3.2, 11.4, 6.6]);
yy = [1 2 3.5 4.5 6 7 8.5 9.5];
h = barh(ax, yy, M, 0.8, 'stacked');
for j = 1:4, set(h(j), 'FaceColor', cols(j, :), 'EdgeColor', 'w'); end
tot = sum(M, 2);
for i = 1:8
    text(tot(i) + 0.3, yy(i), rp_num(tot(i), 1), 'Parent', ax, 'VerticalAlignment', 'middle', 'FontSize', 9.5);
end
set(ax, 'YDir', 'reverse', 'YTick', yy, 'YTickLabel', lab, 'YGrid', 'off');
ylim(ax, [0.3 10.2]); xlim(ax, [0 20]);
xlabel(ax, 'Удельные совокупные затраты, тыс. тг/га');
rp_comma(ax, 'x');
rp_key(f, [0.3, 0.1, 15.9, 1.2], {{'оплата труда', cols(1,:), 'none', 'none', 'patch'}, ...
       {'энергия, топливо', cols(2,:), 'none', 'none', 'patch'}, {'ремонт и ТО', cols(3,:), 'none', 'none', 'patch'}, ...
       {'капитальные затраты', cols(4,:), 'none', 'none', 'patch'}}, 2);
rp_save(f, 'm_costs');
end
