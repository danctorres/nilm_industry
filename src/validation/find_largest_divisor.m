function largest_divisor = find_largest_divisor(n)
    largest_divisor = 1;
    for i = 2:sqrt(n)
        if mod(n, i) == 0
            largest_divisor = max(largest_divisor, i);
            paired_divisor = n / i;
            largest_divisor = max(largest_divisor, paired_divisor);
        end
    end
end
