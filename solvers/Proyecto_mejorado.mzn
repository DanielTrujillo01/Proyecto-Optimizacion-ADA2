% ==========================================
% PARÁMETROS
% ==========================================
int: n; % Número total de personas
int: m; % Número de opiniones
float: ct; % Costo total máximo
float: maxMovs; % Cantidad máxima de movimientos (Esfuerzo o distancia total)



% Datos de las opiniones
array[1..m] of float: v; % Valor real de la opinión [0, 1]
array[1..m] of int: p;   % Distribución inicial de personas

% Resistencia: s[i,k] personas en opinión i con resistencia k
% k=1: Baja, k=2: Media, k=3: Alta
array[1..m, 1..3] of int: s; 

% Costos por nivel de resistencia (Multiplicadores)
array[1..3] of float: costo_resistencia = [1.0, 1.5, 2.0];

% ==========================================
% VALIDACIÓN DE DATOS (ASSERTIONS)
% ==========================================
% Verificamos que la suma de s[i,k] coincida con p[i]
constraint assert(
    forall(i in 1..m)( sum(k in 1..3)(s[i,k]) == p[i] ),
    "Error en datos: La suma de s[i,:] debe ser igual a p[i]"
);

% ==========================================
% VARIABLES DE DECISIÓN
% ==========================================
% x[i, j, k]: Personas que se mueven de i a j con nivel de resistencia k
% Nota: Permitimos x[i,i,k] pero su costo será 0 y no afecta el flujo neto.
array[1..m, 1..m, 1..3] of var 0..n: x;

% Población final en cada opinión
array[1..m] of var 0..n: p_final;

% indice Mediana
var 1..m: median_idx;

% Variables auxiliares para reportes (opcionales para el solver, útiles para output)
var float: costo_total;
var float: movs_total;

% ==========================================
% RESTRICCIONES
% ==========================================

% 1. No mover más personas de las que existen (Restricción de Flujo Saliente)
% Para cada opinión i y nivel k, la suma de gente que sale hacia cualquier j
% no puede superar la cantidad disponible s[i,k].
constraint forall(i in 1..m, k in 1..3)(
    sum(j in 1..m where i != j)(x[i,j,k]) <= s[i,k]
);

% 2. No se permiten movimientos "falsos" sobre el mismo nodo (opcional, limpia la solución)
constraint forall(i in 1..m, k in 1..3)(
    x[i,i,k] = 0
);

% 3. Definición de la Población Final (Conservación de masa)
% p_final[j] = p_inicial[j] + (Entrantes) - (Salientes)
constraint forall(j in 1..m)(
    p_final[j] = p[j] 
                 + sum(i in 1..m, k in 1..3 where i != j)(x[i,j,k])  % Entran a j
                 - sum(dest in 1..m, k in 1..3 where dest != j)(x[j,dest,k]) % Salen de j
);

% 4. Cálculo de Costos y Movimientos
% Costo = Cantidad * Distancia * FactorResistencia
costo_total = sum(i, j in 1..m, k in 1..3 where i != j)(
    x[i,j,k] * abs(i - j) * costo_resistencia[k]
);

% Movimientos = Cantidad * Distancia (Interpretando maxMovs como magnitud de cambio)
movs_total = sum(i, j in 1..m, k in 1..3 where i != j)(
    x[i,j,k] * abs(i - j)
);

%Calculo de la Mediana,la suma acumulativa hasta este indice debe ser al menos la mitad de la poblacion
constraint  sum(j in 1..median_idx)(p_final[j]) >= n / 2.0;

%La suma acumulativa hasta el indice previo (n/2 -1) debe ser menos que la mitad(Esto asegura que  tomamos el primer indice valido)
constraint if median_idx>1 then
    sum(j in 1..median_idx-1)(p_final[j])< n/2.0
    else 
      true
    endif;

% 5. Límites globales
constraint costo_total <= ct;
constraint movs_total <= maxMovs;

% ==========================================
% FUNCIÓN OBJETIVO: POLARIZACIÓN
% ==========================================

%obtenemos el valor actual de la mediana
var float: median = v[median_idx];

% Minimizar la dispersión absoluta respecto a la mediana
var float: pol = sum(j in 1..m)( 
    p_final[j] * abs(v[j] - median) 
);

solve minimize pol;

% ==========================================
% SALIDA (OUTPUT)
% ==========================================
output [
    show(pol), "\n"  % Prints the objective value (e.g., 0.0 or 1.2)
] ++
[
    show(k) ++ "\n" ++  % Prints the Resistance Level (1, 2, or 3)
    concat([
        % Prints the matrix row for this resistance
        concat([
            if j < m then show(x[i,j,k]) ++ "," else show(x[i,j,k]) endif
            | j in 1..m
        ]) ++ "\n"
        | i in 1..m
    ])
    | k in 1..3
];