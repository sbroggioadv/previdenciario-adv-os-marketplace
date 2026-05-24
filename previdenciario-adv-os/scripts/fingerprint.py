#!/usr/bin/env python3
"""
fingerprint.py — Calcula e compara fingerprints das skills/scripts/templates do plugin.

Uso pela skill `cowork-sync` para detectar divergencia multi-dispositivo.

Comandos:
  --out -                           imprime fingerprint atual (markdown) em stdout
  --update-auto-deploy              escreve/atualiza <COWORK>/previdenciario/AUTO-DEPLOY.md
  --diff                            compara baseline vs atual, imprime JSON

Requer:
  --plugin-root <path>              raiz do plugin instalado
  --cowork <path>                   (para update-auto-deploy e diff) path do COWORK

Zero dependencias externas — stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import platform
import re
import socket
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

AUTO_DEPLOY_FILENAME = "AUTO-DEPLOY.md"
STATE_DIR = "previdenciario"


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_file(p: Path) -> tuple[str, int]:
    """Retorna (sha256_8chars, size_bytes)."""
    h = hashlib.sha256()
    size = 0
    with p.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest()[:8], size


def _collect(plugin_root: Path) -> dict:
    """Percorre skills/, scripts/, templates/ e calcula fingerprint de cada .md/.py/.tpl/.json."""
    result: dict[str, list[dict]] = {"skills": [], "scripts": [], "templates": []}

    skills_dir = plugin_root / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                sha, size = _hash_file(skill_md)
                result["skills"].append({"name": skill_dir.name, "sha": sha, "bytes": size})

    scripts_dir = plugin_root / "scripts"
    if scripts_dir.is_dir():
        for p in sorted(scripts_dir.iterdir()):
            if p.is_file() and p.suffix in {".py", ".json", ".sh"} and not p.name.startswith("__"):
                sha, size = _hash_file(p)
                result["scripts"].append({"name": p.name, "sha": sha, "bytes": size})

    templates_dir = plugin_root / "templates"
    if templates_dir.is_dir():
        for p in sorted(templates_dir.iterdir()):
            if p.is_file():
                sha, size = _hash_file(p)
                result["templates"].append({"name": p.name, "sha": sha, "bytes": size})

    return result


def _read_plugin_version(plugin_root: Path) -> str:
    manifest = plugin_root / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        return "unknown"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        return data.get("version", "unknown")
    except Exception:
        return "unknown"


def _render_markdown(fp: dict, plugin_root: Path) -> str:
    plugin_version = _read_plugin_version(plugin_root)
    lines: list[str] = []
    lines.append("# AUTO-DEPLOY — Fingerprint do Plugin")
    lines.append("")
    lines.append("> Snapshot das skills, scripts e templates instalados no momento da ultima operacao bem-sucedida.")
    lines.append("> Gerado automaticamente pelo plugin. NAO editar manualmente.")
    lines.append("")
    lines.append(f"**Plugin versao:** {plugin_version}")
    lines.append(f"**Gerado em:** {_now_iso()}")
    lines.append(f"**Maquina:** {socket.gethostname()}")
    lines.append(f"**Sistema:** {platform.system().lower()} {platform.release()}")
    lines.append("")

    for section, title in [("skills", "Skills"), ("scripts", "Scripts"), ("templates", "Templates")]:
        items = fp.get(section, [])
        if not items:
            continue
        lines.append(f"## {title}")
        lines.append("")
        lines.append("| Item | SHA256 (8 chars) | Bytes |")
        lines.append("|---|---|---|")
        for item in items:
            lines.append(f"| {item['name']} | `{item['sha']}` | {item['bytes']} |")
        lines.append("")

    return "\n".join(lines) + "\n"


_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*`([0-9a-f]{8})`\s*\|\s*(\d+)\s*\|$")


def _parse_auto_deploy(text: str) -> dict:
    """Parse markdown de AUTO-DEPLOY.md e retorna estrutura equivalente a _collect()."""
    result: dict = {"skills": [], "scripts": [], "templates": [], "generated_at": None}

    gen_m = re.search(r"\*\*Gerado em:\*\*\s*([^\s]+)", text)
    if gen_m:
        result["generated_at"] = gen_m.group(1)

    current_section = None
    section_map = {"Skills": "skills", "Scripts": "scripts", "Templates": "templates"}

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            current_section = section_map.get(heading)
            continue
        if current_section is None:
            continue
        m = _ROW_RE.match(stripped)
        if m:
            name, sha, size_s = m.groups()
            result[current_section].append({"name": name, "sha": sha, "bytes": int(size_s)})

    return result


def _diff(baseline: dict, current: dict) -> dict:
    """Diff estruturado entre baseline e current."""
    diff = {
        "baseline_generated_at": baseline.get("generated_at"),
        "current_at": _now_iso(),
        "modified": [],
        "added": [],
        "removed": [],
    }
    for section in ("skills", "scripts", "templates"):
        bl = {item["name"]: item for item in baseline.get(section, [])}
        cur = {item["name"]: item for item in current.get(section, [])}

        for name, c in cur.items():
            if name not in bl:
                diff["added"].append({"item": name, "type": section, "current_sha": c["sha"]})
            elif bl[name]["sha"] != c["sha"]:
                diff["modified"].append({
                    "item": name,
                    "type": section,
                    "baseline_sha": bl[name]["sha"],
                    "current_sha": c["sha"],
                })
        for name, b in bl.items():
            if name not in cur:
                diff["removed"].append({"item": name, "type": section, "baseline_sha": b["sha"]})
    return diff


def _cmd_print(plugin_root: Path) -> int:
    fp = _collect(plugin_root)
    sys.stdout.write(_render_markdown(fp, plugin_root))
    return 0


def _cmd_update(plugin_root: Path, cowork: Path) -> int:
    fp = _collect(plugin_root)
    target = cowork / STATE_DIR / AUTO_DEPLOY_FILENAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_markdown(fp, plugin_root), encoding="utf-8")
    sys.stdout.write(f"OK: AUTO-DEPLOY.md atualizado em {target}\n")
    return 0


def _cmd_diff(plugin_root: Path, cowork: Path) -> int:
    baseline_path = cowork / STATE_DIR / AUTO_DEPLOY_FILENAME
    current = _collect(plugin_root)
    if not baseline_path.exists():
        diff_result = {
            "baseline_generated_at": None,
            "current_at": _now_iso(),
            "added": [{"item": i["name"], "type": sec, "current_sha": i["sha"]}
                      for sec in ("skills", "scripts", "templates")
                      for i in current.get(sec, [])],
            "modified": [],
            "removed": [],
            "note": "Sem baseline AUTO-DEPLOY.md. Todos os itens tratados como ADICIONADOS.",
        }
    else:
        baseline = _parse_auto_deploy(baseline_path.read_text(encoding="utf-8"))
        diff_result = _diff(baseline, current)
    sys.stdout.write(json.dumps(diff_result, indent=2, ensure_ascii=False) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fingerprint do plugin (multi-dispositivo).")
    parser.add_argument("--plugin-root", required=True, type=Path, help="Raiz do plugin instalado.")
    parser.add_argument("--cowork", type=Path, help="Path do COWORK (para update-auto-deploy e diff).")
    parser.add_argument("--out", help="'-' para imprimir markdown do fingerprint atual em stdout.")
    parser.add_argument("--update-auto-deploy", action="store_true",
                        help="Atualiza <cowork>/previdenciario/AUTO-DEPLOY.md com fingerprint atual.")
    parser.add_argument("--diff", action="store_true",
                        help="Compara baseline AUTO-DEPLOY.md com fingerprint atual; imprime JSON.")

    args = parser.parse_args(argv)

    plugin_root = args.plugin_root.resolve()
    if not plugin_root.is_dir():
        sys.stderr.write(f"ERRO: plugin-root nao encontrado: {plugin_root}\n")
        return 2

    if args.out == "-":
        return _cmd_print(plugin_root)
    if args.update_auto_deploy:
        if not args.cowork:
            sys.stderr.write("ERRO: --update-auto-deploy requer --cowork.\n")
            return 2
        return _cmd_update(plugin_root, args.cowork.resolve())
    if args.diff:
        if not args.cowork:
            sys.stderr.write("ERRO: --diff requer --cowork.\n")
            return 2
        return _cmd_diff(plugin_root, args.cowork.resolve())

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
