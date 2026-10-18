function rp_comma(ax, which, fmt)
% RP_COMMA  Подписи делений с десятичной запятой (ГОСТ 2.105). which: 'x', 'y' или 'xy'.
if nargin < 3, fmt = '%g'; end
for c = which
    t = get(ax, [upper(c) 'Tick']);
    set(ax, [upper(c) 'TickMode'], 'manual', [upper(c) 'Tick'], t);
    lab = cell(1, numel(t));
    for i = 1:numel(t)
        v = t(i);
        if abs(v) < 1e-12, v = 0; end
        s = sprintf(fmt, v);
        s = strrep(s, '.', ',');
        s = strrep(s, '-', '−');
        lab{i} = s;
    end
    set(ax, [upper(c) 'TickLabel'], lab);
end
end
