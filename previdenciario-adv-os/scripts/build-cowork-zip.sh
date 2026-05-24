#!/usr/bin/env bash
# build-cowork-zip.sh — Pipeline idempotente de empacotamento para Claude Cowork.
#
# Gera um ZIP Cowork-compatible (somente .claude-plugin/ + skills/) a partir
# da raiz do plugin atual. Roda validacoes hard ANTES de zipar:
#   1. apply-unicode-whitelist.py (substitui chars nao suportados)
#   2. check-skill-descriptions.py (limites + colisao com plugin pai)
#   3. validate-cowork-zip.py     (guardrail final pos-zip)
#
# Falha rapida em qualquer erro; nada e enviado pra dist/ sem aprovacao.
#
# USO:
#   bash scripts/build-cowork-zip.sh --version 0.1.0-alpha.2
#   bash scripts/build-cowork-zip.sh --version 0.1.0-alpha.2 --skip-unicode
#   bash scripts/build-cowork-zip.sh --version 0.1.0-alpha.2 --keep-build
#
# OUTPUT:
#   dist/<PluginName>-cowork-v<version>.zip

set -euo pipefail

# ---- argumentos ---------------------------------------------------------

VERSION=""
SKIP_UNICODE=0
KEEP_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="${2:-}"; shift 2 ;;
    --skip-unicode) SKIP_UNICODE=1; shift ;;
    --keep-build) KEEP_BUILD=1; shift ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//' | head -25
      exit 0
      ;;
    *)
      echo "ERRO: argumento desconhecido: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$VERSION" ]]; then
  echo "ERRO: --version <semver> e obrigatorio (ex: 0.1.0-alpha.2)" >&2
  exit 2
fi

# ---- detecta raiz do plugin --------------------------------------------

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PLUGIN_ROOT"

if [[ ! -f ".claude-plugin/plugin.json" ]]; then
  echo "ERRO: .claude-plugin/plugin.json nao encontrado em $PLUGIN_ROOT" >&2
  exit 2
fi

if [[ ! -d "skills" ]]; then
  echo "ERRO: pasta skills/ nao encontrada em $PLUGIN_ROOT" >&2
  exit 2
fi

# ---- nome do plugin (pra nome do zip) ----------------------------------

PLUGIN_BASENAME="$(basename "$PLUGIN_ROOT")"
# Convencao do workspace: pasta basename pode estar em kebab-case (plugin-marketing)
# ou em PascalCase (Plugin-Previdenciario-Adv-OS). Pra zip name canonico,
# capitalizar cada segmento e padronizar pra `Plugin-<Nome>-Adv-OS` se nao seguir.
# Regra simples: se ja comeca com "Plugin-", mantem; senao, capitaliza e prefixa.
case "$PLUGIN_BASENAME" in
  Plugin-*) ZIP_BASENAME="$PLUGIN_BASENAME" ;;
  plugin-marketing)         ZIP_BASENAME="Plugin-Marketing-Adv-OS" ;;
  plugin-previdenciario)    ZIP_BASENAME="Plugin-Previdenciario-Adv-OS" ;;
  plugin-*)
    # Auto-capitaliza: plugin-foo-bar -> Plugin-Foo-Bar-Adv-OS
    rest="${PLUGIN_BASENAME#plugin-}"
    cap=""
    IFS='-' read -ra parts <<< "$rest"
    for p in "${parts[@]}"; do
      cap+="-$(echo "$p" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')"
    done
    ZIP_BASENAME="Plugin${cap}-Adv-OS"
    ;;
  *) ZIP_BASENAME="$PLUGIN_BASENAME" ;;
esac
ZIP_NAME="${ZIP_BASENAME}-cowork-v${VERSION}.zip"

# ---- diretorio de build temporario -------------------------------------

BUILD_DIR="$(mktemp -d -t cowork-build-XXXXXX)"
trap 'if [[ "$KEEP_BUILD" -eq 0 ]]; then rm -rf "$BUILD_DIR"; fi' EXIT

echo "==> Build dir: $BUILD_DIR"
echo "==> Plugin root: $PLUGIN_ROOT"
echo "==> Version: $VERSION"
echo "==> Zip name: $ZIP_NAME"
echo

# ---- 1. Copiar artefatos para build ------------------------------------

echo "==> [1/6] Copiando .claude-plugin + skills (excluindo _archived/DS_Store)"
mkdir -p "$BUILD_DIR/.claude-plugin"
cp .claude-plugin/plugin.json "$BUILD_DIR/.claude-plugin/plugin.json"

# rsync se disponivel, fallback pra cp
if command -v rsync >/dev/null 2>&1; then
  rsync -a \
    --exclude '_archived' \
    --exclude '.DS_Store' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    skills/ "$BUILD_DIR/skills/"
else
  cp -R skills "$BUILD_DIR/skills"
  find "$BUILD_DIR/skills" -name '_archived' -type d -prune -exec rm -rf {} + 2>/dev/null || true
fi

