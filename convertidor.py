import sys

def calcular_mediana_ponderada(valores, pesos):
    """
    Calcula la mediana ponderada.
    valores: lista de opiniones (v)
    pesos: cantidad de personas por opinion (p)
    """
    # Crear pares (valor, peso) y ordenarlos por valor
    datos = sorted(zip(valores, pesos), key=lambda x: x[0])
    
    total_personas = sum(pesos)
    mitad = total_personas / 2.0
    
    acumulado = 0
    for valor, peso in datos:
        acumulado += peso
        if acumulado >= mitad:
            return valor
    return datos[-1][0]

def convertir_txt_a_dzn(input_path, output_path):
    try:
        with open(input_path, 'r') as f:
            # Leer todas las lineas no vacias y quitar espacios extra
            lines = [line.strip() for line in f if line.strip()]

        # ---------------------------------------------------------
        # PARSEO DEL ARCHIVO TXT
        # ---------------------------------------------------------
        
        # 1. n: Número total de personas
        n = int(lines[0])
        
        # 2. m: Número de opiniones
        m = int(lines[1])
        
        # 3. p: Distribución inicial (separado por comas)
        p_raw = lines[2].split(',')
        p = [int(x) for x in p_raw]
        
        # 4. v: Valores de las opiniones (separado por comas)
        v_raw = lines[3].split(',')
        v = [float(x) for x in v_raw]
        
        # Validaciones básicas de longitud
        if len(p) != m or len(v) != m:
            raise ValueError(f"Error: Se esperaban {m} elementos en 'p' y 'v', pero se encontraron {len(p)} y {len(v)}.")

        # 5. s: Matriz de resistencia (m líneas siguientes)
        # Formato esperado en minizinc 2D: [| 1,2,3 | 4,5,6 | ... |]
        s_rows = []
        current_line_idx = 4
        
        for _ in range(m):
            row_raw = lines[current_line_idx].split(',')
            row = [int(x) for x in row_raw]
            if len(row) != 3:
                raise ValueError(f"Error en matriz 's': La línea {current_line_idx + 1} debe tener 3 valores.")
            s_rows.append(row)
            current_line_idx += 1
            
        # 6. ct: Costo total máximo
        ct = float(lines[current_line_idx])
        
        # 7. maxMovs: Cantidad máxima de movimientos
        maxMovs = float(lines[current_line_idx + 1])

        # ---------------------------------------------------------
        # CÁLCULO DE LA MEDIANA (Necesaria para el modelo)
        # ---------------------------------------------------------
        mediana = calcular_mediana_ponderada(v, p)

        # ---------------------------------------------------------
        # GENERACIÓN DEL ARCHIVO .DZN
        # ---------------------------------------------------------
        with open(output_path, 'w') as out:
            out.write(f"% Generado automaticamente desde {input_path}\n\n")
            out.write(f"n = {n};\n")
            out.write(f"m = {m};\n")
            out.write(f"ct = {ct};\n")
            out.write(f"maxMovs = {maxMovs};\n")
            out.write(f"mediana = {mediana};\n\n")
            
            # Escribir array v
            out.write("v = " + str(v) + ";\n")
            
            # Escribir array p
            out.write("p = " + str(p) + ";\n")
            
            # Escribir array 2D s con formato pipe [| ... | ... |]
            out.write("s = [|")
            for i, row in enumerate(s_rows):
                out.write(f" {row[0]}, {row[1]}, {row[2]} ")
                if i < m - 1:
                    out.write("|") # Separador de fila
            out.write("|];\n")

        print(f"¡Éxito! Archivo convertido guardado en: {output_path}")
        print(f"Mediana calculada: {mediana}")

    except Exception as e:
        print(f"Error procesando el archivo: {e}")

# Ejemplo de uso directo
if __name__ == "__main__":
    # Puedes cambiar estos nombres de archivo
    archivo_entrada = "entrada.txt"
    archivo_salida = "DatosProyecto.dzn"
    
    convertir_txt_a_dzn(archivo_entrada, archivo_salida)