function rp_save(f, name)
% RP_SAVE  Сохранение рисунка в PNG (300 точек на дюйм).
C = rp_init();
if ~exist(C.out, 'dir'), mkdir(C.out); end
print(f, fullfile(C.out, [name '.png']), '-dpng', '-r300');
close(f);
end
