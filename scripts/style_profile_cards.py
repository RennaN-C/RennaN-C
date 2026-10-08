#!/usr/bin/env python3
"""Ajustes discretos de movimento aos cards SVG gerados pelo GitHub Actions.

Mantem o conteudo e os numeros dos geradores intactos.
"""
from pathlib import Path
from xml.etree import ElementTree


def replace_exact(content: str, before: str, after: str, label: str) -> str:
    occurrences = content.count(before)
    if occurrences != 1:
        raise ValueError(f"{label}: esperado 1 trecho, encontrados {occurrences}")
    return content.replace(before, after, 1)


stats_path = Path("profile/stats.svg")
stats = stats_path.read_text(encoding="utf-8")
stats = replace_exact(
    stats,
    "animation: rankAnimation 1s forwards ease-in-out;",
    "animation: rankAnimation 1s forwards ease-in-out, rankBreath 3.8s ease-in-out 1.2s infinite;",
    "Rank: animacao",
)
stats = replace_exact(
    stats,
    "</style>",
    """@keyframes rankBreath {
  0%, 100% { opacity: 0.8; }
  50% { opacity: 1; }
}
@media (prefers-reduced-motion: reduce) {
  .rank-circle { animation: rankAnimation 0.01s forwards ease-in-out !important; }
}
</style>""",
    "Rank: estilos",
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
    assert root.tag.rsplit("}", 1)[-1] == "svg", f"SVG invalido: {path}"
    assert "@keyframes" in path.read_text(encoding="utf-8")
    print(f"OK: {path} com estilo e animacao validados")
