function rp_fix(ax)
% RP_FIX  Восстанавливает положение осей (легенда и цветовая шкала могут его изменить).
f = get(ax, 'Parent');
s = getappdata(f, 'size_cm');
pos = getappdata(ax, 'pos_cm');
set(ax, 'Position', [pos(1)/s(1) pos(2)/s(2) pos(3)/s(1) pos(4)/s(2)]);
end
