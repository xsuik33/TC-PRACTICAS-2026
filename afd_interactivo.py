"""
Autómata Finito Determinista (AFD) - VERSIÓN INTERACTIVA
Ingresa tu propio AFD paso a paso
"""

class AFD:
    """
    Clase para representar un Autómata Finito Determinista
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
        
        Returns:
            tuple: (es_aceptada, camino_estados, es_valida)
        """
        if not cadena:
            es_aceptada = self.estado_inicial in self.estados_aceptacion
            return es_aceptada, [self.estado_inicial], True
        
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
        print("\n" + "=" * 60)
        print("INFORMACIÓN DEL AFD")
        print("=" * 60)
        print(f"Estados: {self.estados}")
        print(f"Alfabeto: {self.alfabeto}")
        print(f"Estado inicial: {self.estado_inicial}")
        print(f"Estados de aceptación: {self.estados_aceptacion}")
        print("\nTabla de Transiciones:")
        print("-" * 60)
        
        # Ordenar para mostrar más claramente
        transiciones_ordenadas = sorted(self.transiciones.items())
        for (estado, simbolo), siguiente in transiciones_ordenadas:
            print(f"  δ({estado}, '{simbolo}') = {siguiente}")
        print("=" * 60 + "\n")


def crear_afd_manual():
    """
    Crea un AFD ingresando los datos manualmente
    """
    print("\n" + "=" * 60)
    print("CREAR UN AUTÓMATA FINITO DETERMINISTA (AFD)")
    print("=" * 60 + "\n")
    
    # 1. ALFABETO
    print("1️⃣  INGRESA EL ABECEDARIO (ALFABETO)")
    print("   Ejemplo: 0,1  o  a,b,c  o  0,1,2")
    alfabeto_input = input("   Abecedario (separados por comas): ").strip()
    alfabeto = set(simbolo.strip() for simbolo in alfabeto_input.split(','))
    print(f"   ✓ Alfabeto: {alfabeto}\n")
    
    # 2. ESTADOS
    print("2️⃣  INGRESA LOS ESTADOS")
    print("   Ejemplo: q0,q1,q2  o  S0,S1,S2")
    estados_input = input("   Estados (separados por comas): ").strip()
    estados = set(estado.strip() for estado in estados_input.split(','))
    print(f"   ✓ Estados: {estados}\n")
    
    # 3. ESTADO INICIAL
    print("3️⃣  INGRESA EL ESTADO INICIAL")
    while True:
        estado_inicial = input("   Estado inicial: ").strip()
        if estado_inicial in estados:
            print(f"   ✓ Estado inicial: {estado_inicial}\n")
            break
        else:
            print(f"   ❌ Error: {estado_inicial} no está en los estados. Intenta de nuevo.\n")
    
    # 4. ESTADOS DE ACEPTACIÓN
    print("4️⃣  INGRESA LOS ESTADOS DE ACEPTACIÓN")
    print("   Ejemplo: q2  o  q1,q3,q5")
    while True:
        aceptacion_input = input("   Estados de aceptación (separados por comas): ").strip()
        estados_aceptacion = set(estado.strip() for estado in aceptacion_input.split(','))
        
        if estados_aceptacion.issubset(estados):
            print(f"   ✓ Estados de aceptación: {estados_aceptacion}\n")
            break
        else:
            invalidos = estados_aceptacion - estados
            print(f"   ❌ Error: {invalidos} no están en los estados. Intenta de nuevo.\n")
    
    # 5. TRANSICIONES
    print("5️⃣  INGRESA LAS TRANSICIONES")
    print("   Formato: estado,símbolo,siguiente_estado")
    print("   Ejemplo: q0,0,q1  (significa δ(q0, '0') = q1)")
    print("   Escribe 'listo' cuando termines.\n")
    
    transiciones = {}
    while True:
        transicion_input = input("   Transición (o 'listo'): ").strip().lower()
        
        if transicion_input == 'listo':
            break
        
        try:
            partes = [p.strip() for p in transicion_input.split(',')]
            if len(partes) != 3:
                print("   ❌ Formato incorrecto. Usa: estado,símbolo,siguiente_estado\n")
                continue
            
            estado_actual, simbolo, siguiente_estado = partes
            
            # Validaciones
            if estado_actual not in estados:
                print(f"   ❌ '{estado_actual}' no está en los estados.\n")
                continue
            if simbolo not in alfabeto:
                print(f"   ❌ '{simbolo}' no está en el alfabeto.\n")
                continue
            if siguiente_estado not in estados:
                print(f"   ❌ '{siguiente_estado}' no está en los estados.\n")
                continue
            
            transiciones[(estado_actual, simbolo)] = siguiente_estado
            print(f"   ✓ δ({estado_actual}, '{simbolo}') = {siguiente_estado}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    print()
    return AFD(estados, alfabeto, transiciones, estado_inicial, estados_aceptacion)


def probar_cadenas(afd):
    """
    Prueba cadenas en el AFD creado
    """
    print("\n" + "=" * 60)
    print("PRUEBA DE CADENAS")
    print("=" * 60)
    print("Escribe las cadenas que deseas probar (o 'salir' para terminar)\n")
    
    while True:
        cadena = input("Ingresa cadena (vacío para cadena vacía): ").strip()
        
        if cadena.lower() == 'salir':
            break
        
        if cadena == '':
            cadena = ''  # cadena vacía
        
        aceptada, camino, valida = afd.procesar_cadena(cadena)
        
        if not valida and not aceptada:
            print(f"❌ RECHAZADA - Símbolo no en alfabeto")
            print(f"   Camino parcial: {' → '.join(camino)}")
        elif aceptada:
            print(f"✓ ACEPTADA")
            print(f"   Camino: {' → '.join(camino)}")
        else:
            print(f"✗ RECHAZADA")
            print(f"   Camino: {' → '.join(camino)}")
        print()


def menu_principal():
    """
    Menú principal
    """
    while True:
        print("\n" + "🤖 " * 15)
        print("AUTÓMATA FINITO DETERMINISTA - MENÚ PRINCIPAL")
        print("🤖 " * 15)
        print("\n1. Crear nuevo AFD")
        print("2. Cargar ejemplo predefinido")
        print("3. Salir")
        
        opcion = input("\nElige una opción (1-3): ").strip()
        
        if opcion == '1':
            afd = crear_afd_manual()
            afd.mostrar_info()
            probar_cadenas(afd)
        
        elif opcion == '2':
            print("\nEJEMPLOS DISPONIBLES:")
            print("1. Cadenas que terminan con '01' (binario)")
            print("2. Números binarios pares")
            print("3. Sin dos 1s consecutivos")
            print("4. Números binarios divisibles por 3")
            
            ejemplo = input("\nElige ejemplo (1-4): ").strip()
            
            if ejemplo == '1':
                afd = AFD(
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
            elif ejemplo == '2':
                afd = AFD(
                    estados={'q0', 'q1'},
                    alfabeto={'0', '1'},
                    transiciones={
                        ('q0', '0'): 'q0',
                        ('q0', '1'): 'q1',
                        ('q1', '0'): 'q0',
                        ('q1', '1'): 'q1',
                    },
                    estado_inicial='q0',
                    estados_aceptacion={'q0'}
                )
            elif ejemplo == '3':
                afd = AFD(
                    estados={'q0', 'q1', 'q2'},
                    alfabeto={'0', '1'},
                    transiciones={
                        ('q0', '0'): 'q0',
                        ('q0', '1'): 'q1',
                        ('q1', '0'): 'q0',
                        ('q1', '1'): 'q2',
                        ('q2', '0'): 'q2',
                        ('q2', '1'): 'q2',
                    },
                    estado_inicial='q0',
                    estados_aceptacion={'q0', 'q1'}
                )
            elif ejemplo == '4':
                afd = AFD(
                    estados={'q0', 'q1', 'q2'},
                    alfabeto={'0', '1'},
                    transiciones={
                        ('q0', '0'): 'q0',
                        ('q0', '1'): 'q1',
                        ('q1', '0'): 'q2',
                        ('q1', '1'): 'q0',
                        ('q2', '0'): 'q1',
                        ('q2', '1'): 'q2',
                    },
                    estado_inicial='q0',
                    estados_aceptacion={'q0'}
                )
            else:
                print("❌ Opción no válida")
                continue
            
            afd.mostrar_info()
            probar_cadenas(afd)
        
        elif opcion == '3':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")


if __name__ == "__main__":
    menu_principal()
