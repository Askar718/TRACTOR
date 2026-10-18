function fig_zone_org()
% Организационная зона: комплексный показатель в зависимости от сменного задания и удалённости
% места зарядки; область, где электротрактор не выполняет сменное задание, закрашена серым.
C = rp_init();
key = {'cult', 'till'}; lt = {'а)', 'б)'};
f = rp_fig(16.5, 10.6);
gray = [0.86 0.86 0.86];
hasI0 = false;
for k = 1:2
    S = rp_mat(['zo_' key{k} '_S']); L = rp_mat(['zo_' key{k} '_L']);
    I = rp_mat(['zo_' key{k} '_I']); Ach = rp_mat(['zo_' key{k} '_Ach']); Scap = rp_mat(['zo_' key{k} '_Scap']);
    [SS, LL] = meshgrid(S, L);
    Sc = repmat(Scap(:), 1, numel(S));
    ok = Sc - SS;                        % >= 0: задание выполнимо электротрактором
    ax = rp_ax(f, [1.7 + (k-1)*7.0, 4.1, 5.3, 5.9]);
    cm = rp_field(ax, S, L, I, C.div, [-0.3 0.3], 12, ok, -ok, gray);
    Im = I; Im(ok < 0) = NaN;
    if any(Im(:) < 0) && any(Im(:) > 0)
        hasI0 = true;
        contour(ax, S, L, Im, [0 0], 'LineColor', [0.1 0.1 0.1], 'LineWidth', 1.4);
    end
    plot(ax, Scap, L, '-', 'Color', [0.25 0.25 0.25], 'LineWidth', 1.6);
    plot(ax, Ach, L, ':', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.4);
    xlim(ax, [min(S) 2]); ylim(ax, [0 4]);
    set(ax, 'XGrid', 'off', 'YGrid', 'off', 'Layer', 'top', 'XTick', 0:0.5:2);
    xlabel(ax, 'Сменное задание S, га'); ylabel(ax, 'Удалённость места зарядки l, км');
    rp_comma(ax, 'xy'); rp_panel(ax, lt{k}, 1.2);
end
rp_cbar(f, [14.4, 4.1, 0.35, 5.9], cm, [-0.3 0.3], -0.3:0.1:0.3, '%.1f', 'Комплексный показатель I');
items = {{'наибольшее сменное задание, выполнимое электротрактором', [0.25 0.25 0.25], '-', 'none'}, ...
         {'площадь, обрабатываемая без подзарядки', [0.1 0.1 0.1], ':', 'none'}, ...
         {'задание не выполняется электротрактором', gray, 'none', 'none', 'patch'}};
if hasI0, items{end+1} = {'граница I = 0', [0.1 0.1 0.1], '-', 'none'}; end
rp_key(f, [1.5, 0.1, 13.0, 2.0], items, 1);
rp_save(f, 'm_zone_org');
end
