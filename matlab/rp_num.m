function s = rp_num(x, d)
% RP_NUM  Число с десятичной запятой и d знаками после неё.
s = strrep(sprintf(['%.' num2str(d) 'f'], x), '.', ',');
end
