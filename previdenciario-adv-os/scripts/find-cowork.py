#!/usr/bin/env python3
"""
find-cowork.py — Descobre o COWORK path ativo via fallback chain.

Usado pelos comandos /cowork-* para saber onde esta o state do usuario.

Ordem:
1. Arg posicional se fornecido
2. Env var COWORK_PATH
3. <CWD>/previdenciario/cowork-state.json (subindo ate 5 niveis)
4. <CWD>/.claude/settings.local.json campo env.COWORK_PATH
5. ~/.config/previdenciario-adv-os/active-cowork.json campo cowork_path

Imprime o path em stdout. Exit 1 se nao encontrar.

Uso:
    python scripts/find-cowork.py              # busca
    python scripts/find-cowork.py /path/to/cw  # valida o path fornecido
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _has_state(p: Path) -> bool:
    return (p / "previdenciario" / "cowork-state.json").exists()


def _try_arg() -> Path | None:
    if len(sys.argv) > 1:
        p = Path(sys.argv[1]).expanduser().resolve()
        if _has_state(p):
            return p
    return None


def _try_env() -> Path | None:
    v = os.environ.get("COWORK_PATH")
    if v:
        p = Path(v).expanduser().resolve()
        if _has_state(p):
            return p
    return None


def _try_cwd_upward() -> Path | None:
    cwd = Path.cwd()
    for _ in range(6):
        if _has_state(cwd):
            return cwd
        if cwd.parent == cwd:
            break
        cwd = cwd.parent
    return None


def _try_settings_local() -> Path | None:
    cwd = Path.cwd()
    for _ in range(6):
        s = cwd / ".claude" / "settings.local.json"
        if s.exists():
            try:
                data = json.loads(s.read_text(encoding="utf-8"))
                env = data.get("env", {}) if isinstance(data, dict) else {}
                v = env.get("COWORK_PATH")
                if v:
                    p = Path(v).expanduser().resolve()
                    if _has_state(p):
                        return p
            except (json.JSONDecodeError, PermissionError):
                pass
        if cwd.parent == cwd:
            break
        cwd = cwd.parent
    return None


def _try_active_cowork() -> Path | None:
    for cfg in (
        Path.home() / ".config" / "previdenciario-adv-os" / "active-cowork.json",
        Path.home() / ".previdenciario-adv-os" / "active-cowork.json",
    ):
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
                v = data.get("cowork_path")
                if v:
                    p = Path(v).expanduser().resolve()
                    if _has_state(p):
                        return p
            except (json.JSONDecodeError, PermissionError):
                pass
    return None


def find_cowork() -> tuple[Path | None, str]:
    for fn, tag in (
        (_try_arg, "arg"),
        (_try_env, "env:COWORK_PATH"),
        (_try_cwd_upward, "cwd_upward"),
        (_try_settings_local, "settings.local.json"),
        (_try_active_cowork, "active-cowork.json"),
    ):
        try:
            p = fn()
            if p:
                return p, tag
        except Exception:
            continue
    return None, ""


def main() -> int:
    path, source = find_cowork()
    if path is None:
        print("", end="")
        sys.stderr.write("ERRO: COWORK nao encontrado. Rode /start para configurar.\n")
        return 1
    print(str(path))
    sys.stderr.write(f"[find-cowork] fonte: {source}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
