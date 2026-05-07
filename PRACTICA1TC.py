"""
Teoría Formal de Lenguajes — Aplicación Flet
Ejercicio 1: Subcadenas/Prefijos/Sufijos + Cerradura de Kleene/Positiva

Requisitos:
    pip install flet

Ejecución:
    python lenguajes_formales.py
"""

import flet as ft
from itertools import product as iproduct

def get_substrings(s: str) -> list[str]:
    seen = set()
    result = []
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            sub = s[i:j]
            if sub not in seen:
                seen.add(sub)
                result.append(sub)
    return sorted(result, key=lambda x: (len(x), x))


def get_prefixes(s: str) -> list[str]:
    return [s[: i + 1] for i in range(len(s))]


def get_suffixes(s: str) -> list[str]:
    return [s[i:] for i in range(len(s))]


def kleene_star(alphabet: list[str], max_len: int) -> list[str]:
    result = ["ε"]
    queue = [""]
    while queue:
        curr = queue.pop(0)
        for c in alphabet:
            nxt = curr + c
            if len(nxt) <= max_len:
                result.append(nxt)
                queue.append(nxt)
    return result


def kleene_plus(alphabet: list[str], max_len: int) -> list[str]:
    return [s for s in kleene_star(alphabet, max_len) if s != "ε"]


def export_to_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

BG        = "#0a0a0f"
CARD      = "#12121a"
BORDER    = "#1e1e2e"
NEON      = "#00ffb3"
PURPLE    = "#7b61ff"
PINK      = "#ff4f7b"
TEXT_DIM  = "#666677"
WHITE     = "#e8e8f0"


def chip(text: str, color: str, bg: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, font_family="monospace", size=13, color=color),
        bgcolor=bg,
        border=ft.border.all(1, color + "44"),
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )


def section_card(title: str, color: str, chips: list[ft.Control], count: int) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(title, font_family="monospace", size=11,
                                    color=color, weight="bold"),
                            ft.Container(
                                content=ft.Text(str(count), font_family="monospace",
                                                size=10, color=color),
                                bgcolor=color + "18",
                                border_radius=100,
                                padding=ft.padding.symmetric(horizontal=9, vertical=3),
                            ),
                        ],
                        alignment="spaceBetween",
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, BORDER)),
                ),
                ft.Container(
                    content=ft.Row(chips, wrap=True, spacing=8),
                    padding=16,
                ),
            ],
            spacing=0,
        ),
        bgcolor=CARD,
        border=ft.border.all(1, BORDER),
        border_radius=12,
    )


# ─── Pestaña 1: Subcadenas / Prefijos / Sufijos ───────────────────────────────

