function [results_cell] = statistical_diff_lvdb_aggregate(active_power, lvdb2_table, lvdb3_table, aggregate_table, visualize)
    % Objective: Analize the relationship between the measured values of lvdb2, lvdb3 and the equipment and the calculated aggregate power
    % Input: active_power, lvdb2_table, lvdb3_table, aggregate_tablepower_events_cell
    % Output: diff_mean_lvdb2, diff_mean_lvdb3, diff_mean_aggregate, diff_std_lvdb2, diff_std_lvdb3, diff_std_aggregate, r_lvdb2, r_lvdb3, r_aggregate, h_lvdb2, h_lvdb3, h_aggregate, p_anova_lvdb2, p_anova_lvdb3, p_anova_aggregate

    check_lvdb2 = sum(table2array(active_power(:, 2:5)), 2) +  sum(table2array(active_power(:, 8:9)), 2);
    check_lvdb3 = sum(table2array(active_power(:, 7:8)), 2);
    
    % aggregate = sum(table2array(active_power(:, 2:end)), 2);
    check_aggregate = check_lvdb2 + check_lvdb3;
    
    % difference_lvdb2 = abs(lvdb2_table.active_power - check_lvdb2);
    % difference_lvdb3 = abs(lvdb3_table.active_power - check_lvdb3);
    
    %  mean function to calculate the average of each array and compare the results.
    diff_mean_lvdb2     = mean(check_lvdb2) - mean(lvdb2_table.active_power);
    diff_mean_lvdb3     = mean(check_lvdb3) - mean(lvdb3_table.active_power);
    diff_mean_aggregate = mean(check_aggregate) - mean(aggregate_table.active_power);
    
    % std function to calculate the standard deviation of each array and compare the results.
    diff_std_lvdb2      = std(check_lvdb2) - std(lvdb2_table.active_power);
    diff_std_lvdb3      = std(check_lvdb3) - std(lvdb3_table.active_power);
    diff_std_aggregate  = std(check_aggregate) - std(aggregate_table.active_power);
    
    % corrcoef function to calculate the correlation between the two arrays and see how closely they are related.
    % -1 indicates a strong negative correlation, 0 indicates no correlation and 1 indicates a strong positive correlation.
    r_lvdb2     = corrcoef(check_lvdb2, lvdb2_table.active_power);
    r_lvdb3     = corrcoef(check_lvdb3, lvdb3_table.active_power);
    r_aggregate = corrcoef(check_aggregate, aggregate_table.active_power);
    
    % r_lvdb2(1, 2)
    
    % ttest function to perform a t-test to determine whether the means of the two arrays are significantly different.
    % h is a Boolean indicating whether the null hypothesis (that the means of the two samples are equal) value indicating can be rejected (h = 1) or not (h = 0).
    % p-value, which is the probability of obtaining the observed result.
    [h_lvdb2, ~]        = ttest(check_lvdb2, lvdb2_table.active_power);
    [h_lvdb3, ~]        = ttest(check_lvdb3, lvdb3_table.active_power);
    [h_aggregate, ~]    = ttest(check_aggregate, aggregate_table.active_power);
    
    % anova function to perform an analysis of variance (ANOVA) to determine whether the variance between the two arrays is significantly different.
    % if p-value is less than a threshold (usually 0.05), then can conclude that there are significant differences between the means of the groups.
    [p_anova_lvdb2, ~]      = anova1([check_lvdb2, lvdb2_table.active_power]);
    [p_anova_lvdb3, ~]      = anova1([check_lvdb3, lvdb3_table.active_power]);
    [p_anova_aggregate, ~]  = anova1([check_aggregate, aggregate_table.active_power]);
    
    
    results_cell = {diff_mean_lvdb2, diff_mean_lvdb3, diff_mean_aggregate, diff_std_lvdb2, diff_std_lvdb3, diff_std_aggregate, r_lvdb2, r_lvdb3, r_aggregate, h_lvdb2, h_lvdb3, h_aggregate, p_anova_lvdb2, p_anova_lvdb3, p_anova_aggregate};

    if (visualize == true)
        figure('units', 'normalized', 'outerposition', [0, 0, 1, 1])
        plot(check_lvdb2)
        hold on
        plot(lvdb2_table.active_power)
        legend('Equipment sum', 'lvdb2')
        xlabel('Seconds [s]')
        ylabel('Active Power [W]')
        title('Difference per sample lvdb2')
        
        figure,
        plot(check_lvdb3)
        hold on
        plot(lvdb3_table.active_power)
        legend('Equipment sum', 'lvdb2')
        xlabel('Seconds [s]')
        ylabel('Active Power [W]')
        title('Difference per sample lvdb3')


        figure,
        plot(check_aggregate)
        hold on
        plot(aggregate_table.active_power)
        legend('Equipment sum', 'Aggregate')
        xlabel('Seconds [s]')
        ylabel('Active Power [W]')
        title('Difference per sample aggregate')
    end
end