function fig_limit()
% Предельные режимы: мощность и частота вращения.
C = rp_init();
Dc = rp_read('limit_cult'); Dt = rp_read('limit_till'); Mo = rp_read('models');
f = rp_fig(16.5, 11.0);
S = {Dc, Dt};
y2 = {Dc.n, Dt.pto};
y2l = {{'Частота вращения', 'двигателя, мин^{-1}'}, {'Частота вращения', 'ВОМ, мин^{-1}'}};
y2lim = {[0 4000], [0 600]};
lt = {'а)', 'б)'};
for k = 1:2
    D = S{k};
    ax = rp_ax(f, [2.2 + (k-1)*8.1, 6.2, 5.7, 4.3]);
    plot(ax, [0 40], Mo.P_lim * [1 1], '--', 'Color', [0.75 0.10 0.10], 'LineWidth', 1.0);
    plot(ax, D.t, D.P, '-', 'Color', C.et, 'LineWidth', 1.3);
    xlim(ax, [0 40]); ylim(ax, [0 20]); set(ax, 'XTickLabel', {});
    ylabel(ax, 'Мощность P, кВт');
    text(1, Mo.P_lim + 0.9, 'предел 17,5 кВт', 'Parent', ax, 'FontSize', 9.5, 'Color', [0.75 0.10 0.10]);
    rp_comma(ax, 'y');
    ax2 = rp_ax(f, [2.2 + (k-1)*8.1, 2.0, 5.7, 3.6]);
    plot(ax2, D.t, y2{k}, '-', 'Color', C.g, 'LineWidth', 1.3);
    xlim(ax2, [0 40]); ylim(ax2, y2lim{k});
    xlabel(ax2, 'Время, с'); ylabel(ax2, y2l{k});
    rp_panel(ax2, lt{k}, 1.05);
end
rp_save(f, 'm_limit');
end
