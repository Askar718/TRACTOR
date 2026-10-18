function fig_autonomy()
% Площадь, обрабатываемая без подзарядки, и сменная выработка.
C = rp_init();
S = rp_read('compare_S1');
n = numel(S.a);
lab = cell(1, n);
for i = 1:n, lab{i} = rp_reglab(S.impl(i), S.a(i), S.v(i), S.feasET(i), S.feasD(i)); end
f = rp_fig(16.5, 13.0);
ax = rp_ax(f, [2.5, 3.0, 5.6, 9.6]);
barh(ax, 1:n, S.Acharge, 0.6, 'FaceColor', C.et, 'EdgeColor', 'none');
set(ax, 'YDir', 'reverse', 'YTick', 1:n, 'YTickLabel', lab, 'YGrid', 'off');
ylim(ax, [0.4 n + 0.6]); xlim(ax, [0 1]);
xlabel(ax, 'Площадь без подзарядки, га');
rp_comma(ax, 'x'); rp_panel(ax, 'а)', 1.2);
ax = rp_ax(f, [9.4, 3.0, 6.9, 9.6]);
h = barh(ax, 1:n, [S.SET S.SD], 0.8, 'grouped');
set(h(1), 'FaceColor', C.et, 'EdgeColor', 'none'); set(h(2), 'FaceColor', C.d, 'EdgeColor', 'none');
set(ax, 'YDir', 'reverse', 'YTick', 1:n, 'YTickLabel', {}, 'YGrid', 'off');
ylim(ax, [0.4 n + 0.6]); xlim(ax, [0 4.5]);
xlabel(ax, 'Сменная выработка, га');
rp_comma(ax, 'x'); rp_panel(ax, 'б)', 1.2);
rp_key(f, [3.0, 0.15, 12.0, 0.7], {{'электротрактор (с подзарядкой)', C.et, 'none', 'none', 'patch'}, ...
       {'дизельный аналог', C.d, 'none', 'none', 'patch'}}, 2);
rp_save(f, 'm_autonomy');
end