def build_tab_subcadenas(page: ft.Page) -> ft.Control:
    result_col = ft.Column(scroll="auto", spacing=14, expand=True)
    stat_sub   = ft.Text("—", size=28, weight="bold", color=NEON, font_family="monospace")
    stat_pre   = ft.Text("—", size=28, weight="bold", color=PURPLE, font_family="monospace")
    stat_suf   = ft.Text("—", size=28, weight="bold", color=PINK, font_family="monospace")
    snack      = ft.SnackBar(content=ft.Text(""), bgcolor=NEON)
    page.overlay.append(snack)

    last_results: dict = {}

    input_field = ft.TextField(
        label="Cadena σ",
        hint_text="ej: abc",
        border_color=BORDER,
        focused_border_color=NEON,
        cursor_color=NEON,
        label_style=ft.TextStyle(color=TEXT_DIM, size=11, font_family="monospace"),
        text_style=ft.TextStyle(color=WHITE, size=15, font_family="monospace"),
        bgcolor=BG,
        border_radius=8,
        filled=True,
        fill_color=BG,
    )

    def compute(e):
        s = input_field.value.strip()
        if not s:
            return
        subs = get_substrings(s)
        pres = get_prefixes(s)
        sufs = get_suffixes(s)
        last_results["subs"] = subs
        last_results["pres"] = pres
        last_results["sufs"] = sufs
        last_results["s"]    = s

        stat_sub.value = str(len(subs))
        stat_pre.value = str(len(pres))
        stat_suf.value = str(len(sufs))

        result_col.controls.clear()
        result_col.controls.append(
            section_card("SUBCADENAS", NEON,
                         [chip(t, NEON, NEON + "0a") for t in subs], len(subs))
        )
        result_col.controls.append(
            section_card("PREFIJOS", PURPLE,
                         [chip(t, PURPLE, PURPLE + "0a") for t in pres], len(pres))
        )
        result_col.controls.append(
            section_card("SUFIJOS", PINK,
                         [chip(t, PINK, PINK + "0a") for t in sufs], len(sufs))
        )
        page.update()

    def export(e):
        if not last_results:
            return
        s    = last_results["s"]
        subs = last_results["subs"]
        pres = last_results["pres"]
        sufs = last_results["sufs"]
        txt = (
            f'Cadena: "{s}"\n\n'
            f"SUBCADENAS ({len(subs)}):\n{', '.join(subs)}\n\n"
            f"PREFIJOS ({len(pres)}):\n{', '.join(pres)}\n\n"
            f"SUFIJOS ({len(sufs)}):\n{', '.join(sufs)}\n"
        )
        filename = f"subcadenas_{s}.txt"
        export_to_file(filename, txt)
        snack.content = ft.Text(f"✓  Guardado como  {filename}", color="#000", weight="bold")
        snack.open = True
        page.update()

    input_field.on_submit = compute

    left = ft.Container(
        content=ft.Column(
            [
                ft.Text("// ENTRADA", font_family="monospace", size=11,
                        color=PURPLE, weight="bold"),
                ft.Container(
                    content=ft.Text(
                        "Ingresa una cadena para calcular sus "
                        "subcadenas, prefijos y sufijos.",
                        size=12, color=TEXT_DIM, font_family="monospace",
                    ),
                    bgcolor=NEON + "08",
                    border=ft.border.all(1, NEON + "22"),
                    border_radius=8,
                    padding=12,
                ),
                input_field,
                ft.Row(
                    [
                        ft.Column(
                            [stat_sub, ft.Text("SUBCADENAS", size=10, color=TEXT_DIM,
                                               font_family="monospace")],
                            horizontal_alignment="center",
                        ),
                        ft.Column(
                            [stat_pre, ft.Text("PREFIJOS", size=10, color=TEXT_DIM,
                                               font_family="monospace")],
                            horizontal_alignment="center",
                        ),
                        ft.Column(
                            [stat_suf, ft.Text("SUFIJOS", size=10, color=TEXT_DIM,
                                               font_family="monospace")],
                            horizontal_alignment="center",
                        ),
                    ],
                    alignment="spaceAround",
                ),
                ft.ElevatedButton(
                    "CALCULAR",
                    on_click=compute,
                    bgcolor=NEON,
                    color="#000",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        text_style=ft.TextStyle(font_family="monospace",
                                                weight="bold",
                                                size=12),
                    ),
                    width=999,
                    height=46,
                ),
                ft.OutlinedButton(
                    "EXPORTAR .TXT",
                    on_click=export,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(1, BORDER),
                        color=TEXT_DIM,
                        text_style=ft.TextStyle(font_family="monospace",
                                                size=11),
                    ),
                    width=999,
                    height=42,
                ),
            ],
            spacing=16,
        ),
        bgcolor=CARD,
        border=ft.border.all(1, BORDER),
        border_radius=12,
        padding=24,
        width=360,
    )

    empty = ft.Container(
        content=ft.Text("— ingresa una cadena para comenzar —",
                        font_family="monospace", size=12, color=BORDER),
        expand=True,
        height=200,
    )
    result_col.controls.append(empty)

    return ft.Row(
        [left, ft.Container(content=result_col, expand=True)],
        spacing=24,
        vertical_alignment="start",
        expand=True,
    )


# ─── Pestaña 2: Cerradura de Kleene / Positiva ───────────────────────────────

