import flet as ft

def main(page: ft.Page):
    page.title = "Practica 3 - Motor AFND | ESCOM IPN"
    page.theme_mode = "dark" 
    page.padding = 30

    # --- Lógica del Motor AFND ---
    tabla_transiciones = {}
    estados_activos = set(["q0"])

    # --- Elementos de UI ---
    txt_origen = ft.TextField(label="Estado Origen", width=120, hint_text="ej: q0")
    txt_simbolo = ft.TextField(label="Símbolo", width=100, hint_text="ej: 1")
    txt_destino = ft.TextField(label="Estado Destino", width=120, hint_text="ej: q1")
    
    lista_transiciones = ft.ListView(height=150, spacing=5)
    row_estados_activos = ft.Row(wrap=True)

    def actualizar_vista_estados():
        row_estados_activos.controls.clear()
        
        # Si el conjunto está vacío, el autómata murió en esa rama
        if not estados_activos:
            row_estados_activos.controls.append(
                ft.Chip(label=ft.Text("∅ (Muerto)", weight="bold"), bgcolor="red900")
            )
        else:
            # Ordenamos para que no estén brincando visualmente
            for estado in sorted(estados_activos):
                row_estados_activos.controls.append(
                    ft.Chip(
                        label=ft.Text(estado, weight="bold"),
                        bgcolor="blue700"
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
                ft.Text(f"δ({origen}, {simbolo}) ➔ {destino}", font_family="monospace")
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

    def reiniciar_simulacion(e):
        estados_activos.clear()
        estados_activos.add("q0")
        txt_entrada_simulacion.value = ""
        actualizar_vista_estados()
        
    def limpiar_todo(e):
        tabla_transiciones.clear()
        lista_transiciones.controls.clear()
        reiniciar_simulacion(e)

    # --- Controles de Simulación ---
    btn_agregar = ft.ElevatedButton("Agregar Transición", on_click=agregar_transicion, bgcolor="blue700", color="white")
    
    txt_entrada_simulacion = ft.TextField(label="Símbolo a evaluar", width=150)
    btn_paso = ft.FilledButton("Paso de Simulación", on_click=simular_paso, icon="play_arrow")
    btn_reiniciar = ft.ElevatedButton("Reiniciar", on_click=reiniciar_simulacion, icon="refresh")
    btn_limpiar = ft.OutlinedButton("Limpiar Todo", on_click=limpiar_todo, icon="delete", icon_color="red")

    # --- Layout Principal ---
    page.add(
        ft.Text("Motor de Autómata Finito No Determinista (AFND)", size=26, weight="bold", color="blue400"),
        
        ft.Text("1. Definición de Transiciones", size=20, weight="bold"),
        ft.Row([txt_origen, txt_simbolo, txt_destino, btn_agregar]),
        ft.Container(
            content=lista_transiciones,
            border=ft.border.all(1, "white54"),
            border_radius=5,
            padding=10
        ),
        ft.Row([btn_limpiar], alignment=ft.MainAxisAlignment.END),
        
        ft.Divider(height=30, thickness=2, color="white24"),
        
        ft.Text("2. Simulación en Tiempo Real", size=20, weight="bold"),
        ft.Text("Conjunto de Estados Activos:"),
        row_estados_activos,
        ft.Row([txt_entrada_simulacion, btn_paso, btn_reiniciar])
    )

    actualizar_vista_estados()

ft.app(target=main)