function [training_index, validation_index] = split_train_validation(agg, ratio)
    % Objective: adaptive binning split. The aggregate is divided into six bins of one standard deviation around its mean,
    %            the bins with more than 100 samples are kept and the same budget n_bin is drawn from each of them:
    %            floor(n_bin * ratio) samples for training and floor(n_bin * (1 - ratio)) for validation, without overlap.
    %            n_bin is the size of the smallest kept bin, capped at 1000 * ratio (cap kept from the original code).
    % Input: agg (column vector with the aggregate active power), ratio (training share, e.g. 0.7)
    % Output: training_index, validation_index (shuffled row indices into agg)

    [N, ~, bin] = histcounts(agg, mean(agg) + (-3:3) * std(agg));
    bins        = find(N > 100);
    if isempty(bins)
        error('split_train_validation: no aggregate bin has more than 100 samples');
    end
    n_bin       = min([1000 * ratio, N(bins)]);

    training_index      = [];
    validation_index    = [];
    for b = bins
        bin_samples         = find(bin == b);
        bin_training        = randsample(bin_samples, floor(n_bin * ratio));
        bin_validation      = randsample(setdiff(bin_samples, bin_training), floor(n_bin * (1 - ratio)));
        training_index      = [training_index; bin_training];
        validation_index    = [validation_index; bin_validation];
    end

    % Rearrange elements randomly
    training_index      = training_index(randperm(numel(training_index)));
    validation_index    = validation_index(randperm(numel(validation_index)));
end
