import flet as ft

def main(page: ft.Page):
    page.title = "Omni-Automata & Compiler Lab"
    page.theme_mode = "dark"  # Usamos string en lugar de ft.ThemeMode
    page.padding = 20

    # --- Lógica del Motor AFND ---
    tabla_transiciones = {}
    estados_activos = set(["q0"])

    # --- Elementos de UI ---
    txt_origen = ft.TextField(label="Estado Origen", width=120)
    txt_simbolo = ft.TextField(label="Símbolo", width=100)
    txt_destino = ft.TextField(label="Estado Destino", width=120)
    
    lista_transiciones = ft.ListView(height=150, spacing=5)
    row_estados_activos = ft.Row(wrap=True)

    def actualizar_vista_estados():
        row_estados_activos.controls.clear()
        for estado in estados_activos:
            row_estados_activos.controls.append(
                ft.Chip(
                    label=ft.Text(estado, weight="bold"),
                    bgcolor="blue700"  # Usamos string en lugar de ft.Colors
                )
            )
        page.update()

    def agregar_transicion(e):
        origen = txt_origen.value.strip()
        simbolo = txt_simbolo.value.strip()
        destino = txt_destino.value.strip()

        if not (origen and simbolo and destino):
            return

        clave = (origen, simbolo)
        if clave not in tabla_transiciones:
            tabla_transiciones[clave] = []
        
        if destino not in tabla_transiciones[clave]:
            tabla_transiciones[clave].append(destino)
            lista_transiciones.controls.append(
                ft.Text(f"δ({origen}, {simbolo}) -> {destino}")
            )
        
        txt_destino.value = ""
        txt_destino.focus()
        page.update()

    def simular_paso(e):
        simbolo_entrada = txt_entrada_simulacion.value.strip()
        if not simbolo_entrada:
            return

        nuevos_activos = set()
        
        for estado in estados_activos:
            clave = (estado, simbolo_entrada)
            if clave in tabla_transiciones:
                nuevos_activos.update(tabla_transiciones[clave])

        estados_activos.clear()
        estados_activos.update(nuevos_activos)
        
        txt_entrada_simulacion.value = ""
        actualizar_vista_estados()

    # --- Controles de Simulación ---
    btn_agregar = ft.ElevatedButton("Agregar Transición", on_click=agregar_transicion)
    
    txt_entrada_simulacion = ft.TextField(label="Símbolo a evaluar", width=150)
    btn_paso = ft.FilledButton("Paso de Simulación", on_click=simular_paso, icon="play_arrow")

    # --- Layout Principal ---
    page.add(
        # Usamos size y weight en lugar de ft.TextThemeStyle para evitar errores
        ft.Text("Definición de AFND", size=24, weight="bold"),
        ft.Row([txt_origen, txt_simbolo, txt_destino, btn_agregar]),
        ft.Container(
            content=lista_transiciones,
            border=ft.border.all(1, "white54"),  # Usamos string para el color del borde
            border_radius=5,
            padding=10
        ),
        ft.Divider(height=30, thickness=2),
        ft.Text("Simulación en Tiempo Real", size=24, weight="bold"),
        ft.Text("Conjunto de Estados Activos:"),
        row_estados_activos,
        ft.Row([txt_entrada_simulacion, btn_paso])
    )

    actualizar_vista_estados()

ft.app(target=main)