function fig_dprofile()
% Нормированные разности показателей для характерных режимов.
C = rp_init();
names = {'I_1', 'I_2', 'I_3', 'I_4', 'I_5', 'I_6', 'I_7', 'I_8', 'I_9', 'I_{10}'};
sc = {'S1', 'S2'};
lt = {'а)', 'б)'};
f = rp_fig(16.5, 11.0);
for k = 1:2
    S = rp_read(['compare_' sc{k}]);
    r1 = find(S.impl == 1 & abs(S.a - 0.11) < 1e-6 & abs(S.v - 4.5) < 1e-6);
    r2 = find(S.impl == 2 & abs(S.a - 0.12) < 1e-6 & abs(S.v - 2.7) < 1e-6);
    d = zeros(10, 2);
    for i = 1:10
        fn = ['d_I' num2str(i)];
        d(i, :) = [S.(fn)(r1) S.(fn)(r2)];
    end
    ax = rp_ax(f, [1.6 + (k-1)*7.6, 2.8, 6.6, 7.6]);
    h = barh(ax, 1:10, d, 0.8, 'grouped');
    set(h(1), 'FaceColor', C.et, 'EdgeColor', 'none'); set(h(2), 'FaceColor', C.d, 'EdgeColor', 'none');
    plot(ax, [0 0], [0.4 10.6], '-', 'Color', [0.1 0.1 0.1], 'LineWidth', 0.8);
    set(ax, 'YDir', 'reverse', 'YTick', 1:10, 'YTickLabel', names, 'YGrid', 'off');
    ylim(ax, [0.4 10.6]); xlim(ax, [-1 1]); set(ax, 'XTick', -1:0.5:1);
    xlabel(ax, 'Нормированная разность d_i');
    rp_comma(ax, 'x'); rp_panel(ax, lt{k}, 1.2);
end
rp_key(f, [2.5, 0.15, 12.0, 0.7], {{'культиватор 0,11 м × 4,5 км/ч', C.et, 'none', 'none', 'patch'}, ...
       {'фреза 0,12 м × 2,7 км/ч', C.d, 'none', 'none', 'patch'}}, 2);
rp_save(f, 'm_dprofile');
end
