function fig_pass(which)
% Запись учётного прохода: мощность, ток тягового электродвигателя, частота вращения.
C = rp_init();
if strcmp(which, 'cult'), D = rp_read('pass_cult'); else, D = rp_read('pass_till'); end
s = D.stage == 1;
t = D.t(s) - D.t(find(s, 1));
z = D.zone(s);
P = D.P(s); I = D.I(s);
if strcmp(which, 'cult')
    Y3 = D.n(s); y3l = {'Частота вращения', 'двигателя, мин^{-1}'}; y3lim = [0 4000];
else
    Y3 = D.pto(s); y3l = {'Частота вращения', 'ВОМ, мин^{-1}'}; y3lim = [400 600];
end
f = rp_fig(16.5, 12.5);
Y = {P, I, Y3};
yl = {{'Мощность', 'P, кВт'}, {'Ток двигателя', 'хода, А'}, y3l};
lims = {[0 18], [0 200], y3lim};
tz = [min(t(z == 2)) max(t(z == 2))];
tmax = max(t);
for k = 1:3
    ax = rp_ax(f, [2.4, 9.0 - (k-1)*3.5, 13.6, 3.0]);
    patch(ax, [tz(1) tz(2) tz(2) tz(1)], [lims{k}(1) lims{k}(1) lims{k}(2) lims{k}(2)], ...
          [0.88 0.93 0.98], 'EdgeColor', 'none');
    plot(ax, t, Y{k}, '-', 'Color', C.et, 'LineWidth', 1.1);
    xlim(ax, [0 tmax]); ylim(ax, lims{k});
    ylabel(ax, yl{k});
    if k < 3, set(ax, 'XTickLabel', {}); else, xlabel(ax, 'Время от начала рабочего хода, с'); end
    rp_comma(ax, 'y');
    if k == 1
        tr = [0 min(t(z == 2))];
        text(mean(tr), 16.5, 'РУ', 'Parent', ax, 'HorizontalAlignment', 'center', 'FontSize', 10);
        text(mean(tz), 16.5, 'учётная делянка', 'Parent', ax, 'HorizontalAlignment', 'center', 'FontSize', 10);
        text(mean([tz(2) tmax]), 16.5, 'УВ', 'Parent', ax, 'HorizontalAlignment', 'center', 'FontSize', 10);
    end
end
rp_save(f, ['m_pass_' which]);
end
