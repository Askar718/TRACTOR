function fig_weights()
% Весовые коэффициенты показателей.
C = rp_init();
W = rp_read('weights');
names = {'I_1', 'I_2', 'I_3', 'I_4', 'I_5', 'I_6', 'I_7', 'I_8', 'I_9', 'I_{10}'};
f = rp_fig(16.5, 8.4);
ax = rp_ax(f, [1.8, 2.4, 14.4, 5.6]);
h = bar(ax, 1:10, [W.w_ahp W.w_entropy W.w], 0.85, 'grouped');
set(h(1), 'FaceColor', C.et, 'EdgeColor', 'none'); set(h(2), 'FaceColor', C.g, 'EdgeColor', 'none');
set(h(3), 'FaceColor', [0.25 0.25 0.25], 'EdgeColor', 'none');
set(ax, 'XTick', 1:10, 'XTickLabel', names, 'XGrid', 'off');
xlim(ax, [0.4 10.6]); ylim(ax, [0 0.22]);
ylabel(ax, 'Весовой коэффициент');
rp_comma(ax, 'y', '%.2f');
rp_key(f, [1.5, 0.1, 14.5, 0.7], {{'метод анализа иерархий', C.et, 'none', 'none', 'patch'}, ...
       {'энтропийный метод', C.g, 'none', 'none', 'patch'}, {'итоговые (α = 0,5)', [0.25 0.25 0.25], 'none', 'none', 'patch'}}, 3);
rp_save(f, 'm_weights');
end
