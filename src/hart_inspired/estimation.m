function [est] = estimation(states, agg, ALL_EVENTS_AGG_IDX, ALL_EVENTS_EQ_ID, ALL_EVENTS_STATE_CHANGE)
    est = [];
    size_ALL_EVENTS_AGG_IDX = size(ALL_EVENTS_AGG_IDX, 1);
    
    i = 1;
    while i < size_ALL_EVENTS_AGG_IDX
        if ALL_EVENTS_STATE_CHANGE(i) == 1     % if an event if caused by one turn on
            % find next event of that equipment turn off
            eq_id_event_causing = ALL_EVENTS_EQ_ID(i);
            next_eq_event = find (ALL_EVENTS_EQ_ID == eq_id_event_causing);
            if ~isempty(next_eq_event) && size(next_eq_event, 1) > 1
                next_eq_event = next_eq_event(2);

                current_event_idx = ALL_EVENTS_AGG_IDX(i) + 1;
                next_eq_event_idx = ALL_EVENTS_AGG_IDX(next_eq_event);
    
                % check other eq states
                states_current_event = states(current_event_idx, :);
                states_next_event = states(next_eq_event_idx, :);
    
                states_current_event(eq_id_event_causing) = [];
                states_current_event(states_current_event ~= 0 & states_current_event ~= 1) = [];
                states_next_event(eq_id_event_causing) = [];
                states_next_event(states_next_event ~= 0 & states_next_event ~= 1) = [];
    
                states_equal = isequal(states_current_event, states_next_event);
    
                if states_equal
                    agg_interval_power_diff = abs( agg(current_event_idx) - agg(next_eq_event_idx) );
                    est(current_event_idx : next_eq_event_idx, eq_id_event_causing) = agg_interval_power_diff;
    
                    agg(current_event_idx : next_eq_event_idx - 1) = agg(current_event_idx : next_eq_event_idx - 1) - agg_interval_power_diff;
                    states(current_event_idx, eq_id_event_causing) = 2; % give a number different from 0 or 1
    
                    ALL_EVENTS_AGG_IDX(i) = [];
                    ALL_EVENTS_EQ_ID(i) = [];
                    ALL_EVENTS_STATE_CHANGE(i) = [];

                    size_ALL_EVENTS_AGG_IDX = size(ALL_EVENTS_AGG_IDX)
                    i = 1;  % start again
                else
                    i = i + 1;
                end
            else
                i = i + 1;
            end
        else
            i = i + 1;
        end
    end
    figure
    plot(agg)

end