def build_tab_kleene(page: ft.Page) -> ft.Control:
    result_col = ft.Column(scroll="auto", spacing=14, expand=True)
    stat_total = ft.Text("—", size=28, weight="bold", color=NEON, font_family="monospace")
    snack      = ft.SnackBar(content=ft.Text(""), bgcolor=NEON)
    page.overlay.append(snack)

    last_results: dict = {}
    DISPLAY_LIMIT = 2000

    alpha_field = ft.TextField(
        label="Alfabeto Σ",
        hint_text="ej: ab  ó  01",
        border_color=BORDER,
        focused_border_color=NEON,
        cursor_color=NEON,
        label_style=ft.TextStyle(color=TEXT_DIM, size=11, font_family="monospace"),
        text_style=ft.TextStyle(color=WHITE, size=15, font_family="monospace"),
        bgcolor=BG,
        border_radius=8,
        filled=True,
        fill_color=BG,
    )

    maxlen_field = ft.TextField(
        label="Longitud máxima",
        hint_text="1 – 8",
        value="3",
        border_color=BORDER,
        focused_border_color=NEON,
        cursor_color=NEON,
        label_style=ft.TextStyle(color=TEXT_DIM, size=11, font_family="monospace"),
        text_style=ft.TextStyle(color=WHITE, size=15, font_family="monospace"),
        bgcolor=BG,
        border_radius=8,
        filled=True,
        fill_color=BG,
        keyboard_type="number",
    )

    def _run(kind: str):
        raw = alpha_field.value.replace(" ", "")
        chars = list(dict.fromkeys(raw))   # deduplicate, preserve order
        if not chars:
            return
        try:
            ml = int(maxlen_field.value)
            ml = max(1, min(8, ml))
        except ValueError:
            ml = 3
        maxlen_field.value = str(ml)

        data = kleene_star(chars, ml) if kind == "star" else kleene_plus(chars, ml)
        last_results["kind"]  = kind
        last_results["chars"] = chars
        last_results["ml"]    = ml
        last_results["data"]  = data

        stat_total.value = str(len(data))

        color  = NEON if kind == "star" else PURPLE
        label  = "CERRADURA DE KLEENE  Σ*" if kind == "star" else "CERRADURA POSITIVA  Σ+"
        shown  = data[:DISPLAY_LIMIT]
        chips  = []
        for t in shown:
            if t == "ε":
                chips.append(chip("ε", PINK, PINK + "0a"))
            else:
                chips.append(chip(t, color, color + "0a"))

        controls = [
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(label, font_family="monospace", size=11,
                                color=color, weight="bold"),
                        ft.Container(
                            content=ft.Text(f"{len(data):,}", font_family="monospace",
                                            size=10, color=color),
                            bgcolor=color + "18",
                            border_radius=100,
                            padding=ft.padding.symmetric(horizontal=9, vertical=3),
                        ),
                    ],
                    alignment="spaceBetween",
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                border=ft.border.only(bottom=ft.border.BorderSide(1, BORDER)),
            ),
            ft.Container(
                content=ft.Row(chips, wrap=True, spacing=8),
                padding=16,
            ),
        ]

        if len(data) > DISPLAY_LIMIT:
            controls.append(
                ft.Container(
                    content=ft.Text(
                        f"⚠  Mostrando {DISPLAY_LIMIT:,} de {len(data):,} — exporta para ver todas",
                        font_family="monospace", size=11, color=PINK,
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    border=ft.border.only(top=ft.border.BorderSide(1, BORDER)),
                )
            )

        result_col.controls.clear()
        result_col.controls.append(
            ft.Container(
                content=ft.Column(controls, spacing=0),
                bgcolor=CARD,
                border=ft.border.all(1, BORDER),
                border_radius=12,
            )
        )
        page.update()

    def export(e):
        if not last_results:
            return
        kind  = last_results["kind"]
        chars = last_results["chars"]
        ml    = last_results["ml"]
        data  = last_results["data"]
        tipo  = "Cerradura de Kleene (Σ*)" if kind == "star" else "Cerradura Positiva (Σ+)"
        txt = (
            f"Alfabeto: {{{', '.join(chars)}}}\n"
            f"Longitud máxima: {ml}\n"
            f"Tipo: {tipo}\n"
            f"Total de cadenas: {len(data):,}\n\n"
            + ", ".join(data) + "\n"
        )
        filename = f"cerradura_{'kleene' if kind == 'star' else 'positiva'}.txt"
        export_to_file(filename, txt)
        snack.content = ft.Text(f"✓  Guardado como  {filename}", color="#000", weight="bold")
        snack.open = True
        page.update()

    left = ft.Container(
        content=ft.Column(
            [
                ft.Text("// ENTRADA", font_family="monospace", size=11,
                        color=PURPLE, weight="bold"),
                ft.Container(
                    content=ft.Text(
                        "Σ*  incluye la cadena vacía  ε\nΣ+  excluye la cadena vacía",
                        size=12, color=TEXT_DIM, font_family="monospace",
                    ),
                    bgcolor=NEON + "08",
                    border=ft.border.all(1, NEON + "22"),
                    border_radius=8,
                    padding=12,
                ),
                alpha_field,
                maxlen_field,
                ft.Row(
                    [
                        ft.Column(
                            [stat_total,
                             ft.Text("CADENAS", size=10, color=TEXT_DIM, font_family="monospace")],
                            horizontal_alignment="center",
                            expand=True,
                        ),
                    ],
                    alignment="spaceAround",
                ),
                ft.ElevatedButton(
                    "KLEENE  Σ*",
                    on_click=lambda e: _run("star"),
                    bgcolor=NEON,
                    color="#000",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        text_style=ft.TextStyle(font_family="monospace",
                                                weight="bold",
                                                size=12),
                    ),
                    width=999,
                    height=46,
                ),
                ft.OutlinedButton(
                    "POSITIVA  Σ+",
                    on_click=lambda e: _run("plus"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(1, PURPLE),
                        color=PURPLE,
                        text_style=ft.TextStyle(font_family="monospace",
                                                size=12),
                    ),
                    width=999,
                    height=44,
                ),
                ft.OutlinedButton(
                    "EXPORTAR .TXT",
                    on_click=export,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        side=ft.BorderSide(1, BORDER),
                        color=TEXT_DIM,
                        text_style=ft.TextStyle(font_family="monospace",
                                                size=11),
                    ),
                    width=999,
                    height=42,
                ),
            ],
            spacing=16,
        ),
        bgcolor=CARD,
        border=ft.border.all(1, BORDER),
        border_radius=12,
        padding=24,
        width=360,
    )

    empty = ft.Container(
        content=ft.Text("— define un alfabeto y genera la cerradura —",
                        font_family="monospace", size=12, color=BORDER),
        expand=True,
        height=200,
    )
    result_col.controls.append(empty)

    return ft.Row(
        [left, ft.Container(content=result_col, expand=True)],
        spacing=24,
        vertical_alignment="start",
        expand=True,
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def main(page: ft.Page):
    page.title        = "Teoría Formal de Lenguajes"
    page.bgcolor      = BG
    page.padding      = 0
    page.fonts        = {}
    page.theme = ft.Theme(color_scheme_seed=NEON)

    # Header
    header = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    width=12, height=12,
                    bgcolor=NEON,
                    border_radius=6,
                    shadow=ft.BoxShadow(blur_radius=12, color=NEON),
                ),
                ft.Text("TEORÍA FORMAL DE LENGUAJES", size=17,
                        weight="w800", color=WHITE,
                        font_family="monospace"),
                ft.Container(expand=True),
                ft.Text("AUTÓMATAS · CADENAS · CERRADURAS",
                        size=10, color=NEON, font_family="monospace"),
            ],
            vertical_alignment="center",
            spacing=14,
        ),
        bgcolor=BG,
        border=ft.border.only(bottom=ft.border.BorderSide(1, BORDER)),
        padding=ft.padding.symmetric(horizontal=36, vertical=22),
    )

    # Tabs
    tab_sub = build_tab_subcadenas(page)
    tab_kle = build_tab_kleene(page)

    content_container = ft.Container(
        content=tab_sub,
        padding=ft.padding.symmetric(horizontal=36, vertical=32),
        expand=True,
    )

    def switch_tab(idx: int):
        for i, btn in enumerate(tab_row.controls):
            btn.style = ft.ButtonStyle(
                color=NEON if i == idx else TEXT_DIM,
                bgcolor="transparent",
                text_style=ft.TextStyle(font_family="monospace", size=11),
                shape=ft.RoundedRectangleBorder(radius=0),
            )
        content_container.content = tab_sub if idx == 0 else tab_kle
        page.update()

    btn0 = ft.TextButton(
        "SUBCADENAS / PREFIJOS / SUFIJOS",
        on_click=lambda e: switch_tab(0),
        style=ft.ButtonStyle(
            color=NEON,
            text_style=ft.TextStyle(font_family="monospace", size=11),
            shape=ft.RoundedRectangleBorder(radius=0),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )
    btn1 = ft.TextButton(
        "CERRADURA KLEENE / POSITIVA",
        on_click=lambda e: switch_tab(1),
        style=ft.ButtonStyle(
            color=TEXT_DIM,
            text_style=ft.TextStyle(font_family="monospace", size=11),
            shape=ft.RoundedRectangleBorder(radius=0),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )
    tab_row = ft.Row([btn0, btn1], spacing=0)

    tab_bar = ft.Container(
        content=tab_row,
        border=ft.border.only(bottom=ft.border.BorderSide(1, BORDER)),
        padding=ft.padding.only(left=24),
    )

    page.add(
        ft.Column(
            [
                header,
                tab_bar,
                content_container,
            ],
            spacing=0,
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)