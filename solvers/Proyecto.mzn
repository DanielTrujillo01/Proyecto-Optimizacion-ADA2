% ==========================================
% PARÁMETROS DE ENTRADA 
% ==========================================
int: n;           
int: m;          
float: ct;        
float: maxMovs;   
float: mediana;   

% Valores de las opiniones 
array[1..m] of float: v; 

% Distribución inicial 
array[1..m] of int: p;   

% Matriz de Resistencia s[i,k]: Personas en opinión i con resistencia k
% k=1 (Baja), k=2 (Media), k=3 (Alta)
array[1..m, 1..3] of int: s; 

% Multiplicadores de costo por resistencia 
array[1..3] of float: costo_resistencia = [1.0, 1.5, 2.0];


% ==========================================
% VARIABLES DE DECISIÓN
% ==========================================
% x[i, j, k]: Cantidad de personas de resistencia k que pasan de la opinión i a la j.
% Si i == j, las personas MANTIENEN su opinión.
array[1..m, 1..m, 1..3] of var 0..n: x;

% Población final en cada opinión j
array[1..m] of var 0..n: p_final;

% Variables para reportar el uso de recursos
var float: costo_total;
var float: movs_total;

% ==========================================
% RESTRICCIONES
% ==========================================

% 1. Conservación de Flujo (Salida):
constraint forall(i in 1..m, k in 1..3)(
    sum(j in 1..m)(x[i,j,k]) == s[i,k]
);


% 2. Definición de la Población Final:
% La gente que termina en j es la suma de todos los que vinieron de cualquier i (incluido i=j)
constraint forall(j in 1..m)(
    p_final[j] = sum(i in 1..m, k in 1..3)(x[i,j,k])
);

% 4. Cálculo de Costo (Esfuerzo):
costo_total = sum(i, j in 1..m, k in 1..3)(
    x[i,j,k] * abs(i - j) * costo_resistencia[k]
);

% 5. Cálculo de Movimientos:
movs_total = sum(i, j in 1..m, k in 1..3)(
    x[i,j,k] * abs(i - j)
);

% 6. Límites de Recursos
constraint costo_total <= ct;
constraint movs_total <= maxMovs;

% ==========================================
% FUNCIÓN OBJETIVO: POLARIZACIÓN
% ==========================================
% Pol = Sum( p_final[j] * |v[j] - mediana| )
var float: pol = sum(j in 1..m)( 
    p_final[j] * abs(v[j] - mediana) 
);

solve minimize pol;

% ==========================================
% SALIDA
% ==========================================
output [
    show(pol), "\n"
] ++
[
    show(k) ++ "\n" ++
    concat([
        concat([
            show(x[i,j,k]) ++ (if j < m then "," else "" endif)
            | j in 1..m
        ]) ++ "\n"
        | i in 1..m
    ])
    | k in 1..3
];