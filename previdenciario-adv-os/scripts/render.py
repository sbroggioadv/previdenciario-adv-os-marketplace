#!/usr/bin/env python3
"""
render.py — Engine de templating + bootstrap do COWORK.

Le cowork-state.json, renderiza templates do plugin, cria estrutura de pastas
e arquivos no <COWORK> do usuario.

Sintaxe de template (Mustache-like simplificada):
    {{VAR}}                           substituicao simples
    {{#SECTION}}...{{/SECTION}}       bloco condicional (renderiza se truthy)
    {{^SECTION}}...{{/SECTION}}       bloco inverso (renderiza se falsy)
    {{#LIST}}...{{.}}...{{/LIST}}     iteracao em lista (item via {{.}})
    {{#OBJ}}...{{field}}...{{/OBJ}}   iteracao em lista de objetos

Uso:
    python scripts/render.py <cowork_path> [--force] [--dry-run]
        Renderiza tudo a partir do state em <cowork_path>/previdenciario/cowork-state.json

    python scripts/render.py <cowork_path> --only persona
        Renderiza apenas a persona

    --force      Sobrescreve persona/MEMORY existentes (por default preserva)
    --dry-run    Mostra o que seria feito, nao escreve

Idempotente: rodar 2x sem --force preserva persona/MEMORY do usuario.
Templates SEMPRE sobrescritos (CLAUDE.md, settings-local.json) — sao gerenciados pelo plugin.
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Importa state.py do mesmo diretorio
sys.path.insert(0, str(Path(__file__).parent))
import state as state_mod  # noqa: E402

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PLUGIN_ROOT / "templates"

# Arquivos preservados (nao sobrescritos sem --force)
USER_OWNED_FILES = {"persona.md", "MEMORY.md"}

# Arquivos sempre regenerados (gerenciados pelo plugin)
PLUGIN_OWNED_FILES = {"CLAUDE.md"}


# ---------------------------------------------------------------------------
# Mini engine de templating (Mustache-like)
# ---------------------------------------------------------------------------

SECTION_RE = re.compile(r"\{\{([#^])([A-Z_][A-Z0-9_]*)\}\}(.*?)\{\{/\2\}\}", re.DOTALL)
VAR_RE = re.compile(r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}")
ITEM_VAR_RE = re.compile(r"\{\{([a-z_][a-z0-9_]*)\}\}")
DOT_RE = re.compile(r"\{\{\.\}\}")


def _is_truthy(v) -> bool:
    if v is None or v is False:
        return False
    if isinstance(v, (str, list, dict)) and len(v) == 0:
        return False
    return True


def _render_section(marker: str, name: str, body: str, ctx: dict) -> str:
    value = ctx.get(name)
    truthy = _is_truthy(value)

    if marker == "^":
        return _render_string(body, ctx) if not truthy else ""

    # marker == "#"
    if not truthy:
        return ""

    # Lista de objetos
    if isinstance(value, list) and value and isinstance(value[0], dict):
        out_parts = []
        for item in value:
            # 1) Substitui {{campo_lowercase}} com valores do item (ANTES do render_string)
            sub = ITEM_VAR_RE.sub(
                lambda m: str(item.get(m.group(1), "")) if item.get(m.group(1)) is not None else "",
                body,
            )
            # 2) Depois resolve vars UPPERCASE via contexto + fields do item (uppercased)
            sub_ctx = {**ctx, **{k.upper(): v for k, v in item.items()}}
            sub = _render_string(sub, sub_ctx)
            out_parts.append(sub)
        return "".join(out_parts)

    # Lista de escalares
    if isinstance(value, list):
        out_parts = []
        for item in value:
            sub = DOT_RE.sub(str(item), body)
            sub = _render_string(sub, ctx)
            out_parts.append(sub)
        return "".join(out_parts)

    # Truthy nao-lista: renderiza body uma vez
    return _render_string(body, ctx)


def _render_string(template: str, ctx: dict) -> str:
    # Resolve sections recursivamente (matches mais externos primeiro)
    while True:
        m = SECTION_RE.search(template)
        if not m:
            break
        marker, name, body = m.group(1), m.group(2), m.group(3)
        rendered = _render_section(marker, name, body, ctx)
        template = template[:m.start()] + rendered + template[m.end():]

    # Resolve variaveis simples
    def _replace_var(m: re.Match) -> str:
        key = m.group(1)
        if key in ctx and not isinstance(ctx[key], (list, dict)):
            v = ctx[key]
            return str(v) if v is not None else ""
        return ""

    template = VAR_RE.sub(_replace_var, template)
    return template


def render_template(template_str: str, ctx: dict) -> str:
    return _render_string(template_str, ctx)


# ---------------------------------------------------------------------------
# Construcao de contexto a partir do state
# ---------------------------------------------------------------------------

def build_context(state: dict, *, area: dict | None = None,
                  scope_name: str | None = None,
                  cowork_path: Path | None = None) -> dict:
    """Constroi dict de contexto para renderizacao."""
    identity = state.get("identity", {})
    tom = state.get("tom_voz", {})
    suprema = state.get("suprema_corte", {})
    prefs = state.get("preferences", {})
    skills = state.get("skills", {})
    cp = cowork_path or Path(state.get("cowork_path", ""))

    ctx: dict = {
        # Identidade
        "FIRM_NAME": identity.get("firm_name", ""),
        "FIRM_SLUG": identity.get("firm_slug", ""),
        "ADVOGADO_NOME": identity.get("advogado_nome", ""),
        "OAB_NUMERO": identity.get("oab_numero") or "",
        "OAB_UF": identity.get("oab_uf") or "",
        "CIDADE": identity.get("cidade") or "",
        "UF": identity.get("uf") or "",
        "EMAIL": identity.get("email") or "",
        "TELEFONE": identity.get("telefone") or "",
        "ENDERECO": identity.get("endereco") or "",
        # Tom de voz
        "TOM_VOZ_PERFIL": tom.get("perfil", "tecnico-combativo"),
        "TOM_VOZ_INTENSIDADE": tom.get("intensidade_combativa", 7),
        "POSTURA_DEFAULT": tom.get("postura_default", ""),
        "EXPRESSOES_ASSINATURA": tom.get("expressoes_assinatura", []),
        "EXPRESSOES_ASSINATURA_LIST": tom.get("expressoes_assinatura", []),
        "TERMOS_A_EVITAR": tom.get("termos_a_evitar", []),
        "TERMOS_A_EVITAR_LIST": tom.get("termos_a_evitar", []),
        # Areas
        "AREAS_LIST": state.get("areas", []),
        # Skills
        "SKILLS_OPT_IN_COUNT": len(skills.get("opt_in_active", [])),
        # Suprema Corte
        "SUPREMA_CORTE_ENABLED": suprema.get("enabled", True),
        "SUPREMA_CORTE_STATUS": "ATIVA" if suprema.get("enabled", True) else "DESATIVADA",
        # Preferences
        "OUTPUT_FORMAT_PREFERIDO": prefs.get("output_format_preferido", "docx"),
        # Meta
        "PLUGIN_VERSION": state.get("plugin_version", "0.1.0-alpha.0"),
        "SCHEMA_VERSION": state.get("schema_version", "1.0.0"),
        "GENERATED_AT": dt.datetime.now(dt.timezone.utc).isoformat(),
        "ANO_VIGENTE": dt.datetime.now().year,
        "COWORK_PATH": str(cp),
        "COWORK_PATH_NORMALIZED": str(cp).replace("\\", "/"),
        "SCOPE_NAME": scope_name or identity.get("firm_name", "Workspace"),
    }

    # Contexto especifico de area
    if area is not None:
        ctx["AREA_SLUG"] = area.get("slug", "")
        ctx["AREA_DISPLAY_NAME"] = area.get("display_name", "")
        ctx["TIPO_ATUACAO"] = area.get("tipo_atuacao", "misto")
        ctx["TIPO_ATUACAO_CONTENCIOSO"] = area.get("tipo_atuacao") == "contencioso"
        ctx["TIPO_ATUACAO_CONSULTIVO"] = area.get("tipo_atuacao") == "consultivo"
        ctx["TIPO_ATUACAO_MISTO"] = area.get("tipo_atuacao") == "misto"
        polo = area.get("polo_predominante")
        ctx["POLO_PREDOMINANTE_AUTOR"] = polo == "autor"
        ctx["POLO_PREDOMINANTE_REU"] = polo == "reu"
        ctx["POLO_PREDOMINANTE_AMBOS"] = polo == "ambos"
        ctx["SUBFOLDERS_LIST"] = area.get("subfolders", ["Clientes", "Processos", "Modelos", "Pesquisas", "Pareceres"])
        ctx["SKILLS_SUGERIDAS_LIST"] = area.get("skills_sugeridas", [])

    return ctx


# ---------------------------------------------------------------------------
# Operacoes de filesystem
# ---------------------------------------------------------------------------

def _write_file(path: Path, content: str, *, dry_run: bool, preserve_user_owned: bool = False) -> str:
    """Escreve arquivo. Respeita --dry-run e preserve flag.

    Retorna:
        'created' / 'updated' / 'preserved' / 'dry-created' / 'dry-updated' / 'dry-preserved'
    """
    exists = path.exists()
    if preserve_user_owned and exists:
        return "dry-preserved" if dry_run else "preserved"

    action = "updated" if exists else "created"
    if dry_run:
        return f"dry-{action}"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return action


def _read_template(name: str) -> str:
    p = TEMPLATES_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Template nao encontrado: {p}")
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def render_persona(state: dict, cowork: Path, *, dry_run: bool, force: bool) -> str:
    tpl = _read_template("persona.md.tpl")
    ctx = build_context(state, cowork_path=cowork)
    rendered = render_template(tpl, ctx)
    target = cowork / "previdenciario" / "persona.md"
    return _write_file(target, rendered, dry_run=dry_run, preserve_user_owned=not force)


def render_cowork_claude(state: dict, cowork: Path, *, dry_run: bool) -> str:
    tpl = _read_template("cowork-CLAUDE.md.tpl")
    ctx = build_context(state, cowork_path=cowork)
    rendered = render_template(tpl, ctx)
    target = cowork / "CLAUDE.md"
    return _write_file(target, rendered, dry_run=dry_run, preserve_user_owned=False)


def render_cowork_memory(state: dict, cowork: Path, *, dry_run: bool, force: bool) -> str:
    tpl = _read_template("MEMORY.md.tpl")
    ctx = build_context(state, cowork_path=cowork, scope_name="Workspace COWORK")
    rendered = render_template(tpl, ctx)
    target = cowork / "MEMORY.md"
    return _write_file(target, rendered, dry_run=dry_run, preserve_user_owned=not force)


def render_areas(state: dict, cowork: Path, *, dry_run: bool, force: bool) -> list[tuple[str, str]]:
    """Renderiza CLAUDE.md + MEMORY.md + subpastas para cada area ativa."""
    results: list[tuple[str, str]] = []
    tpl_claude = _read_template("area-CLAUDE.md.tpl")
    tpl_memory = _read_template("MEMORY.md.tpl")

    for area in state.get("areas", []):
        slug = area.get("slug", "")
        if not slug:
            continue

        area_path = cowork / slug
        ctx = build_context(state, area=area, cowork_path=cowork,
                            scope_name=area.get("display_name", slug))

        # CLAUDE.md da area
        rendered_claude = render_template(tpl_claude, ctx)
        target_claude = area_path / "CLAUDE.md"
        results.append((str(target_claude.relative_to(cowork)),
                        _write_file(target_claude, rendered_claude, dry_run=dry_run, preserve_user_owned=False)))

        # MEMORY.md da area
        rendered_mem = render_template(tpl_memory, ctx)
        target_mem = area_path / "MEMORY.md"
        results.append((str(target_mem.relative_to(cowork)),
                        _write_file(target_mem, rendered_mem, dry_run=dry_run, preserve_user_owned=not force)))

        # Subpastas
        for sub in area.get("subfolders", ["Clientes", "Processos", "Modelos", "Pesquisas", "Pareceres"]):
            sub_path = area_path / sub
            if dry_run:
                results.append((str(sub_path.relative_to(cowork)) + "/", "dry-created" if not sub_path.exists() else "dry-preserved"))
            else:
                sub_path.mkdir(parents=True, exist_ok=True)
                results.append((str(sub_path.relative_to(cowork)) + "/", "ensured"))

    return results


def render_settings_local(state: dict, workspace_path: Path, cowork: Path, *, dry_run: bool) -> str:
    tpl = _read_template("settings-local.json.tpl")
    ctx = build_context(state, cowork_path=cowork)
    rendered = render_template(tpl, ctx)
    target = workspace_path / ".claude" / "settings.local.json"
    return _write_file(target, rendered, dry_run=dry_run, preserve_user_owned=False)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def render_all(cowork: Path, *, dry_run: bool, force: bool, only: str | None,
               workspace_path: Path | None = None) -> dict:
    """Renderiza tudo. Retorna relatorio."""
    state = state_mod.load(cowork)
    report: dict[str, list[tuple[str, str]] | str] = {}

    if only in (None, "persona"):
        report["persona.md"] = render_persona(state, cowork, dry_run=dry_run, force=force)

    if only in (None, "cowork-claude"):
        report["CLAUDE.md"] = render_cowork_claude(state, cowork, dry_run=dry_run)

    if only in (None, "cowork-memory"):
        report["MEMORY.md"] = render_cowork_memory(state, cowork, dry_run=dry_run, force=force)

    if only in (None, "areas"):
        report["areas"] = render_areas(state, cowork, dry_run=dry_run, force=force)

    if only in (None, "settings") and workspace_path:
        report[".claude/settings.local.json"] = render_settings_local(
            state, workspace_path, cowork, dry_run=dry_run
        )

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Render templates do plugin contra cowork-state.json")
    parser.add_argument("cowork_path", help="Path do COWORK do usuario")
    parser.add_argument("--workspace", help="Path do workspace Claude Code (para settings.local.json)")
    parser.add_argument("--force", action="store_true", help="Sobrescreve persona/MEMORY existentes")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que seria feito, nao escreve")
    parser.add_argument("--only", choices=["persona", "cowork-claude", "cowork-memory", "areas", "settings"],
                        help="Renderiza apenas o componente especificado")
    args = parser.parse_args()

    cowork = Path(args.cowork_path).resolve()
    workspace = Path(args.workspace).resolve() if args.workspace else None

    if not cowork.exists():
        print(f"ERRO: COWORK path nao existe: {cowork}", file=sys.stderr)
        return 1

    try:
        report = render_all(cowork, dry_run=args.dry_run, force=args.force,
                            only=args.only, workspace_path=workspace)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1

    print(f"Render {'(dry-run) ' if args.dry_run else ''}contra {cowork}")
    print()
    for key, value in report.items():
        if isinstance(value, list):
            print(f"  {key}:")
            for path, status in value:
                print(f"    [{status}] {path}")
        else:
            print(f"  [{value}] {key}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
