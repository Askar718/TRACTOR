function q = rp_pct(x, p)
% RP_PCT  Выборочный квантиль уровня p (линейная интерполяция, без пакетов расширения).
x = sort(x(:));
n = numel(x);
r = 1 + (n - 1) * p;
lo = floor(r); hi = ceil(r);
q = x(lo) + (r - lo) * (x(hi) - x(lo));
end
