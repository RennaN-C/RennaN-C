# Perfil GitHub — identidade e rollback

## Ponto de retorno preservado

- Repositório: `RennaN-C/RennaN-C`
- Branch de backup: `backup/profile-before-identity-refresh-2026-10-08`
- Commit original exato: `e16117aa84c01a49a25d3fdeb8f21cb404a7d7e9`
- Branch de trabalho: `feat/profile-identity-refresh`
- Branch pública atual: `main` (**não modificada por este redesign**).

O backup inclui o `banner.png` original, o README, os SVGs gerados e o workflow/script que existiam antes do redesign. Não é necessário alterar credenciais ou secrets para desfazer o tema.

## Reverter depois do merge (sem reescrever o histórico)

Execute no clone local com as mudanças de trabalho salvas:

```bash
git checkout main
git pull --ff-only

git restore --source backup/profile-before-identity-refresh-2026-10-08 -- \
  README.md \
  .github/workflows/profile-stats.yml \
  scripts/style_profile_cards.py \
  profile/stats.svg \
  profile/streak.svg

git rm banner-v2.svg
git add -A
git commit -m "revert: restore profile appearance before identity refresh"
git push origin main
```

Se a branch de backup não estiver no clone local:

```bash
git fetch origin backup/profile-before-identity-refresh-2026-10-08
```

Depois use como fonte `origin/backup/profile-before-identity-refresh-2026-10-08` no `git restore`.

**Alternativa segura:** faça uma PR de restauração a partir da branch de backup, sem force-push. O agendamento periódico pode atualizar os números dos cards mesmo após o rollback; por isso, o retorno é ao layout e às configurações anteriores, e a geração volta a produzir os SVGs correspondentes.

## Pré-merge

1. Confira o README renderizado na branch `feat/profile-identity-refresh`.
2. Confira a geração de `profile/stats.svg` e `profile/streak.svg` no GitHub Actions.
3. Faça merge só se gostar do resultado. Caso contrário, feche a PR e deixe a `main` como está.

## Arquivos afetados

- `banner-v2.svg` — banner editável, sem apagar `banner.png`.
- `README.md` — novo banner e badges.
- `.github/workflows/profile-stats.yml` — títulos e números em branco mais forte.
- `profile/stats.svg` e `profile/streak.svg` — atualizados automaticamente após executar a Action.
