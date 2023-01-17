function [R] = select_feature(features, aggregate_power)
    [R] = corrcoef(features, aggregate_power);
end