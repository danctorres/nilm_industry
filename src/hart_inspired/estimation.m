function [estimation] = estimation(st_table, change_indices_table, agg)

    columnIndex = [];
    eq_change = [];
    sum_change_idx = find(abs(diff(sum(table2array(st_table(:, 2:8)), 2))) ~= 0);   % all the events
    for i = 1:size(st_table, 2) - 2
        for j = 1:size(sum_change_idx, 1)
            buff = find(change_indices_table{i} == sum_change_idx(j));      % find which equipment changes at each event
            if ~isempty(buff)
                columnIndex(j) = buff;
                eq_change(j) = i;
            end
        end
    end
    
    unchanged_indices = find(diff(eq_change) == 0) + 1;
    % eq_change(unchanged_indices)
    % sum_change_idx(unchanged_indices)
    % agg = agg_table.P_kW;
    % plot(agg)
    
    estimation = {};
    j = 0;
    while true
        for i = 1:size(unchanged_indices, 2)
            if (i == 1) % first equipment change
                % If equipment begins turn off or on
                % estimation{eq_change(1)} = sprintf('1 -> %d: %d', sum_change_idx(i), abs( agg(sum_change_idx(i)) - agg(0) ));
        
            elseif (i == size(sum_change_idx, 1))
                % If equipment end turn off or on
                % estimation{eq_change(end)} = sprintf('%d -> %d: %d', sum_change_idx(end), size(agg, 1), abs( agg(sum_change_idx(end) - agg(end) ));
        
            else
                eq_that_changes = eq_change(unchanged_indices(i));
                interval = [sum_change_idx(unchanged_indices(i) - 1) + 1, sum_change_idx(unchanged_indices(i))];
                if (numel(estimation) < eq_that_changes)
                    estimation{eq_that_changes} = abs( agg(interval(2)) - agg(interval(1)) );
                else
                    if isempty(estimation{eq_that_changes})
                        estimation{eq_that_changes} = abs( agg(interval(2)) - agg(interval(1)) );
                        % agg(interval(2) : interval(1)) = agg(interval(2) : interval(1)) - ;

                        % This is wrong, and the estimated values are not
                        % being save with reference for the interval,
                        % really incomplete
                    else
                        estimation{eq_that_changes} = [ estimation{eq_that_changes} abs( agg(interval(2)) - agg(interval(1)) ) ];
                    end
                end
            end
        end

        %% Delete
        eq_change(unchanged_indices) = [];
        unchanged_indices = find(diff(eq_change) == 0) + 1;
        % and subtract
        j = j + 1;
        if isempty(unchanged_indices)
            return;
        end
    end

end