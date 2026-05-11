import flet as ft
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from itertools import product as iterproduct

# ─────────────────────────────────────────────
#  CORE AFD ENGINE
# ─────────────────────────────────────────────

class AFD:
    def __init__(self):
        self.states: list[str] = []
        self.alphabet: list[str] = []
        self.initial_state: str = ""
        self.accept_states: set[str] = set()
        self.transitions: dict[tuple[str, str], str] = {}  # (state, symbol) -> state
        self.name: str = "AFD sin nombre"

    def validate(self, string: str):
        """Returns (accepted: bool, trace: list[dict])"""
        if not self.initial_state:
            return False, []
        current = self.initial_state
        trace = [{"step": 0, "state": current, "remaining": string, "symbol": None}]
        for i, symbol in enumerate(string):
            if symbol not in self.alphabet:
                trace.append({"step": i+1, "state": "ERROR", "remaining": string[i+1:], "symbol": symbol, "error": f"Símbolo '{symbol}' no está en el alfabeto"})
                return False, trace
            key = (current, symbol)
            if key not in self.transitions:
                trace.append({"step": i+1, "state": "MUERTO", "remaining": string[i+1:], "symbol": symbol, "error": "Sin transición definida"})
                return False, trace
            current = self.transitions[key]
            trace.append({"step": i+1, "state": current, "remaining": string[i+1:], "symbol": symbol})
        accepted = current in self.accept_states
        return accepted, trace

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "states": self.states,
            "alphabet": self.alphabet,
            "initial_state": self.initial_state,
            "accept_states": list(self.accept_states),
            "transitions": {f"{k[0]},{k[1]}": v for k, v in self.transitions.items()}
        }

    def from_json(self, data: dict):
        self.name = data.get("name", "AFD")
        self.states = data["states"]
        self.alphabet = data["alphabet"]
        self.initial_state = data["initial_state"]
        self.accept_states = set(data["accept_states"])
        self.transitions = {}
        for k, v in data.get("transitions", {}).items():
            parts = k.split(",", 1)
            if len(parts) == 2:
                self.transitions[(parts[0], parts[1])] = v

    def to_xml(self) -> str:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<automaton type="dfa">',
                 f'  <name>{self.name}</name>',
                 f'  <alphabet>{",".join(self.alphabet)}</alphabet>',
                 f'  <initial_state>{self.initial_state}</initial_state>',
                 f'  <accept_states>{",".join(self.accept_states)}</accept_states>',
                 '  <states>']
        for s in self.states:
            lines.append(f'    <state name="{s}"/>')
        lines.append('  </states>')
        lines.append('  <transitions>')
        for (s, sym), t in self.transitions.items():
            lines.append(f'    <transition from="{s}" symbol="{sym}" to="{t}"/>')
        lines.append('  </transitions>')
        lines.append('</automaton>')
        return "\n".join(lines)

    def from_xml(self, xml_str: str):
        root = ET.fromstring(xml_str)
        self.name = root.findtext("name") or "AFD"
        alph = root.findtext("alphabet") or ""
        self.alphabet = [a for a in alph.split(",") if a]
        self.initial_state = root.findtext("initial_state") or ""
        acc = root.findtext("accept_states") or ""
        self.accept_states = set(a for a in acc.split(",") if a)
        self.states = [s.get("name") for s in root.findall(".//state") if s.get("name")]
        self.transitions = {}
        for t in root.findall(".//transition"):
            f, sym, to = t.get("from"), t.get("symbol"), t.get("to")
            if f and sym and to:
                self.transitions[(f, sym)] = to

    def to_jff(self) -> str:
        lines = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
                 '<structure>', '  <type>fa</type>', '  <automaton>']
        for i, s in enumerate(self.states):
            is_init = ' initial="true"' if s == self.initial_state else ''
            is_final = ' final="true"' if s in self.accept_states else ''
            lines.append(f'    <state id="{i}" name="{s}"{is_init}{is_final}>')
            lines.append(f'      <x>{100 + i*120}</x>')
            lines.append(f'      <y>100</y>')
            lines.append('    </state>')
        for (src, sym), dst in self.transitions.items():
            src_id = self.states.index(src) if src in self.states else 0
            dst_id = self.states.index(dst) if dst in self.states else 0
            lines.append(f'    <transition>')
            lines.append(f'      <from>{src_id}</from>')
            lines.append(f'      <to>{dst_id}</to>')
            lines.append(f'      <read>{sym}</read>')
            lines.append(f'    </transition>')
        lines.append('  </automaton>')
        lines.append('</structure>')
        return "\n".join(lines)

    def from_jff(self, jff_str: str):
        root = ET.fromstring(jff_str)
        id_to_name = {}
        self.states = []
        self.initial_state = ""
        self.accept_states = set()
        self.transitions = {}
        self.alphabet = []
        for state in root.findall(".//state"):
            sid = state.get("id")
            name = state.get("name") or f"q{sid}"
            id_to_name[sid] = name
            self.states.append(name)
            if state.find("initial") is not None or state.get("initial") == "true":
                self.initial_state = name
            if state.find("final") is not None or state.get("final") == "true":
                self.accept_states.add(name)
        symbols = set()
        for trans in root.findall(".//transition"):
            frm = id_to_name.get(trans.findtext("from") or "")
            to = id_to_name.get(trans.findtext("to") or "")
            sym = trans.findtext("read") or ""
            if frm and to and sym:
                self.transitions[(frm, sym)] = to
                symbols.add(sym)
        self.alphabet = sorted(symbols)
        self.name = "AFD desde JFF"


