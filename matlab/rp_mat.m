function X = rp_mat(name)
% RP_MAT  Чтение числовой матрицы без заголовка.
C = rp_init();
X = dlmread(fullfile(C.data, [name '.csv']), ',');
end
