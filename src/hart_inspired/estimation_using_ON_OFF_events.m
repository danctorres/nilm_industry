function [est] = estimation_using_ON_OFF_events(states, agg, ALL_EVENTS_AGG_IDX, ALL_EVENTS_EQ_ID, ALL_EVENTS_STATE_CHANGE)
    est = -1 * ones(size(states));  % if an estimation cannot be made, it saves the value -1 for the interval
    est = est .* states;
    size_ALL_EVENTS_AGG_IDX = size(ALL_EVENTS_AGG_IDX, 1);
    
    i = 1;
    while i < size_ALL_EVENTS_AGG_IDX
        if ALL_EVENTS_STATE_CHANGE(i) == 1     % if an event if caused by one turn on
            % find next event of that equipment turn off
            eq_id_event_causing = ALL_EVENTS_EQ_ID(i);
            next_eq_event = find (ALL_EVENTS_EQ_ID(i + 1 : end) == eq_id_event_causing);
            if ~isempty(next_eq_event) && ALL_EVENTS_STATE_CHANGE(next_eq_event(1) + i) == -1  % just make sure that equipment turns off
                next_eq_event = next_eq_event(1) + i;

                current_event_idx = ALL_EVENTS_AGG_IDX(i);
                next_eq_event_idx = ALL_EVENTS_AGG_IDX(next_eq_event);
    
                % check other eq states
                states_current_event = states(current_event_idx, :);
                states_next_event = states(next_eq_event_idx, :);
    
                states_current_event(eq_id_event_causing) = [];
                states_next_event(eq_id_event_causing) = [];
    
                states_equal = isequal(states_current_event, states_next_event);
    
                if states_equal
                    agg_interval_power_diff = abs( agg(current_event_idx) - agg(next_eq_event_idx) );
                    est(current_event_idx : next_eq_event_idx, eq_id_event_causing) = agg_interval_power_diff;
    
                    agg(current_event_idx : next_eq_event_idx - 1) = agg(current_event_idx : next_eq_event_idx - 1) - agg_interval_power_diff;
                    states(current_event_idx : next_eq_event_idx - 1, eq_id_event_causing) = 0; % now consider that equipment OFF for that interval
     
%                      ALL_EVENTS_AGG_IDX(i) = [];
%                      ALL_EVENTS_EQ_ID(i) = [];
%                      ALL_EVENTS_STATE_CHANGE(i) = [];
% 
%                      size_ALL_EVENTS_AGG_IDX = size(ALL_EVENTS_AGG_IDX, 1);
%                      i = 1;
                end
            end
        end
         i = i + 1;
    end
    % figure
    % plot(agg)
    est(est == -1) = nan;
end