#!/usr/bin/env python3
"""Refina animações dos SVGs do perfil, preservando métricas e acessibilidade.

O Stats é regenerado a cada execução. Por isso, modificamos somente o SVG
produzido no workflow, sem fixar a nota nem os valores das estatísticas.
"""
import re
from pathlib import Path
from xml.etree import ElementTree


def replace_exact(content: str, before: str, after: str, label: str) -> str:
    occurrences = content.count(before)
    if occurrences != 1:
        raise ValueError(f"{label}: esperado 1 trecho, encontrados {occurrences}")
    return content.replace(before, after, 1)


def animate_rank_letter(content: str) -> str:
    """Desenha primeiro a letra; revela o + (se houver) e depois o anel."""
    # O gerador coloca o rank dentro de <g class="rank-text">,
    # não diretamente numa tag <text class="rank-text">.
    pattern = re.compile(
        r'(?P<open><g class="rank-text">\s*)'
        r'(?P<text_open><text\b[^>]*\bdata-testid="level-rank-icon"[^>]*>)'
        r'(?P<rank>[^<]+)'
        r'(?P<text_close></text>)'
        r'(?P<close>\s*</g>)',
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        raise ValueError("Rank: estrutura esperada não encontrada no SVG gerado")

    rank = match.group("rank").strip()
    if not re.fullmatch(r"[A-Z][+-]?", rank):
        raise ValueError(f"Rank inesperado: {rank!r}")

    base, has_plus = (rank[:-1], True) if rank.endswith("+") else (rank, False)
    outline_label = (
        f'{base}<tspan class="rank-plus-placeholder">+</tspan>'
        if has_plus else rank
    )
    final_label = (
        f'{base}<tspan class="rank-plus">+</tspan>'
        if has_plus else rank
    )

    # Mantém as posições originais e o text-anchor do próprio gerador.
    # O tspan transparente reserva a largura do + para alinhar os contornos.
    text_open = match.group("text_open")
    outline_open = (
        text_open.replace(
            "<text ", '<text class="rank-letter-outline" aria-hidden="true" ', 1
        ).replace('data-testid="level-rank-icon"', "", 1)
    )
    filled_open = text_open.replace(
        "<text ", '<text class="rank-letter-fill" ', 1
    )
    replacement = (
        match.group("open")
        + outline_open + outline_label + "</text>\n          "
        + filled_open + final_label + "</text>"
        + match.group("close")
    )
    return content[:match.start()] + replacement + content[match.end():]


stats_path = Path("profile/stats.svg")
stats = stats_path.read_text(encoding="utf-8")

# Mantém o fim do anel calculado pelo serviço para a nota REAL do usuário.
end_offset = re.search(
    r"@keyframes rankAnimation\s*\{.*?\bto\s*\{\s*"
    r"stroke-dashoffset:\s*([0-9.]+)\s*;",
    stats,
    flags=re.DOTALL,
)
if not end_offset:
    raise ValueError("Rank: offset final do anel não encontrado")
ring_final = end_offset.group(1)

stats = animate_rank_letter(stats)
stats = replace_exact(
    stats,
    "animation: scaleInAnimation 0.3s ease-in-out forwards;",
    "animation: none;",
    "Rank: desativar zoom rápido padrão",
)
stats = replace_exact(
    stats,
    "animation: rankAnimation 1s forwards ease-in-out;",
    (
        "stroke-dashoffset: 251.32741228718345;\n"
        "      animation: rankAnimation 2s ease-in-out 3.6s forwards, "
        "rankBreath 3.8s ease-in-out 5.7s infinite;"
    ),
    "Rank: anel somente depois da letra",
)

stats = replace_exact(
    stats,
    "</style>",
    f"""/* Traço da letra -> preenchimento -> símbolo + -> anel da nota */
.rank-letter-outline {{
  fill: none;
  stroke: #F5F7FA;
  stroke-width: 1.55px;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 180;
  stroke-dashoffset: 180;
  animation: rankLetterTrace 2.85s ease-in-out forwards;
}}
.rank-letter-fill {{
  fill: #F5F7FA;
  opacity: 0;
  animation: rankLetterFill 0.38s ease-out 2.7s forwards;
}}
.rank-plus-placeholder {{
  fill: none;
  stroke: none;
}}
.rank-plus {{
  opacity: 0;
  animation: rankPlusAppear 0.34s ease-out 3.13s forwards;
}}
@keyframes rankLetterTrace {{
  from {{ stroke-dashoffset: 180; }}
  to {{ stroke-dashoffset: 0; }}
}}
@keyframes rankLetterFill {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}
@keyframes rankPlusAppear {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}
@keyframes rankBreath {{
  0%, 100% {{ opacity: 0.8; }}
  50% {{ opacity: 1; }}
}}
@media (prefers-reduced-motion: reduce) {{
  .rank-circle {{
    animation: none !important;
    stroke-dashoffset: {ring_final} !important;
    opacity: 0.85 !important;
  }}
  .rank-letter-outline {{
    display: none !important;
  }}
  .rank-letter-fill, .rank-plus {{
    animation: none !important;
    opacity: 1 !important;
  }}
}}
</style>""",
    "Rank: estilos e movimento reduzido",
)
stats_path.write_text(stats, encoding="utf-8")

streak_path = Path("profile/streak.svg")
streak = streak_path.read_text(encoding="utf-8")
streak = replace_exact(
    streak,
    "<circle cx='247.5' cy='71' r='40' fill='none'",
    "<circle id='profile-streak-ring' cx='247.5' cy='71' r='40' fill='none'",
    "Streak: anel",
)
streak = replace_exact(
    streak,
    "<g transform='translate(247.5, 19.5)' stroke-opacity='0'",
    "<g id='profile-streak-fire' transform='translate(247.5, 19.5)' stroke-opacity='0'",
    "Streak: chama",
)
streak = replace_exact(
    streak,
    "animation: fadein 0.5s linear forwards 0.4s'",
    "animation: fadein 0.5s linear forwards 0.4s, streakBreath 3.8s ease-in-out 1.3s infinite'",
    "Streak: pulso do anel",
)
streak = replace_exact(
    streak,
    "<g id='profile-streak-fire' transform='translate(247.5, 19.5)' stroke-opacity='0' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s'>",
    "<g id='profile-streak-fire' transform='translate(247.5, 19.5)' stroke-opacity='0' style='opacity: 0; animation: fadein 0.5s linear forwards 0.6s, fireBreath 3.2s ease-in-out 1.5s infinite'>",
    "Streak: pulso da chama",
)
streak = replace_exact(
    streak,
    "</style>",
    """@keyframes streakBreath {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.65; }
}
@keyframes fireBreath {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.65; }
}
@media (prefers-reduced-motion: reduce) {
  #profile-streak-ring, #profile-streak-fire {
    animation: none !important;
    opacity: 1 !important;
  }
}
</style>""",
    "Streak: estilos",
)
streak_path.write_text(streak, encoding="utf-8")

for path in (stats_path, streak_path):
    root = ElementTree.parse(path).getroot()
    assert root.tag.rsplit("}", 1)[-1] == "svg", f"SVG inválido: {path}"
    assert "@keyframes" in path.read_text(encoding="utf-8")
    print(f"OK: {path} com estilos, animações e XML válidos")