# Limpar artefatos macOS residuais (defesa em profundidade)
find "$BUILD_DIR" -name '.DS_Store' -delete 2>/dev/null || true
find "$BUILD_DIR" -name '__MACOSX' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name '*.pyc' -delete 2>/dev/null || true
find "$BUILD_DIR" -name '*.swp' -delete 2>/dev/null || true
find "$BUILD_DIR" -name '.gitkeep' -delete 2>/dev/null || true

# ---- 2. Aplicar whitelist unicode --------------------------------------

if [[ "$SKIP_UNICODE" -eq 0 ]]; then
  echo "==> [2/6] Aplicando whitelist unicode"
  if [[ -f "scripts/apply-unicode-whitelist.py" ]]; then
    python3 scripts/apply-unicode-whitelist.py "$BUILD_DIR"
  else
    echo "    AVISO: scripts/apply-unicode-whitelist.py nao encontrado — pulando"
  fi
else
  echo "==> [2/6] Whitelist unicode PULADA (--skip-unicode)"
fi

# ---- 3. Validar descriptions/sizes/colisoes (no build dir) -------------

echo "==> [3/6] Validando descriptions/sizes/colisoes (no build dir)"
# Roda o check com SKILLS_DIR override no build (mais seguro que rodar em prod)
if [[ -f "scripts/check-skill-descriptions.py" ]]; then
  # cria copia temporaria do script apontando pra build/skills
  TMPCHECK="$BUILD_DIR/.check-skill-descriptions.py"
  sed "s|SKILLS_DIR = Path(__file__).resolve().parent.parent / \"skills\"|SKILLS_DIR = Path(\"$BUILD_DIR/skills\")|" \
    scripts/check-skill-descriptions.py > "$TMPCHECK"
  python3 "$TMPCHECK" || { echo "ERRO: check-skill-descriptions falhou" >&2; exit 1; }
  rm -f "$TMPCHECK"
else
  echo "    AVISO: scripts/check-skill-descriptions.py nao encontrado — pulando"
fi

# ---- 4. Sanitizar plugin.json (3 campos canonicos) ---------------------

echo "==> [4/6] Sanitizando plugin.json (apenas name/version/description)"
python3 - <<PYEOF
import json, sys
from pathlib import Path

src = Path("$BUILD_DIR/.claude-plugin/plugin.json")
data = json.loads(src.read_text(encoding="utf-8"))

# Apenas os 3 campos minimos aceitos consistentemente pelo Cowork
keep = {}
for k in ("name", "version", "description"):
    if k not in data:
        print(f"ERRO: plugin.json esta faltando campo obrigatorio: {k}", file=sys.stderr)
        sys.exit(1)
    keep[k] = data[k]

# Forca a version do CLI (sobrescreve o que estiver no arquivo)
keep["version"] = "$VERSION"

# Validacoes hard:
name = keep["name"]
import re
if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
    print(f"ERRO: plugin.name '{name}' fora do regex kebab-case", file=sys.stderr)
    sys.exit(1)
if len(name) > 64:
    print(f"ERRO: plugin.name '{name}' excede 64 chars", file=sys.stderr)
    sys.exit(1)
if len(keep["description"]) > 1024:
    print(f"ERRO: plugin.description excede 1024 chars ({len(keep['description'])})", file=sys.stderr)
    sys.exit(1)

src.write_text(json.dumps(keep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"    OK: name={name} version={keep['version']} desc={len(keep['description'])}c")
PYEOF

# ---- 5. Zipar a partir da raiz do build --------------------------------

echo "==> [5/6] Gerando ZIP"
mkdir -p dist
ZIP_PATH="$PLUGIN_ROOT/dist/$ZIP_NAME"
rm -f "$ZIP_PATH"

# Zipar a partir DENTRO do build (paths relativos sem prefixo de pasta)
( cd "$BUILD_DIR" && zip -rq "$ZIP_PATH" . \
    -x "*.DS_Store" "*/__pycache__/*" "*.pyc" "__MACOSX/*" )

ZIP_SIZE=$(stat -f%z "$ZIP_PATH" 2>/dev/null || stat -c%s "$ZIP_PATH")
ZIP_FILES=$(unzip -l "$ZIP_PATH" | tail -1 | awk '{print $2}')

echo "    OK: $ZIP_PATH ($ZIP_SIZE bytes, $ZIP_FILES entries)"

# ---- 6. Guardrail final: validate-cowork-zip.py ------------------------

echo "==> [6/6] Validacao final do ZIP gerado"
if [[ -f "scripts/validate-cowork-zip.py" ]]; then
  python3 scripts/validate-cowork-zip.py "$ZIP_PATH" || {
    echo "ERRO: validate-cowork-zip.py reprovou o ZIP gerado" >&2
    echo "    ZIP mantido em $ZIP_PATH para inspecao" >&2
    exit 1
  }
else
  echo "    AVISO: scripts/validate-cowork-zip.py nao encontrado — pulando guardrail"
fi

echo
echo "OK: build concluido"
echo "    Path: $ZIP_PATH"
echo "    Size: $ZIP_SIZE bytes"
echo "    Files: $ZIP_FILES"
echo
echo "Proximos passos manuais no Cowork:"
echo "  1. Apagar versao anterior do plugin (UI Cowork) se existir"
echo "  2. Upload do ZIP gerado"
echo "  3. Verificar plugin instalado + skills disponiveis"
