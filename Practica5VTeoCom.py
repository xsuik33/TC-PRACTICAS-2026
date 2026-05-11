"""
Instituto Politécnico Nacional - Escuela Superior de Cómputo
Unidad de Aprendizaje: Teoría de la Computación
Práctica 5: Extensión de Software Interactivo para Visualizar Autómatas

Alumno:
- Iker Saul Gonzalez Ortiz
"""

import flet as ft
import xml.etree.ElementTree as ET
import os
import urllib.parse
import urllib.request
import base64
import asyncio 

def border_all(width: float, color: str):
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)

async def main(page: ft.Page):
    page.title = "Visualizador DFA - Iker Saul"
    page.theme_mode = "light"
    page.padding = 20
    page.window_width = 850
    page.window_height = 700

    automata_data = {}

    # --- SERVICIOS: FilePicker (Versión 0.85.0) ---
    save_file_dialog = ft.FilePicker()
    # En 0.85.0, FilePicker se agrega a servicios para evitar el error "Unknown control"
    page.services.append(save_file_dialog)

    # Lógica para procesar el resultado del guardado
    async def al_seleccionar_ruta(e: ft.FilePickerResultEvent):
        if e.path and 'image_bytes' in automata_data:
            try:
                with open(e.path, "wb") as f:
                    f.write(automata_data['image_bytes'])
                lbl_status_diagram.value = f"✅ Guardado en: {e.path}"
                lbl_status_diagram.color = "green"
            except Exception as ex:
                lbl_status_diagram.value = f"❌ Error al guardar: {ex}"
                lbl_status_diagram.color = "red"
            page.update()

    save_file_dialog.on_result = al_seleccionar_ruta

    async def ejecutar_guardado(e):
        # Disparamos la ventana de guardado
        await save_file_dialog.save_file(
            allowed_extensions=["png"], 
            file_name="Mi_Automata_ESCOM.png"
        )

    # --- CONTROLES UI ---
    txt_path = ft.TextField(label="Ruta de tu archivo JFLAP (.jff)", expand=True)
    txt_states = ft.TextField(label="Estados (Ej: q0,q1)", expand=True)
    txt_alphabet = ft.TextField(label="Alfabeto (Ej: a,b)", expand=True)
    txt_initial = ft.TextField(label="Estado Inicial", expand=True)
    txt_finals = ft.TextField(label="Estados Finales", expand=True)
    txt_transitions = ft.TextField(
        label="Transiciones (origen,símbolo,destino)", 
        multiline=True, 
        min_lines=5, 
        expand=True
    )
    lbl_status_config = ft.Text(value="", italic=True)
    lbl_status_diagram = ft.Text(value="", italic=True)
    
    txt_string = ft.TextField(label="Ingresa la cadena a evaluar", expand=True)
    lbl_sim_result = ft.Text(value="Esperando cadena...", size=24, weight="bold")
    
    chk_paso_a_paso = ft.Checkbox(label="Simulación lenta (1 seg/paso)", value=False)

    diagram_container = ft.Container(
        content=ft.Text(value="Aún no hay grafo generado...", color="grey"), 
        expand=True, 
        border=border_all(1, "grey"), 
        border_radius=10,
        padding=10,
        alignment=ft.Alignment(0, 0)
    )
    
    # --- FUNCIONES LÓGICAS ---
    async def cargar_jff(e):
        ruta = txt_path.value.strip().replace('"', '').replace("'", "")
        if not os.path.exists(ruta):
            lbl_status_config.value = "Ruta inválida."
            lbl_status_config.color = "red"
            page.update()
            return
        try:
            tree = ET.parse(ruta)
            root = tree.getroot()
            automaton = root.find('automaton')
            
            states_map, initial_state, final_states = {}, "", []
            for state in automaton.findall('state'):
                s_id, s_name = state.get('id'), state.get('name')
                states_map[s_id] = s_name
                if state.find('initial') is not None: initial_state = s_name
                if state.find('final') is not None: final_states.append(s_name)
            
            transitions_list, alphabet = [], set()
            for trans in automaton.findall('transition'):
                read_sym = trans.find('read').text or ""
                if read_sym:
                    alphabet.add(read_sym)
                    transitions_list.append(f"{states_map[trans.find('from').text]},{read_sym},{states_map[trans.find('to').text]}")

            txt_states.value = ",".join(states_map.values())
            txt_alphabet.value = ",".join(sorted(list(alphabet)))
            txt_initial.value = initial_state
            txt_finals.value = ",".join(final_states)
            txt_transitions.value = "\n".join(transitions_list)
            
            lbl_status_config.value = "¡Importación exitosa!"
            lbl_status_config.color = "green"
            page.update()
        except Exception as ex:
            lbl_status_config.value = f"Error: {ex}"
            lbl_status_config.color = "red"
            page.update()

    async def compilar_y_graficar(e):
        try:
            states = set(x.strip() for x in txt_states.value.split(',') if x.strip())
            initial = txt_initial.value.strip()
            finals = set(x.strip() for x in txt_finals.value.split(',') if x.strip())
            
            transitions = {q: {} for q in states}
            for line in txt_transitions.value.split('\n'):
                if line.strip():
                    o, s, d = [x.strip() for x in line.split(',')]
                    transitions[o][s] = d

            automata_data.update({'initial': initial, 'finals': finals, 'transitions': transitions})
            
            # Construcción manual de DOT para la API
            dot_code = 'digraph G { rankdir=LR; bgcolor="transparent"; '
            dot_code += 'node [style="filled", fillcolor="#e3f2fd", shape=circle]; '
            dot_code += f'start [shape=point]; start -> "{initial}"; '
            
            for q in states:
                if q in finals: dot_code += f'"{q}" [shape=doublecircle]; '
                    
            for origen, dict_dest in transitions.items():
                for simbolo, destino in dict_dest.items():
                    dot_code += f'"{origen}" -> "{destino}" [label="{simbolo}", color="#1565c0"]; '
            dot_code += '}'
            
            url = f"https://quickchart.io/graphviz?graph={urllib.parse.quote(dot_code)}"
            
            # Descarga y conversión a Base64 para evitar problemas de caché
            respuesta = urllib.request.urlopen(url)
            img_data = respuesta.read()
            automata_data['image_bytes'] = img_data 
            
            img_b64 = base64.b64encode(img_data).decode("utf-8")
            diagram_container.content = ft.Image(src=f"data:image/png;base64,{img_b64}", fit="contain", expand=True)
            
            lbl_status_diagram.value = "Grafo listo."
            lbl_status_diagram.color = "green"
            btn_guardar_grafo.disabled = False
            
            await switch_tab(1)
            
        except Exception as ex:
            lbl_status_diagram.value = f"Error: {ex}"
            lbl_status_diagram.color = "red"
            await switch_tab(1)

    async def probar_cadena(e):
        if not automata_data:
            lbl_sim_result.value = "⚠️ Genera el autómata primero."
            lbl_sim_result.color = "orange"
            page.update()
            return
            
        estado_actual = automata_data['initial']
        cadena = txt_string.value.strip()
        lbl_sim_result.color = "black"
        
        try:
            for i, simbolo in enumerate(cadena):
                siguiente = automata_data['transitions'][estado_actual][simbolo]
                if chk_paso_a_paso.value:
                    lbl_sim_result.value = f" Pasos: {i+1}/{len(cadena)} | {estado_actual} --({simbolo})--> {siguiente}"
                    page.update()
                    await asyncio.sleep(1.5)  # Pausa de 3 segundos para simular paso a paso 
                estado_actual = siguiente
            
            if estado_actual in automata_data['finals']:
                lbl_sim_result.value = f"✅ ACEPTADA (Fin en {estado_actual})"
                lbl_sim_result.color = "green"
            else:
                lbl_sim_result.value = f"❌ RECHAZADA (Fin en {estado_actual})"
                lbl_sim_result.color = "red"
        except KeyError:
            lbl_sim_result.value = f"🚫 ERROR: Sin transición para '{simbolo}' en '{estado_actual}'"
            lbl_sim_result.color = "red"
        page.update()

    # --- COMPONENTES DE VISTA ---
    view_config = ft.Container(
        padding=20,
        content=ft.Column([
            ft.Row([txt_path, ft.Button(content=ft.Text("📂 Importar JFLAP"), on_click=cargar_jff)]),
            lbl_status_config,
            ft.Divider(),
            ft.Row([txt_states, txt_alphabet]),
            ft.Row([txt_initial, txt_finals]),
            txt_transitions,
            ft.Button(content=ft.Text("⚙️ Crear Grafo"), on_click=compilar_y_graficar)
        ], scroll="adaptive")
    )

    btn_guardar_grafo = ft.Button(content=ft.Text("💾 Guardar Imagen"), on_click=ejecutar_guardado, disabled=True)

    view_visual = ft.Container(
        padding=20,
        content=ft.Column([
            ft.Row([lbl_status_diagram, btn_guardar_grafo], alignment="spaceBetween"),
            diagram_container
        ])
    )

    view_simulacion = ft.Container(
        padding=30,
        content=ft.Column([
            ft.Text("Simulador de Cadenas", size=20, weight="bold"),
            ft.Row([txt_string, chk_paso_a_paso]),
            ft.Button(content=ft.Text("▶️ Iniciar Evaluación"), on_click=probar_cadena, bgcolor="blue", color="white"),
            ft.Divider(),
            lbl_sim_result
        ])
    )

    content_area = ft.Container(content=view_config, expand=True)

    async def switch_tab(idx):
        vistas = [view_config, view_visual, view_simulacion]
        content_area.content = vistas[idx]
        for i, btn in enumerate(nav_buttons):
            btn.bgcolor = "blue" if i == idx else "white"
            btn.color = "white" if i == idx else "black"
        page.update()

    # --- CORRECCIÓN APLICADA AQUÍ ABAJO ---
    # Envolvemos las llamadas a switch_tab en funciones asíncronas
    async def ir_datos(e):
        await switch_tab(0)

    async def ir_grafo(e):
        await switch_tab(1)

    async def ir_prueba(e):
        await switch_tab(2)

    # Navegación actualizada
    btn_config = ft.Button(content=ft.Text("1. Datos"), on_click=ir_datos)
    btn_visual = ft.Button(content=ft.Text("2. Grafo"), on_click=ir_grafo)
    btn_sim = ft.Button(content=ft.Text("3. Prueba"), on_click=ir_prueba)

    nav_buttons = [btn_config, btn_visual, btn_sim]
    page.add(
        ft.Row([ft.Text("Software Visual de Autómatas - IPN ESCOM", size=24, weight="bold", color="blue")]),
        ft.Row(nav_buttons, alignment="center"),
        ft.Divider(),
        content_area
    )
    await switch_tab(0)

if __name__ == "__main__":
    ft.run(main)