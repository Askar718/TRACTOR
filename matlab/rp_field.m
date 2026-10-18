function cmapd = rp_field(ax, X, Y, Z, cmap, lims, nlev, G, H, mcol)
% RP_FIELD  Поле значений Z(Y, X) ступенчатой заливкой (nlev уровней); NaN не закрашиваются.
% Необязательные аргументы (непрерывные поля на той же сетке):
%   G — поле значений закрашиваются только там, где G >= 0;
%   H — ячейки, где H >= 0, закрашиваются сплошным цветом mcol.
xi = linspace(min(X), max(X), 301);
yi = linspace(min(Y), max(Y), 301);
[XX, YY] = meshgrid(X, Y);
[XI, YI] = meshgrid(xi, yi);
ZI = interp2(XX, YY, Z, XI, YI, 'linear');
step = (lims(2) - lims(1)) / nlev;
q = floor((ZI - lims(1)) / step);
q(q < 0) = 0; q(q > nlev - 1) = nlev - 1;
ZQ = lims(1) + (q + 0.5) * step;
ZQ(isnan(ZI)) = NaN;
idx = round(linspace(1, size(cmap, 1), nlev));
cmapd = cmap(idx, :);
cm = cmapd; top = lims(2);
if nargin >= 8 && ~isempty(G)
    ZQ(interp2(XX, YY, G, XI, YI, 'linear') < 0) = NaN;
end
if nargin >= 10 && ~isempty(H)
    ZQ(interp2(XX, YY, H, XI, YI, 'linear') >= 0) = lims(2) + 0.5 * step;
    cm = [cmapd; mcol]; top = lims(2) + step;
end
h = pcolor(ax, XI, YI, ZQ);
set(h, 'EdgeColor', 'none', 'FaceColor', 'flat');
colormap(ax, cm);
caxis(ax, [lims(1) top]);
end
