function fig_cmp_energy()
% Подведённая и первичная энергия, выбросы CO2 на 1 га: ЭТ и дизельный аналог.
C = rp_init();
S = rp_read('compare_S1');
n = numel(S.a);
lab = cell(1, n);
for i = 1:n, lab{i} = rp_reglab(S.impl(i), S.a(i), S.v(i), S.feasET(i), S.feasD(i)); end
f = rp_fig(16.5, 13.0);
V = {[S.ET_I1 S.D_I1], [S.ET_I2 S.D_I2], [S.ET_I8 S.D_I8]};
xl = {'I_1, МДж/га', 'I_2, МДж/га', 'I_8, кг CO_2/га'};
xm = [700 800 55]; xt = {0:200:600, 0:200:600, 0:10:50};
lt = {'а)', 'б)', 'в)'};
for k = 1:3
    ax = rp_ax(f, [2.6 + (k-1)*4.6, 3.0, 4.1, 9.6]);
    h = barh(ax, 1:n, V{k}, 0.8, 'grouped');
    set(h(1), 'FaceColor', C.et, 'EdgeColor', 'none'); set(h(2), 'FaceColor', C.d, 'EdgeColor', 'none');
    set(ax, 'YDir', 'reverse', 'YTick', 1:n, 'YGrid', 'off');
    if k == 1, set(ax, 'YTickLabel', lab); else, set(ax, 'YTickLabel', {}); end
    ylim(ax, [0.4 n + 0.6]); xlim(ax, [0 xm(k)]); set(ax, 'XTick', xt{k});
    xlabel(ax, xl{k});
    rp_comma(ax, 'x'); rp_panel(ax, lt{k}, 1.2);
end
rp_key(f, [3.0, 0.15, 12.0, 0.7], {{'электротрактор YL254ET', C.et, 'none', 'none', 'patch'}, ...
       {'дизельный аналог JM-254 (расчёт)', C.d, 'none', 'none', 'patch'}}, 2);
rp_save(f, 'm_cmp_energy');
end
