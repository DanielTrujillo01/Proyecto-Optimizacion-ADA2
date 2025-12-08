% ==========================================
% FINAL MODEL – WORKS WITH SEPARATE .dzn FILE
% ==========================================
int: n;
int: m;
float: ct;
float: maxMovs;
array[1..m] of float: v;
array[1..m] of int: p;
array[1..m, 1..3] of int: s;
array[1..3] of float: costo_resistencia = [1.0, 1.5, 2.0];

% ---------- Integer scaling ----------
int: SCALE = 1000;
array[1..m] of int: v_int = [ round(v[i] * SCALE) | i in 1..m ];

int: COST_SCALE = 2;
array[1..3] of int: cr_int = [ round(costo_resistencia[k] * COST_SCALE) | k in 1..3 ];
int: ct_int = floor(ct * COST_SCALE);
int: maxMovs_int = floor(maxMovs);
int: half_pop = (n + 1) div 2;

% ==========================================
% VARIABLES
% ==========================================
array[1..m, 1..m, 1..3] of var 0..n: x;
array[1..m] of var 0..n: p_final;
var 1..m: median_idx;

var int: costo_total_int;
var int: movs_total;
var int: polarization_int;

% ==========================================
% CONSTRAINTS
% ==========================================
constraint forall(i in 1..m, k in 1..3)(
    sum(j in 1..m where i != j)(x[i,j,k]) <= s[i,k]
);

constraint forall(i in 1..m, k in 1..3)( x[i,i,k] = 0 );

constraint forall(j in 1..m)(
    p_final[j] = p[j]
               + sum(i in 1..m, k in 1..3 where i != j)(x[i,j,k])
               - sum(d in 1..m, k in 1..3 where d != j)(x[j,d,k])
);

constraint costo_total_int = sum(i,j in 1..m, k in 1..3 where i != j)(
    x[i,j,k] * abs(i-j) * cr_int[k]
);
constraint movs_total = sum(i,j in 1..m, k in 1..3 where i != j)(
    x[i,j,k] * abs(i-j)
);

constraint costo_total_int <= ct_int;
constraint movs_total <= maxMovs_int;

constraint sum(j in 1..median_idx)(p_final[j]) >= half_pop;
constraint if median_idx > 1 then
    sum(j in 1..median_idx-1)(p_final[j]) < half_pop
else true endif;

constraint polarization_int = sum(j in 1..m)(
    p_final[j] * abs(v_int[j] - v_int[median_idx])
);

solve minimize polarization_int;

% ==========================================
% OUTPUT – NO let, NO if, NO type errors ever
% ==========================================
output [
    % Polarization with exactly 3 decimal places, always (e.g. 1.488, 0.005, 1.000)
    show(polarization_int div SCALE) ++ "." ++
    show((polarization_int mod SCALE) div 100) ++
    show(((polarization_int mod SCALE) div 10) mod 10) ++
    show((polarization_int mod SCALE) mod 10) ++ "\n"
]
++
[ show(k) ++ "\n" ++
  concat(i in 1..m)(
      concat(j in 1..m)(
          show(x[i,j,k]) ++ if j < m then "," else "" endif
      ) ++ "\n"
  )
  | k in 1..3
];