# ─────────────────────────────────────────────
#  STRING OPERATIONS
# ─────────────────────────────────────────────

def get_prefixes(s: str) -> list[str]:
    return [s[:i] for i in range(len(s)+1)]

def get_suffixes(s: str) -> list[str]:
    return [s[i:] for i in range(len(s)+1)]

def get_substrings(s: str) -> list[str]:
    result = set()
    for i in range(len(s)+1):
        for j in range(i, len(s)+1):
            result.add(s[i:j])
    return sorted(result)

def kleene_star(alphabet: list[str], max_len: int) -> list[str]:
    result = [""]
    for length in range(1, max_len+1):
        for combo in iterproduct(alphabet, repeat=length):
            result.append("".join(combo))
    return result

def kleene_plus(alphabet: list[str], max_len: int) -> list[str]:
    result = []
    for length in range(1, max_len+1):
        for combo in iterproduct(alphabet, repeat=length):
            result.append("".join(combo))
    return result


# ─────────────────────────────────────────────
#  UI THEME
# ─────────────────────────────────────────────

BG       = "#0D1117"
SURFACE  = "#161B22"
SURFACE2 = "#1C2333"
BORDER   = "#30363D"
ACCENT   = "#58A6FF"
ACCENT2  = "#3FB950"
DANGER   = "#F85149"
WARNING  = "#D29922"
TEXT     = "#E6EDF3"
TEXT2    = "#8B949E"
FONT     = "Courier New"

# --- NUEVA FUNCIÓN PARA REEMPLAZAR ft.border.all ---
def border_all(width: float, color: str):
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)

def chip(label: str, color: str = ACCENT) -> ft.Container:
    return ft.Container(
        content=ft.Text(label, size=11, color=color, font_family=FONT, weight=ft.FontWeight.BOLD),
        bgcolor=f"{color}22",
        # REPARADO:
        border=border_all(1, color),
        border_radius=4,
        # REPARADO:
        padding=ft.Padding(left=8, right=8, top=3, bottom=3),
    )


def section_title(text: str) -> ft.Text:
    return ft.Text(text, size=13, color=ACCENT, font_family=FONT,
                   weight=ft.FontWeight.BOLD)


def divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER)


# ─────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────

