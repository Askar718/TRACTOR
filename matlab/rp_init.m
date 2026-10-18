function C = rp_init()
% RP_INIT  Единые настройки оформления рисунков отчёта и палитра.
set(0, 'DefaultAxesFontName', 'Times New Roman', 'DefaultAxesFontSize', 10, ...
       'DefaultTextFontName', 'Times New Roman', 'DefaultTextFontSize', 10, ...
       'DefaultLineLineWidth', 1.2, 'DefaultAxesLineWidth', 0.6);
C.et   = [0.000 0.447 0.741];   % электротрактор
C.d    = [0.850 0.325 0.098];   % дизельный аналог
C.g    = [0.466 0.674 0.188];
C.v    = [0.494 0.184 0.556];
C.y    = [0.929 0.694 0.125];
C.gray = [0.45 0.45 0.45];
C.lgray = [0.85 0.85 0.85];
C.blues = [0.45 0.68 0.90; 0.00 0.447 0.741; 0.03 0.20 0.45];
C.oranges = [0.98 0.65 0.45; 0.85 0.325 0.098; 0.55 0.18 0.05];
C.mk = {'o', 's', '^'};
% расходящаяся шкала: красный (преимущество Д) – белый – синий (преимущество ЭТ)
n = 32;
r1 = [linspace(0.70, 1, n)', linspace(0.10, 1, n)', linspace(0.10, 1, n)'];
b1 = [linspace(1, 0.05, n)', linspace(1, 0.30, n)', linspace(1, 0.65, n)'];
C.div = [r1; b1(2:end, :)];
C.only = [0.78 0.86 0.74];   % области, выполнимые только электротрактором
C.data = fullfile(fileparts(mfilename('fullpath')), 'data');
C.out  = fullfile(fileparts(mfilename('fullpath')), '..', 'results', 'fig');
end
