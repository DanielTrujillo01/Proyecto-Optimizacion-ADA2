% ==========================================
% PARAMETERS
% ==========================================
int: n; % Total people
int: m; % Number of opinions
float: ct; % Max cost (Original Float)
float: maxMovs; % Max movements

% Opinion Data
array[1..m] of float: v; % Real opinion value [0, 1]
array[1..m] of int: p;   % Initial distribution

% Resistance Data
array[1..m, 1..3] of int: s; 
array[1..3] of float: costo_resistencia=[1.0, 1.5, 2.0]; 

% ==========================================
% SCALING FACTOR (THE FIX)
% ==========================================
% We multiply floats by 10,000 to work with Integers.
float: F_SCALE = 10000.0;
int: I_SCALE = 10000;

% 1. Scale the Opinions (v -> v_int)
array[1..m] of int: v_int = [ round(v[i] * F_SCALE) | i in 1..m ];

% 2. Scale the Resistance Costs
array[1..3] of int: costo_res_int = [ round(costo_resistencia[k] * F_SCALE) | k in 1..3 ];

% 3. Scale the Max Cost Constraint
int: ct_int = round(ct * F_SCALE);

% 4. MaxMovs usually doesn't need scaling if it's just a count, 
% but we treat it as an int for the solver.
int: maxMovs_int = round(maxMovs);

% ==========================================
% DATA VALIDATION
% ==========================================
constraint assert(
    forall(i in 1..m)( sum(k in 1..3)(s[i,k]) == p[i] ),
    "Error: Sum of s[i,:] must equal p[i]"
);

% ==========================================
% DECISION VARIABLES (ALL INTEGERS NOW)
% ==========================================
array[1..m, 1..m, 1..3] of var 0..n: x;
array[1..m] of var 0..n: p_final;

% Median Index
var 1..m: median_idx;

% Variables for reports (Now Integers!)
var int: costo_total_int; % Scaled cost
var int: movs_total;      % Natural integer (no scale needed)

% ==========================================
% CONSTRAINTS
% ==========================================

% 1. Outgoing Flow Limit
constraint forall(i in 1..m, k in 1..3)(
    sum(j in 1..m where i != j)(x[i,j,k]) <= s[i,k]
);

% 2. No movement on same node
constraint forall(i in 1..m, k in 1..3)(
    x[i,i,k] = 0
);

% 3. Final Population (Conservation of Mass)
constraint forall(j in 1..m)(
    p_final[j] = p[j] 
                 + sum(i in 1..m, k in 1..3 where i != j)(x[i,j,k]) 
                 - sum(dest in 1..m, k in 1..3 where dest != j)(x[j,dest,k])
);

% 4. Costs and Moves
% Note: We use 'costo_res_int', so the result is SCALED.
constraint costo_total_int = sum(i, j in 1..m, k in 1..3 where i != j)(
    x[i,j,k] * abs(i - j) * costo_res_int[k]
);

constraint movs_total = sum(i, j in 1..m, k in 1..3 where i != j)(
    x[i,j,k] * abs(i - j)
);

% 5. Global Limits
constraint costo_total_int <= ct_int;
constraint movs_total <= maxMovs_int;

% ==========================================
% MEDIAN CALCULATION (INTEGER LOGIC)
% ==========================================
% Instead of "sum >= n / 2.0", we use "2 * sum >= n" to avoid floats.

constraint 2 * sum(j in 1..median_idx)(p_final[j]) >= n;

constraint if median_idx > 1 then
    2 * sum(j in 1..median_idx-1)(p_final[j]) < n
else 
    true 
endif;

% ==========================================
% OBJECTIVE FUNCTION (SCALED POLARIZATION)
% ==========================================

% We calculate polarization using the Scaled Opinions (v_int).
% Result: pol_int will be 10,000 times bigger than the real answer.
var int: pol_int = sum(j in 1..m)( 
    p_final[j] * abs(v_int[j] - v_int[median_idx]) 
);

solve minimize pol_int;

% ==========================================
% OUTPUT
% ==========================================
output [
    % We divide by F_SCALE to show the user the correct decimal (e.g. 1.488)
    show(pol_int / F_SCALE), "\n"
] ++
[
    show(k) ++ "\n" ++ 
    concat([
        concat([
            if j < m then show(x[i,j,k]) ++ "," else show(x[i,j,k]) endif
            | j in 1..m
        ]) ++ "\n"
        | i in 1..m
    ])
    | k in 1..3
];