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


# Contornos vetoriais em unidades normalizadas de DejaVu Sans Bold (licença livre).
# São apenas traços dos caracteres usados nas notas: C, B, A, S, + e -.
# Não há arquivo de fonte nem dependência adicional no workflow.
RANK_GLYPHS = {
    "S": (1475, "M1227 1446V1130Q1104 1185 987 1213Q870 1241 766 1241Q628 1241 562 1203Q496 1165 496 1085Q496 1025 540.5 991.5Q585 958 702 934L866 901Q1115 851 1220 749Q1325 647 1325 459Q1325 212 1178.5 91.5Q1032 -29 731 -29Q589 -29 446 -2Q303 25 160 78V403Q303 327 436.5 288.5Q570 250 694 250Q820 250 887 292Q954 334 954 412Q954 482 908.5 520Q863 558 727 588L578 621Q354 669 250.5 774Q147 879 147 1057Q147 1280 291 1400Q435 1520 705 1520Q828 1520 958 1501.5Q1088 1483 1227 1446Z"),
    "A": (1585, "M1094 272H492L397 0H10L563 1493H1022L1575 0H1188ZM588 549H997L793 1143Z"),
    "B": (1561, "M786 915Q877 915 924 955Q971 995 971 1073Q971 1150 924 1190.5Q877 1231 786 1231H573V915ZM799 262Q915 262 973.5 311Q1032 360 1032 459Q1032 556 974 604.5Q916 653 799 653H573V262ZM1157 799Q1281 763 1349 666Q1417 569 1417 428Q1417 212 1271 106Q1125 0 827 0H188V1493H766Q1077 1493 1216.5 1399Q1356 1305 1356 1098Q1356 989 1305 912.5Q1254 836 1157 799Z"),
    "C": (1503, "M1372 82Q1266 27 1151 -1Q1036 -29 911 -29Q538 -29 320 179.5Q102 388 102 745Q102 1103 320 1311.5Q538 1520 911 1520Q1036 1520 1151 1492Q1266 1464 1372 1409V1100Q1265 1173 1161 1207Q1057 1241 942 1241Q736 1241 618 1109Q500 977 500 745Q500 514 618 382Q736 250 942 250Q1057 250 1161 284Q1265 318 1372 391Z"),
    "+": (1716, "M977 1284V760H1499V524H977V0H739V524H217V760H739V1284Z"),
    "-": (850, "M111 735H739V444H111Z"),
}


def animate_rank_letter(content: str) -> str:
    """Transforma o texto do rank em paths; a letra é desenhada antes do anel."""
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
        raise ValueError("Rank: estrutura de texto esperada não encontrada")

    rank = match.group("rank").strip()
    if not re.fullmatch(r"[SABC][+-]?", rank):
        raise ValueError(f"Rank não suportado: {rank!r}")

    scale = 26 / 2048
    total = sum(RANK_GLYPHS[g][0] for g in rank)
    left = -10 - (total * scale / 2)  # centralizado no anel atual
    baseline = 16
    groups = []

    for index, symbol in enumerate(rank):
        advance, drawing = RANK_GLYPHS[symbol]
        kind = "rank-glyph" if index == 0 else "rank-suffix"
        groups.append(
            f'<g transform="translate({left:.4f} {baseline}) '
            f'scale({scale:.8f} -{scale:.8f})">'
            f'<path class="{kind}-outline" d="{drawing}" pathLength="100" />'
            f'<path class="{kind}-fill" d="{drawing}" />'
            f'</g>'
        )
        left += advance * scale

    rendered = (
        f'<g class="rank-text" data-testid="level-rank-icon" '
        f'aria-label="Rank {rank}">' + "".join(groups) + '</g>'
    )
    return content[:match.start()] + rendered + content[match.end():]


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
        "rankBreath 3.8s ease-in-out 6.15s infinite;"
    ),
    "Rank: anel somente depois da letra",
)

stats = replace_exact(
    stats,
    "</style>",
    """/* O rank é desenhado por paths reais, não por texto mascarado. */
.rank-glyph-outline, .rank-suffix-outline {
  fill: none;
  stroke: #67E8F9;
  stroke-width: 110;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 100;
  stroke-dashoffset: 100;
}
.rank-glyph-outline {
  animation: rankVectorDraw 2.8s ease-in-out 0.15s forwards,
             rankOutlineFade 0.32s ease-out 2.85s forwards;
}
.rank-glyph-fill {
  fill: #F5F7FA;
  opacity: 0;
  animation: rankVectorFill 0.32s ease-out 2.83s forwards;
}
.rank-suffix-outline {
  animation: rankVectorDraw 0.62s ease-in-out 3.06s forwards,
             rankOutlineFade 0.22s ease-out 3.64s forwards;
}
.rank-suffix-fill {
  fill: #F5F7FA;
  opacity: 0;
  animation: rankVectorFill 0.2s ease-out 3.64s forwards;
}
@keyframes rankVectorDraw {
  to { stroke-dashoffset: 0; }
}
@keyframes rankVectorFill {
  to { opacity: 1; }
}
@keyframes rankOutlineFade {
  to { opacity: 0; }
}
@keyframes rankBreath {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .rank-circle {
    animation: none !important;
    stroke-dashoffset: __RING_FINAL__ !important;
    opacity: 0.85 !important;
  }
  .rank-glyph-outline, .rank-suffix-outline {
    display: none !important;
  }
  .rank-glyph-fill, .rank-suffix-fill {
    animation: none !important;
    opacity: 1 !important;
  }
}
</style>""".replace("__RING_FINAL__", ring_final),
    "Rank: paths vetoriais, sequência e movimento reduzido",
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