def main(page: ft.Page):
    page.title = "AFD Simulator — ESCOM IPN"
    page.bgcolor = BG
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {"Courier New": "Courier New"}
    page.padding = 0
    page.window_width = 1280
    page.window_height = 820
    page.window_min_width = 900

    afd = AFD()

    # ── Shared state refs ──
    status_bar_text = ft.Ref[ft.Text]()
    tab_container = ft.Ref[ft.Column]()

    def set_status(msg: str, color: str = TEXT2):
        if status_bar_text.current:
            status_bar_text.current.value = msg
            status_bar_text.current.color = color
            page.update()

    # ═══════════════════════════════════════════
    #  TAB 1: DEFINICIÓN MANUAL
    # ═══════════════════════════════════════════

    manual_alphabet_field = ft.TextField(
        label="Alfabeto (separar con comas, ej: a,b,0,1)",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13),
    )
    manual_states_field = ft.TextField(
        label="Estados (separar con comas, ej: q0,q1,q2)",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13),
    )
    manual_initial_field = ft.TextField(
        label="Estado inicial",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13), width=200,
    )
    manual_accept_field = ft.TextField(
        label="Estados de aceptación (separar con comas)",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13),
    )
    manual_name_field = ft.TextField(
        label="Nombre del AFD",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13),
        value="Mi AFD",
    )

    transition_table_container = ft.Column(spacing=6)
    transition_inputs: dict = {}  # (state, symbol) -> TextField

    def build_transition_table(_=None):
        transition_inputs.clear()
        transition_table_container.controls.clear()
        states = [s.strip() for s in manual_states_field.value.split(",") if s.strip()]
        alphabet = [a.strip() for a in manual_alphabet_field.value.split(",") if a.strip()]
        if not states or not alphabet:
            transition_table_container.controls.append(
                ft.Text("Define estados y alfabeto primero.", color=TEXT2, font_family=FONT, size=12)
            )
            page.update()
            return

        header = ft.Row([ft.Container(width=80)] +
                        [ft.Container(ft.Text(sym, color=ACCENT, font_family=FONT, size=12,
                                              weight=ft.FontWeight.BOLD, text_align="center"),
                                      width=90)
                         for sym in alphabet])
        transition_table_container.controls.append(header)

        for state in states:
            cells = [ft.Container(
                ft.Text(state, color=TEXT, font_family=FONT, size=12, weight=ft.FontWeight.BOLD),
                width=80
            )]
            for sym in alphabet:
                tf = ft.TextField(
                    value=afd.transitions.get((state, sym), ""),
                    border_color=BORDER, focused_border_color=ACCENT,
                    color=TEXT, bgcolor=SURFACE, text_style=ft.TextStyle(font_family=FONT, size=12),
                    width=90, height=38,
                    text_align="center",
                    hint_text="—", hint_style=ft.TextStyle(color=BORDER),
                )
                transition_inputs[(state, sym)] = tf
                cells.append(tf)
            transition_table_container.controls.append(ft.Row(cells, spacing=4))
        page.update()

    def save_manual_afd(_=None):
        states = [s.strip() for s in manual_states_field.value.split(",") if s.strip()]
        alphabet = [a.strip() for a in manual_alphabet_field.value.split(",") if a.strip()]
        initial = manual_initial_field.value.strip()
        accepts = [s.strip() for s in manual_accept_field.value.split(",") if s.strip()]

        if not states or not alphabet or not initial:
            set_status("⚠ Completa todos los campos requeridos.", DANGER)
            return

        afd.states = states
        afd.alphabet = alphabet
        afd.initial_state = initial
        afd.accept_states = set(accepts)
        afd.name = manual_name_field.value.strip() or "Mi AFD"
        afd.transitions = {}
        for (state, sym), tf in transition_inputs.items():
            val = tf.value.strip()
            if val:
                afd.transitions[(state, sym)] = val

        set_status(f"✓ AFD '{afd.name}' guardado correctamente ({len(states)} estados, {len(alphabet)} símbolos).", ACCENT2)
        refresh_afd_info()

    manual_tab = ft.Column([
        section_title("► DEFINICIÓN MANUAL DE AFD"),
        divider(),
        ft.Row([manual_name_field], expand=True),
        ft.Row([manual_alphabet_field, manual_states_field], spacing=12, expand=True),
        ft.Row([manual_initial_field, manual_accept_field], spacing=12, expand=True),
        ft.Row([
            ft.ElevatedButton("Generar tabla de transiciones", on_click=build_transition_table,
                              bgcolor=SURFACE2, color=ACCENT,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("Guardar AFD", on_click=save_manual_afd,
                              bgcolor=ACCENT, color=BG,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
        ], spacing=12),
        divider(),
        section_title("► TABLA DE TRANSICIONES"),
        # REPARADO:
        ft.Container(transition_table_container, padding=8, bgcolor=SURFACE,
                     border=border_all(1, BORDER), border_radius=8),
    ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    # ═══════════════════════════════════════════
    #  TAB 2: IMPORTAR ARCHIVO
    # ═══════════════════════════════════════════

    import_result = ft.Column(spacing=6)
    
    txt_ruta_archivo = ft.TextField(
        label="Ruta del archivo (ej: C:/descargas/auto.jff)",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13),
        expand=True
    )

    def cargar_archivo_manual(e):
        ruta = txt_ruta_archivo.value.strip()
        ruta = ruta.replace('"', '').replace("'", "")
        if not ruta: return
        try:
            content = Path(ruta).read_text(encoding="utf-8")
            ext = Path(ruta).suffix.lower()
            if ext == ".jff":
                afd.from_jff(content)
            elif ext == ".json":
                afd.from_json(json.loads(content))
            elif ext == ".xml":
                afd.from_xml(content)
            else:
                set_status("⚠ Formato no soportado. Usa .jff, .json o .xml", DANGER)
                page.update()
                return

            import_result.controls.clear()
            import_result.controls.append(
                ft.Text(f"✓ Autómata '{afd.name}' cargado correctamente", color=ACCENT2, font_family=FONT, size=13, weight=ft.FontWeight.BOLD)
            )
            import_result.controls.append(
                ft.Row([chip(f"Estados: {len(afd.states)}"), chip(f"Alfabeto: {','.join(afd.alphabet)}"),
                        chip(f"Inicial: {afd.initial_state}"), chip(f"Aceptación: {len(afd.accept_states)}", ACCENT2)], wrap=True, spacing=8)
            )
            set_status(f"✓ Archivo '{Path(ruta).name}' importado.", ACCENT2)
            refresh_afd_info()
            # Pre-fill manual fields
            manual_name_field.value = afd.name
            manual_states_field.value = ",".join(afd.states)
            manual_alphabet_field.value = ",".join(afd.alphabet)
            manual_initial_field.value = afd.initial_state
            manual_accept_field.value = ",".join(afd.accept_states)
        except Exception as ex:
            import_result.controls.clear()
            import_result.controls.append(ft.Text(f"✗ Error: {ex}", color=DANGER, font_family=FONT, size=12))
            set_status(f"✗ Error al importar: {ex}", DANGER)
        page.update()

    import_tab = ft.Column([
        section_title("► IMPORTAR AUTÓMATA DESDE ARCHIVO"),
        divider(),
        ft.Text("Formatos soportados: .jff (JFLAP), .json, .xml", color=TEXT2, font_family=FONT, size=12),
        ft.Row([
            txt_ruta_archivo,
            ft.ElevatedButton("📂  Cargar archivo",
                              on_click=cargar_archivo_manual,
                              bgcolor=ACCENT, color=BG,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
        ], spacing=12),
        divider(),
        import_result,
    ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    # ═══════════════════════════════════════════
    #  TAB 3: SIMULACIÓN
    # ═══════════════════════════════════════════

    sim_input = ft.TextField(
        label="Cadena a validar",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=14), width=320,
        hint_text="Ingresa una cadena...",
    )
    sim_result_container = ft.Column(spacing=8)
    trace_data: list = []
    current_step = [0]

    def run_simulation(_=None):
        if not afd.initial_state:
            set_status("⚠ No hay AFD cargado.", DANGER)
            return
        string = sim_input.value
        accepted, trace = afd.validate(string)
        trace_data.clear()
        trace_data.extend(trace)
        current_step[0] = len(trace) - 1
        render_trace(trace, accepted, string)

    def render_trace(trace: list, accepted: bool, string: str):
        sim_result_container.controls.clear()

        # Result banner
        color = ACCENT2 if accepted else DANGER
        symbol = "✓ ACEPTADA" if accepted else "✗ RECHAZADA"
        sim_result_container.controls.append(
            ft.Container(
                ft.Row([ft.Text(f'"{string}"  →  {symbol}',
                               color=color, font_family=FONT, size=16, weight=ft.FontWeight.BOLD)],
                       alignment="center"),
                # REPARADO:
                bgcolor=f"{color}15", border=border_all(2, color),
                border_radius=8, padding=12,
            )
        )

        # Step-by-step trace
        sim_result_container.controls.append(section_title("► TRAZA DE EJECUCIÓN"))
        for step in trace:
            step_color = DANGER if step.get("state") in ("ERROR", "MUERTO") else TEXT
            sym_text = f"—{step['symbol']}→" if step.get("symbol") else "inicio"
            row = ft.Row([
                ft.Container(ft.Text(f"Paso {step['step']}", color=TEXT2, font_family=FONT, size=11), width=60),
                ft.Container(ft.Text(sym_text, color=WARNING, font_family=FONT, size=12), width=70),
                chip(step["state"], color=ACCENT2 if step["state"] in afd.accept_states else (DANGER if step["state"] in ("ERROR","MUERTO") else ACCENT)),
                ft.Text(f"  resto: '{step['remaining']}'", color=TEXT2, font_family=FONT, size=11) if step.get("remaining") is not None else ft.Text(""),
            ], spacing=8)
            sim_result_container.controls.append(row)
            if step.get("error"):
                sim_result_container.controls.append(
                    ft.Text(f"  ↳ {step['error']}", color=DANGER, font_family=FONT, size=11)
                )

        page.update()

    def step_forward(_=None):
        if not afd.initial_state:
            set_status("⚠ No hay AFD cargado.", DANGER)
            return
            
        string = sim_input.value
        
        # Si es el primer clic, calculamos la traza y empezamos en el paso 0
        if not trace_data:
            accepted, trace = afd.validate(string)
            trace_data.extend(trace)
            current_step[0] = 0

        # Mostramos la interfaz solo hasta el paso actual
        idx = min(current_step[0], len(trace_data)-1)
        render_trace_partial(trace_data[:idx+1], string)

    def render_trace_partial(trace: list, string: str):
        last = trace[-1]
        accepted = last["state"] in afd.accept_states and last.get("remaining") == "" and not last.get("error")
        sim_result_container.controls.clear()

        status_text = "EN PROGRESO..." if last.get("remaining") else ("ACEPTADA ✓" if last["state"] in afd.accept_states else "RECHAZADA ✗")
        color = ACCENT2 if "ACEPT" in status_text else (DANGER if "RECHAZ" in status_text else WARNING)
        sim_result_container.controls.append(
            ft.Container(
                ft.Row([ft.Text(f'"{string}"  →  Paso {last["step"]}  |  {status_text}',
                               color=color, font_family=FONT, size=14, weight=ft.FontWeight.BOLD)],
                       alignment="center"),
                # REPARADO:
                bgcolor=f"{color}15", border=border_all(1, color),
                border_radius=8, padding=10,
            )
        )
        sim_result_container.controls.append(section_title("► TRAZA PARCIAL"))
        for step in trace:
            sym_text = f"—{step['symbol']}→" if step.get("symbol") else "inicio"
            row = ft.Row([
                ft.Container(ft.Text(f"Paso {step['step']}", color=TEXT2, font_family=FONT, size=11), width=60),
                ft.Container(ft.Text(sym_text, color=WARNING, font_family=FONT, size=12), width=70),
                chip(step["state"], color=ACCENT2 if step["state"] in afd.accept_states else ACCENT),
            ], spacing=8)
            sim_result_container.controls.append(row)
        if current_step[0] < len(trace_data)-1:
            current_step[0] += 1
        page.update()

    # --- FUNCIÓN DE REINICIO SEGURA ---
    def restart_sim(e):
        trace_data.clear()
        sim_result_container.controls.clear()
        current_step[0] = 0
        page.update()

    sim_tab = ft.Column([
        section_title("► SIMULACIÓN Y VALIDACIÓN DE CADENAS"),
        divider(),
        ft.Row([
            sim_input,
            ft.ElevatedButton("▶  Validar completo", on_click=run_simulation,
                              bgcolor=ACCENT2, color=BG,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("⏭  Paso a paso", on_click=step_forward,
                              bgcolor=ACCENT, color=BG,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("⏮  Reiniciar", on_click=restart_sim,
                              bgcolor=SURFACE2, color=TEXT2,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
        ], spacing=10, wrap=True),
        divider(),
        # REPARADO:
        ft.Container(sim_result_container, padding=10, bgcolor=SURFACE,
                     border=border_all(1, BORDER), border_radius=8,
                     expand=True),
    ], spacing=10, expand=True)

    # ═══════════════════════════════════════════
    #  TAB 4: EXPORTAR
    # ═══════════════════════════════════════════

    export_result = ft.Text("", color=ACCENT2, font_family=FONT, size=12)
    export_dir_text = ft.Text("Directorio de salida: ./exports/", color=TEXT2, font_family=FONT, size=12)

    def export_afd(fmt: str):
        if not afd.initial_state:
            set_status("⚠ No hay AFD para exportar.", DANGER)
            return
        out_dir = Path("./exports")
        out_dir.mkdir(exist_ok=True)
        name_safe = re.sub(r"[^\w\-]", "_", afd.name)
        try:
            if fmt == "json":
                path = out_dir / f"{name_safe}.json"
                path.write_text(json.dumps(afd.to_json(), indent=2, ensure_ascii=False), encoding="utf-8")
            elif fmt == "xml":
                path = out_dir / f"{name_safe}.xml"
                path.write_text(afd.to_xml(), encoding="utf-8")
            elif fmt == "jff":
                path = out_dir / f"{name_safe}.jff"
                path.write_text(afd.to_jff(), encoding="utf-8")
            export_result.value = f"✓ Exportado: {path.resolve()}"
            export_result.color = ACCENT2
            set_status(f"✓ Exportado como {fmt.upper()}: {path.name}", ACCENT2)
        except Exception as ex:
            export_result.value = f"✗ Error: {ex}"
            export_result.color = DANGER
            set_status(f"✗ Error al exportar: {ex}", DANGER)
        page.update()

    export_tab = ft.Column([
        section_title("► EXPORTAR AUTÓMATA"),
        divider(),
        ft.Text("El autómata actualmente cargado se exportará en el formato seleccionado.", color=TEXT2, font_family=FONT, size=12),
        ft.Row([
            ft.ElevatedButton("Exportar .jff", on_click=lambda _: export_afd("jff"),
                              bgcolor=ACCENT, color=BG,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("Exportar .json", on_click=lambda _: export_afd("json"),
                              bgcolor=SURFACE2, color=ACCENT,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("Exportar .xml", on_click=lambda _: export_afd("xml"),
                              bgcolor=SURFACE2, color=ACCENT,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
        ], spacing=12),
        export_dir_text,
        export_result,
    ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    # ═══════════════════════════════════════════
    #  TAB 5: SUBCADENAS / PREFIJOS / SUFIJOS
    # ═══════════════════════════════════════════

    str_ops_input = ft.TextField(
        label="Cadena de entrada",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=14), width=320,
    )
    str_ops_result = ft.Column(spacing=8)

    def run_str_ops(_=None):
        s = str_ops_input.value
        if not s:
            return
        prefixes = get_prefixes(s)
        suffixes = get_suffixes(s)
        substrings = get_substrings(s)

        str_ops_result.controls.clear()

        def make_list(title, items, color):
            chips_row = ft.Row(
                [ft.Container(
                    ft.Text(f'"{i}"' if i else '""', color=color, font_family=FONT, size=11),
                    # REPARADO:
                    bgcolor=f"{color}18", border=border_all(1, color),
                    border_radius=4, padding=ft.Padding(left=6, right=6, top=2, bottom=2)
                ) for i in items],
                wrap=True, spacing=6, run_spacing=6
            )
            return ft.Column([
                ft.Text(f"{title} ({len(items)})", color=color, font_family=FONT, size=12, weight=ft.FontWeight.BOLD),
                chips_row,
            ], spacing=4)

        str_ops_result.controls.extend([
            make_list("PREFIJOS", prefixes, ACCENT),
            divider(),
            make_list("SUFIJOS", suffixes, WARNING),
            divider(),
            make_list("SUBCADENAS", substrings, ACCENT2),
        ])
        page.update()

    def save_str_ops(_=None):
        s = str_ops_input.value
        if not s:
            return
        out_dir = Path("./exports")
        out_dir.mkdir(exist_ok=True)
        path = out_dir / f"str_ops_{s[:20]}.txt"
        content = f"Cadena: {s}\n\nPREFIJOS:\n{chr(10).join(get_prefixes(s))}\n\nSUFIJOS:\n{chr(10).join(get_suffixes(s))}\n\nSUBCADENAS:\n{chr(10).join(get_substrings(s))}\n"
        path.write_text(content, encoding="utf-8")
        set_status(f"✓ Guardado: {path.name}", ACCENT2)

    str_ops_tab = ft.Column([
        section_title("► SUBCADENAS, PREFIJOS Y SUFIJOS"),
        divider(),
        ft.Row([
            str_ops_input,
            ft.ElevatedButton("Calcular", on_click=run_str_ops,
                              bgcolor=ACCENT, color=BG,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("Guardar .txt", on_click=save_str_ops,
                              bgcolor=SURFACE2, color=ACCENT,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
        ], spacing=10, wrap=True),
        divider(),
        # REPARADO:
        ft.Container(str_ops_result, padding=10, bgcolor=SURFACE,
                     border=border_all(1, BORDER), border_radius=8,
                     expand=True),
    ], spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)

    # ═══════════════════════════════════════════
    #  TAB 6: CERRADURA DE KLEENE
    # ═══════════════════════════════════════════

    kleene_alphabet_field = ft.TextField(
        label="Alfabeto (separar con comas)",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13), width=300,
        value="a,b",
    )
    kleene_max_field = ft.TextField(
        label="Longitud máxima",
        border_color=BORDER, focused_border_color=ACCENT,
        color=TEXT, label_style=ft.TextStyle(color=TEXT2, font_family=FONT),
        bgcolor=SURFACE2, text_style=ft.TextStyle(font_family=FONT, size=13), width=150,
        value="3", input_filter=ft.NumbersOnlyInputFilter(),
    )
    kleene_result = ft.Column(spacing=8)

    def run_kleene(kind: str):
        alph = [a.strip() for a in kleene_alphabet_field.value.split(",") if a.strip()]
        if not alph:
            return
        try:
            max_len = int(kleene_max_field.value or 3)
            max_len = min(max_len, 6)
        except ValueError:
            max_len = 3

        if kind == "star":
            result = kleene_star(alph, max_len)
            title_str = f"Σ* — Cerradura de Kleene ({len(result)} cadenas)"
        else:
            result = kleene_plus(alph, max_len)
            title_str = f"Σ⁺ — Cerradura Positiva ({len(result)} cadenas)"

        kleene_result.controls.clear()
        kleene_result.controls.append(
            ft.Text(title_str, color=ACCENT, font_family=FONT, size=12, weight=ft.FontWeight.BOLD)
        )
        chips = ft.Row(
            [ft.Container(
                ft.Text(f'"{w}"' if w else '""', color=TEXT, font_family=FONT, size=11),
                # REPARADO:
                bgcolor=SURFACE2, border=border_all(1, BORDER),
                border_radius=4, padding=ft.Padding(left=6, right=6, top=2, bottom=2)
            ) for w in result],
            wrap=True, spacing=6, run_spacing=6
        )
        kleene_result.controls.append(chips)
        page.update()

    def save_kleene(kind: str):
        alph = [a.strip() for a in kleene_alphabet_field.value.split(",") if a.strip()]
        if not alph:
            return
        try:
            max_len = int(kleene_max_field.value or 3)
            max_len = min(max_len, 6)
        except ValueError:
            max_len = 3
        result = kleene_star(alph, max_len) if kind == "star" else kleene_plus(alph, max_len)
        out_dir = Path("./exports")
        out_dir.mkdir(exist_ok=True)
        filename = f"kleene_{'star' if kind=='star' else 'plus'}_{''.join(alph)}.txt"
        path = out_dir / filename
        path.write_text("\n".join(result), encoding="utf-8")
        set_status(f"✓ Guardado: {path.name}", ACCENT2)

    kleene_tab = ft.Column([
        section_title("► CERRADURA DE KLEENE Y POSITIVA"),
        divider(),
        ft.Text("⚠ La longitud máxima se limita a 6 para evitar explosión combinatoria.", color=WARNING, font_family=FONT, size=11),
        ft.Row([kleene_alphabet_field, kleene_max_field], spacing=12),
        ft.Row([
            ft.ElevatedButton("Calcular Σ* (Kleene)", on_click=lambda _: run_kleene("star"),
                              bgcolor=ACCENT, color=BG,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("Calcular Σ⁺ (Positiva)", on_click=lambda _: run_kleene("plus"),
                              bgcolor=SURFACE2, color=ACCENT,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("Guardar Σ*", on_click=lambda _: save_kleene("star"),
                              bgcolor=SURFACE2, color=TEXT2,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
            ft.ElevatedButton("Guardar Σ⁺", on_click=lambda _: save_kleene("plus"),
                              bgcolor=SURFACE2, color=TEXT2,
                              style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))),
        ], spacing=12, wrap=True),
        divider(),
        # REPARADO:
        ft.Container(kleene_result, padding=10, bgcolor=SURFACE,
                     border=border_all(1, BORDER), border_radius=8,
                     expand=True),
    ], spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)

    # ═══════════════════════════════════════════
    #  AFD INFO PANEL (sidebar)
    # ═══════════════════════════════════════════

    afd_info_panel = ft.Column(spacing=6)

    def refresh_afd_info():
        afd_info_panel.controls.clear()
        if not afd.initial_state:
            afd_info_panel.controls.append(
                ft.Text("Sin AFD cargado", color=TEXT2, font_family=FONT, size=11)
            )
        else:
            afd_info_panel.controls.extend([
                ft.Text(afd.name, color=TEXT, font_family=FONT, size=13, weight=ft.FontWeight.BOLD),
                chip(f"Estados: {len(afd.states)}"),
                chip(f"Σ = {{{','.join(afd.alphabet)}}}"),
                chip(f"q₀ = {afd.initial_state}"),
                chip(f"F = {{{','.join(afd.accept_states)}}}", ACCENT2),
                chip(f"δ = {len(afd.transitions)} transiciones", WARNING),
            ])
        page.update()

    refresh_afd_info()

    # ═══════════════════════════════════════════
    #  NAVIGATION
    # ═══════════════════════════════════════════

    tabs_content = [manual_tab, import_tab, sim_tab, export_tab, str_ops_tab, kleene_tab]
    tab_names = ["Definir AFD", "Importar", "Simular", "Exportar", "Sub/Pre/Suf", "Kleene"]
    current_tab = [0]

    tab_buttons = []
    content_area = ft.Column(expand=True)

    def switch_tab(idx: int):
        current_tab[0] = idx
        for i, btn in enumerate(tab_buttons):
            btn.bgcolor = ACCENT if i == idx else SURFACE2
            btn.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=6),
                color=BG if i == idx else TEXT2,
            )
        content_area.controls.clear()
        content_area.controls.append(
            ft.Container(tabs_content[idx], padding=16, expand=True)
        )
        page.update()

    for i, name in enumerate(tab_names):
        btn = ft.ElevatedButton(
            name,
            on_click=lambda _, i=i: switch_tab(i),
            bgcolor=ACCENT if i == 0 else SURFACE2,
            color=BG if i == 0 else TEXT2,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6)),
            height=36,
        )
        tab_buttons.append(btn)

    switch_tab(0)

    # ═══════════════════════════════════════════
    #  LAYOUT
    # ═══════════════════════════════════════════

    header = ft.Container(
        ft.Row([
            ft.Text("AFD", color=ACCENT, font_family=FONT, size=22, weight=ft.FontWeight.BOLD),
            ft.Text(" SIMULATOR", color=TEXT, font_family=FONT, size=22),
            ft.Container(expand=True),
            ft.Text("ESCOM · IPN · Teoría de la Computación",
                    color=TEXT2, font_family=FONT, size=11),
        ], alignment="start"),
        # REPARADO:
        bgcolor=SURFACE, padding=ft.Padding(left=20, right=20, top=12, bottom=12),
        border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
    )

    nav_bar = ft.Container(
        ft.Row(tab_buttons, spacing=6, wrap=True),
        # REPARADO:
        bgcolor=SURFACE, padding=ft.Padding(left=16, right=16, top=8, bottom=8),
        border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
    )

    sidebar = ft.Container(
        ft.Column([
            ft.Text("AFD ACTIVO", color=TEXT2, font_family=FONT, size=10, weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=2)),
            divider(),
            afd_info_panel,
        ], spacing=8),
        width=200, bgcolor=SURFACE,
        # REPARADO:
        border=ft.Border(right=ft.BorderSide(1, BORDER)),
        padding=12,
    )

    status_bar = ft.Container(
        ft.Text("Listo.", ref=status_bar_text, color=TEXT2, font_family=FONT, size=11),
        # REPARADO:
        bgcolor=SURFACE, padding=ft.Padding(left=16, right=16, top=6, bottom=6),
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
    )

    body = ft.Row([
        sidebar,
        ft.Container(content_area, expand=True, bgcolor=BG),
    ], expand=True, spacing=0)

    page.add(
        ft.Column([
            header,
            nav_bar,
            ft.Container(body, expand=True),
            status_bar,
        ], spacing=0, expand=True)
    )

# REPARADO:
ft.run(main)