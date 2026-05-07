"""
Autómata Finito Determinista (AFD)
Implementación y ejemplos prácticos
"""

class AFD:
    """
    Clase para representar un Autómata Finito Determinista
    
    Atributos:
        estados: conjunto de estados
        alfabeto: conjunto de símbolos de entrada
        transiciones: diccionario {(estado, símbolo): nuevo_estado}
        estado_inicial: estado de inicio
        estados_aceptacion: conjunto de estados finales
    """
    
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_aceptacion):
        """Inicializa un AFD"""
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_aceptacion = estados_aceptacion
    
    def procesar_cadena(self, cadena):
        """
        Procesa una cadena y retorna si es aceptada
        
        Args:
            cadena: string a validar
            
        Returns:
            tuple: (es_aceptada, camino_estados, es_valida)
        """
        estado_actual = self.estado_inicial
        camino = [estado_actual]
        
        for simbolo in cadena:
            # Validar que el símbolo está en el alfabeto
            if simbolo not in self.alfabeto:
                return False, camino, False
            
            # Obtener siguiente estado
            clave = (estado_actual, simbolo)
            if clave not in self.transiciones:
                return False, camino, True
            
            estado_actual = self.transiciones[clave]
            camino.append(estado_actual)
        
        # Verificar si terminó en estado de aceptación
        es_aceptada = estado_actual in self.estados_aceptacion
        return es_aceptada, camino, True
    
    def mostrar_info(self):
        """Muestra información del AFD"""
        print("=" * 50)
        print("INFORMACIÓN DEL AFD")
        print("=" * 50)
        print(f"Estados: {self.estados}")
        print(f"Alfabeto: {self.alfabeto}")
        print(f"Estado inicial: {self.estado_inicial}")
        print(f"Estados de aceptación: {self.estados_aceptacion}")
        print("\nTransiciones:")
        for (estado, simbolo), siguiente in sorted(self.transiciones.items()):
            print(f"  δ({estado}, '{simbolo}') = {siguiente}")
        print("=" * 50)


# ============================================================
# EJEMPLO 1: AFD que acepta cadenas que terminan con "01"
# ============================================================
print("\n### EJEMPLO 1: Cadenas que terminan con '01' ###\n")

afd1 = AFD(
    estados={'q0', 'q1', 'q2'},
    alfabeto={'0', '1'},
    transiciones={
        ('q0', '0'): 'q1',
        ('q0', '1'): 'q0',
        ('q1', '0'): 'q1',
        ('q1', '1'): 'q2',
        ('q2', '0'): 'q1',
        ('q2', '1'): 'q0',
    },
    estado_inicial='q0',
    estados_aceptacion={'q2'}
)

afd1.mostrar_info()

cadenas_prueba1 = ['01', '101', '001', '1101', '11', '0', '010']
for cadena in cadenas_prueba1:
    aceptada, camino, valida = afd1.procesar_cadena(cadena)
    estado = "✓ ACEPTADA" if aceptada else "✗ RECHAZADA"
    print(f"'{cadena}': {estado} - Camino: {' → '.join(camino)}")


# ============================================================
# EJEMPLO 2: AFD que acepta números binarios pares
# ============================================================
print("\n### EJEMPLO 2: Números binarios pares (terminan en 0) ###\n")

afd2 = AFD(
    estados={'q0', 'q1'},
    alfabeto={'0', '1'},
    transiciones={
        ('q0', '0'): 'q0',  # número par
        ('q0', '1'): 'q1',  # número impar
        ('q1', '0'): 'q0',  # vuelve a par
        ('q1', '1'): 'q1',  # sigue siendo impar
    },
    estado_inicial='q0',
    estados_aceptacion={'q0'}
)

afd2.mostrar_info()

cadenas_prueba2 = ['0', '10', '110', '1010', '11', '101', '1001']
for cadena in cadenas_prueba2:
    aceptada, camino, valida = afd2.procesar_cadena(cadena)
    estado = "✓ ACEPTADA (PAR)" if aceptada else "✗ RECHAZADA (IMPAR)"
    print(f"'{cadena}': {estado} - Camino: {' → '.join(camino)}")


# ============================================================
# EJEMPLO 3: AFD que acepta cadenas sin dos 1s consecutivos
# ============================================================
print("\n### EJEMPLO 3: Sin dos 1s consecutivos ###\n")

afd3 = AFD(
    estados={'q0', 'q1', 'q2'},
    alfabeto={'0', '1'},
    transiciones={
        ('q0', '0'): 'q0',
        ('q0', '1'): 'q1',
        ('q1', '0'): 'q0',
        ('q1', '1'): 'q2',  # estado de rechazo
        ('q2', '0'): 'q2',
        ('q2', '1'): 'q2',
    },
    estado_inicial='q0',
    estados_aceptacion={'q0', 'q1'}
)

afd3.mostrar_info()

cadenas_prueba3 = ['0', '1', '10', '101', '1010', '11', '110', '0110']
for cadena in cadenas_prueba3:
    aceptada, camino, valida = afd3.procesar_cadena(cadena)
    estado = "✓ ACEPTADA" if aceptada else "✗ RECHAZADA"
    print(f"'{cadena}': {estado} - Camino: {' → '.join(camino)}")


# ============================================================
# EJEMPLO 4: AFD que acepta cadenas divisibles por 3
# ============================================================
print("\n### EJEMPLO 4: Números en binario divisibles por 3 ###\n")

afd4 = AFD(
    estados={'q0', 'q1', 'q2'},
    alfabeto={'0', '1'},
    transiciones={
        ('q0', '0'): 'q0',  # 0 % 3 = 0
        ('q0', '1'): 'q1',  # 1 % 3 = 1
        ('q1', '0'): 'q2',  # 2 % 3 = 2
        ('q1', '1'): 'q0',  # 3 % 3 = 0
        ('q2', '0'): 'q1',  # 4 % 3 = 1
        ('q2', '1'): 'q2',  # 5 % 3 = 2
    },
    estado_inicial='q0',
    estados_aceptacion={'q0'}
)

afd4.mostrar_info()

cadenas_prueba4 = ['0', '11', '110', '1001', '1100', '111', '1010']
for cadena in cadenas_prueba4:
    aceptada, camino, valida = afd4.procesar_cadena(cadena)
    valor_decimal = int(cadena, 2) if cadena else 0
    estado = "✓ ACEPTADA" if aceptada else "✗ RECHAZADA"
    print(f"'{cadena}' ({valor_decimal}): {estado} - Camino: {' → '.join(camino)}")
