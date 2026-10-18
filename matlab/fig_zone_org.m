function fig_zone_org()
% Организационная зона: комплексный показатель в зависимости от сменного задания и удалённости зарядки.
C = rp_init();
key = {'cult', 'till'}; lt = {'а)', 'б)'};
f = rp_fig(16.5, 9.8);
for k = 1:2
    S = rp_mat(['zo_' key{k} '_S']); L = rp_mat(['zo_' key{k} '_L']);
    I = rp_mat(['zo_' key{k} '_I']); Ach = rp_mat(['zo_' key{k} '_Ach']);
    ax = rp_ax(f, [1.7 + (k-1)*7.0, 3.3, 5.3, 5.9]);
    cm = rp_field(ax, S, L, I, C.div, [-0.3 0.3], 12);
    contour(ax, S, L, I, [0 0], 'LineColor', [0.1 0.1 0.1], 'LineWidth', 1.4);
    plot(ax, Ach, L, ':', 'Color', [0.1 0.1 0.1], 'LineWidth', 1.4);
    xlim(ax, [min(S) max(S)]); ylim(ax, [0 4]);
    set(ax, 'XGrid', 'off', 'YGrid', 'off', 'Layer', 'top');
    xlabel(ax, 'Сменное задание S, га'); ylabel(ax, 'Удалённость места зарядки l, км');
    rp_comma(ax, 'xy'); rp_panel(ax, lt{k}, 1.2);
end
rp_cbar(f, [14.4, 3.3, 0.35, 5.9], cm, [-0.3 0.3], -0.3:0.1:0.3, '%.1f', 'Комплексный показатель I');
rp_key(f, [1.5, 0.1, 13.0, 0.7], {{'I = 0', [0.1 0.1 0.1], '-', 'none'}, {'площадь, обрабатываемая на одной зарядке', [0.1 0.1 0.1], ':', 'none'}}, 2);
rp_save(f, 'm_zone_org');
end
