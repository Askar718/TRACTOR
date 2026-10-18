function D = rp_read(name)
% RP_READ  Чтение числового CSV с заголовком в структуру (поле на столбец).
C = rp_init();
fn = fullfile(C.data, [name '.csv']);
fid = fopen(fn, 'r');
hdr = fgetl(fid);
fclose(fid);
cols = strsplit(hdr, ',');
X = dlmread(fn, ',', 1, 0);
D = struct();
for j = 1:numel(cols)
    D.(strtrim(cols{j})) = X(:, j);
end
end
