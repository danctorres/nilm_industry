function [per_machine, aggregate] = calculate_all_errors(truth, estimates, convert_W_2_kW)
    % Objective: errors of each estimate file against its ground-truth file (pairs matched by position, checked by timestamp)
    % Input: truth{i} (timestamp, machine 1..M), estimates{i} (timestamp, measured aggregate, estimate 1..M), convert_W_2_kW
    % Output: per_machine (one row per file pair and machine),
    %         aggregate (one row per file pair: measured aggregate vs sum of the machine estimates)

    assert(numel(truth) == numel(estimates), 'Got %d ground-truth files and %d estimate files', numel(truth), numel(estimates));
    per_machine = table();
    aggregate   = table();
    for i = 1:numel(truth)
        assert(isequal(string(truth{i}{:, 1}), string(estimates{i}{:, 1})), 'Timestamps of ground-truth file %d and estimate file %d differ', i, i);
        true_vals   = truth{i}{:, 2:end};
        est_vals    = estimates{i}{:, 3:end};
        n           = size(true_vals, 2);
        assert(size(est_vals, 2) == n, 'Ground-truth file %d has %d machines, estimate file %d has %d', i, n, i, size(est_vals, 2));

        metrics     = calculate_error(true_vals, est_vals, convert_W_2_kW);
        metrics     = addvars(metrics, repmat(n, n, 1), string(truth{i}.Properties.VariableNames(2:end))', 'Before', 1, 'NewVariableNames', {'n_machines', 'machine'});
        per_machine = [per_machine; metrics];

        metrics     = calculate_error(estimates{i}{:, 2}, sum(est_vals, 2), convert_W_2_kW);
        aggregate   = [aggregate; addvars(metrics, n, 'Before', 1, 'NewVariableNames', 'n_machines')];
    end
end
