import flet as ft
from visual_automata.fa.dfa import VisualDFA
import xml.etree.ElementTree as ET
import os

def main(page: ft.Page):
    page.title = "Simulador de Autómatas - Práctica 5"
    page.scroll = "adaptive"
    page.theme_mode = "dark" 
    page.padding = 30

    txt_states = ft.TextField(label="Estados (Ej: q0,q1,q2)", expand=True)
    txt_alphabet = ft.TextField(label="Alfabeto (Ej: 0,1)", expand=True)
    txt_initial = ft.TextField(label="Estado Inicial (Ej: q0)", expand=True)
    txt_finals = ft.TextField(label="Estados Finales (Ej: q1,q2)", expand=True)
    txt_transitions = ft.TextField(label="Transiciones (origen,símbolo,destino)", multiline=True, min_lines=4, expand=True)
    
    txt_path = ft.TextField(
        label="Ruta absoluta del archivo .jff", 
        hint_text="C:\\Users\\usuario\\Documents\\automata.jff",
        expand=True
    )

    img_container = ft.Container(padding=20)
    txt_result = ft.Text(size=18, weight="bold")
    automata_data = {}

    def cargar_desde_ruta(e):
        path = txt_path.value.strip().replace('"', '')
        if not os.path.exists(path):
            txt_result.value = "Error: El archivo no existe."
            txt_result.color = "red"
            page.update()
            return
            
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            automaton = root.find('automaton')
            
            states_map = {}
            initial_state = ""
            final_states = []
            for state in automaton.findall('state'):
                s_id, s_name = state.get('id'), state.get('name')
                states_map[s_id] = s_name
                if state.find('initial') is not None: initial_state = s_name
                if state.find('final') is not None: final_states.append(s_name)
            
            transitions_list, alphabet = [], set()
            for trans in automaton.findall('transition'):
                read_node = trans.find('read')
                read_sym = read_node.text if read_node is not None and read_node.text else ""
                if read_sym:
                    alphabet.add(read_sym)
                    transitions_list.append(f"{states_map[trans.find('from').text]},{read_sym},{states_map[trans.find('to').text]}")

            txt_states.value = ",".join(states_map.values())
            txt_alphabet.value = ",".join(sorted(list(alphabet)))
            txt_initial.value = initial_state
            txt_finals.value = ",".join(final_states)
            txt_transitions.value = "\n".join(transitions_list)
            
            txt_result.value = "Archivo cargado correctamente."
            txt_result.color = "green"
            page.update()
        except Exception as ex:
            txt_result.value = f"Error: {ex}"
            txt_result.color = "red"
            page.update()

    def generar_automata(e):
        try:
            states = set(x.strip() for x in txt_states.value.split(',') if x.strip())
            alphabet = set(x.strip() for x in txt_alphabet.value.split(',') if x.strip())
            initial = txt_initial.value.strip()
            finals = set(x.strip() for x in txt_finals.value.split(',') if x.strip())
            
            transitions = {q: {} for q in states}
            for line in txt_transitions.value.split('\n'):
                if line.strip():
                    o, s, d = [x.strip() for x in line.split(',')]
                    transitions[o][s] = d

            automata_data.update({'initial': initial, 'finals': finals, 'transitions': transitions})
            
            dfa = VisualDFA(states=states, input_symbols=alphabet, transitions=transitions, initial_state=initial, final_states=finals)
            
            # SOLUCIÓN: Se eliminan los argumentos 'format' y 'view' que causan conflicto
            dfa.show_diagram(filename="diagrama_dfa_dinamico")
            
            # Intentar cargar la imagen generada (por defecto visual-automata suele añadir la extensión)
            img_path = "diagrama_dfa_dinamico.png"
            if not os.path.exists(img_path):
                img_path = "diagrama_dfa_dinamico"

            img_container.content = ft.Image(src=img_path, fit="contain", width=600)
            txt_result.value = "Grafo generado exitosamente."
            txt_result.color = "green"
            page.update()
        except Exception as ex:
            txt_result.value = f"Error: {ex}"
            txt_result.color = "red"
            page.update()

    txt_string = ft.TextField(label="Cadena a simular", expand=True)

    def simular_cadena(e):
        if not automata_data:
            txt_result.value = "Genera el autómata primero."
            txt_result.color = "red"
            page.update()
            return
            
        curr = automata_data['initial']
        cadena = txt_string.value.strip()
        try:
            for s in cadena:
                curr = automata_data['transitions'][curr][s]
            res = curr in automata_data['finals']
            txt_result.value = f"Resultado: {'ACEPTADA' if res else 'RECHAZADA'}"
            txt_result.color = "blue" if res else "orange"
        except:
            txt_result.value = "Cadena RECHAZADA (Camino no válido)"
            txt_result.color = "red"
        page.update()

    page.add(
        ft.Text("Constructor de Autómatas (DFA)", size=28, weight="bold", color="blue"),
        ft.Row([txt_path, ft.ElevatedButton("Cargar JFF", on_click=cargar_desde_ruta, bgcolor="amber", color="black")]),
        ft.Divider(),
        ft.Row([txt_states, txt_alphabet]),
        ft.Row([txt_initial, txt_finals]),
        txt_transitions,
        ft.Row([ft.ElevatedButton("Generar Grafo", on_click=generar_automata)], alignment="center"),
        ft.Divider(),
        ft.Row([txt_string, ft.ElevatedButton("Simular", on_click=simular_cadena, bgcolor="blue", color="white")]),
        txt_result, 
        img_container
    )

ft.app(target=main)