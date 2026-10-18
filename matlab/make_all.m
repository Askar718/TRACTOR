% MAKE_ALL  Построение всех рисунков отчёта (MATLAB R2018b и новее; GNU Octave 8 и новее).
% Перед запуском выполните python3 src/export_matlab.py — он формирует matlab/data/*.csv.
here = fileparts(mfilename('fullpath'));
addpath(here);
figs = {'fig_method', 'fig_hierarchy', 'fig_session', 'fig_balance', '@() fig_pass(''cult'')', ...
        '@() fig_pass(''till'')', 'fig_limit', 'fig_power_v', 'fig_energy_ha', 'fig_traction', ...
        'fig_tiller_A', 'fig_soc', 'fig_cells', 'fig_thermal', 'fig_depth', 'fig_validation', ...
        'fig_diesel', 'fig_cmp_energy', 'fig_autonomy', 'fig_costs', 'fig_dprofile', 'fig_weights', ...
        'fig_index_mc', 'fig_tornado', '@() fig_zone_tech(''S1'')', '@() fig_zone_tech(''S2'')', ...
        'fig_zone_org', 'fig_zone_econ'};
for i = 1:numel(figs)
    try
        if figs{i}(1) == '@', feval(eval(figs{i})); else, feval(figs{i}); end
        fprintf('готово: %s\n', figs{i});
    catch err
        fprintf('ОШИБКА в %s: %s\n', figs{i}, err.message);
    end
end
