#!/usr/bin/env python3
"""
apply-unicode-whitelist.py — Substitui caracteres unicode nao-suportados pelo
Claude Cowork por equivalentes seguros.

Fecha pendencia do COWORK-PUBLISHING-GUIDE.md.

Caracteres OK no Cowork (descobertos via teste empirico):
- Acentos PT-BR: ã ç é ê í ó º
- Box drawing simples: ┌ ─ ┐ │ ├ ┤ └ ┘
- Em-dash: —
- Setas: → ↓
- Box symbols: □ ►
- Emojis: ✅ ✓ ❌ ⚠ 🔴 🟡 🟢

Caracteres com SUSPEITA (substituir antes de zipar):
- Box drawing duplo: ╔ ╗ ╚ ╝ ╠ ╣ ║ ═ -> simples
- Simbolos decorativos: ▼ ✗ × · § ★ ◆ … – "" ''
- Tipograficos: aspas curvas, traços longos
- Emojis "deprecated" 1F XXXX

Uso:
    python3 apply-unicode-whitelist.py <diretorio>   # in-place
    python3 apply-unicode-whitelist.py <dir> --dry-run   # so reporta
    python3 apply-unicode-whitelist.py --check-deps   # so verifica

Stdlib only.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path


# Mapeamento: char suspeito -> char seguro
WHITELIST_REPLACEMENTS = {
    # Box drawing duplos -> simples
    '╔': '┌', '╗': '┐', '╚': '└', '╝': '┘',
    '╠': '├', '╣': '┤', '╦': '┬', '╩': '┴', '╬': '┼',
    '║': '│', '═': '─',
    # Tipografia decorativa (em-dash — e OK no Cowork por teste empirico — NAO substituir)
    '…': '...',
    '–': '-',
    # '—' permanece — testado e funciona no Cowork
    # Aspas tipograficas (U+201C/D e U+2018/19) — substituir por normais
    '“': '"', '”': '"',  # LEFT/RIGHT DOUBLE QUOTATION MARK
    '‘': "'", '’': "'",  # LEFT/RIGHT SINGLE QUOTATION MARK
    '«': '"', '»': '"',  # « » Guillemets
    # Simbolos varios
    '▼': 'v',
    '✗': 'X', '×': 'x',
    '★': '*', '☆': '*',
    '◆': '*', '◇': '*',
    '·': '-',
    '§': 'S',
    '°': 'o',
    # Setas alternativas
    '⇒': '->', '⇐': '<-', '⇔': '<->',
    '⟶': '->', '⟵': '<-',
    # Espacos especiais
    ' ': ' ',  # non-breaking space
    '​': '',   # zero-width space
    '‎': '',   # left-to-right mark
    '‏': '',   # right-to-left mark
    '﻿': '',   # BOM
}


def apply_whitelist(content: str) -> tuple[str, dict]:
    """
    Aplica substituicoes na string. Retorna (nova_string, stats_dict).
    """
    stats = {}
    for old, new in WHITELIST_REPLACEMENTS.items():
        if old == new:
            continue  # guard: no-op, evita falso positivo no count
        count = content.count(old)
        if count > 0:
            stats[old] = count
            content = content.replace(old, new)
    return content, stats


def scan_file(path: Path, dry_run: bool = False) -> dict:
    """
    Scaneia arquivo e (se nao dry_run) substitui caracteres.
    Returns: { 'path', 'changes': {char: count}, 'modified': bool }
    """
    try:
        original = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return {'path': str(path), 'changes': {}, 'modified': False, 'error': 'nao-utf8'}

    new_content, stats = apply_whitelist(original)
    modified = bool(stats)

    if modified and not dry_run:
        path.write_text(new_content, encoding='utf-8')

    return {'path': str(path), 'changes': stats, 'modified': modified}


def find_target_files(root: Path) -> list[Path]:
    """Encontra .md, .json, .yaml, .yml, .txt em root recursivamente.
    Pula .git/, node_modules/, _archived/, audit/."""
    targets = []
    SKIP_DIRS = {'.git', 'node_modules', '_archived', 'audit'}
    EXTENSIONS = ('*.md', '*.json', '*.yml', '*.yaml', '*.txt')
    for ext in EXTENSIONS:
        for p in root.rglob(ext):
            parts_lower = {part.lower() for part in p.parts}
            if parts_lower & SKIP_DIRS:
                continue
            targets.append(p)
    return sorted(set(targets))


def main() -> int:
    parser = argparse.ArgumentParser(description="Aplica unicode whitelist em arquivos do build Cowork.")
    parser.add_argument("path", nargs="?", help="Diretorio root para processar (default: cwd)")
    parser.add_argument("--dry-run", action="store_true", help="So reporta, nao modifica")
    parser.add_argument("--check-deps", action="store_true", help="Verifica deps (stdlib only — sempre OK)")
    args = parser.parse_args()

    if args.check_deps:
        print("Deps: stdlib only — OK")
        return 0

    root = Path(args.path if args.path else '.').resolve()
    if not root.exists():
        print(f"Erro: {root} nao existe", file=sys.stderr)
        return 1

    files = find_target_files(root)
    print(f"Processando {len(files)} arquivos em {root}", file=sys.stderr)

    total_modified = 0
    total_changes = 0
    all_chars = {}

    for f in files:
        result = scan_file(f, dry_run=args.dry_run)
        if result.get('modified'):
            total_modified += 1
            rel = f.relative_to(root)
            for char, count in result['changes'].items():
                total_changes += count
                all_chars[char] = all_chars.get(char, 0) + count
            char_summary = ", ".join(f"'{c}'x{n}" for c, n in result['changes'].items())
            print(f"  [{'DRY' if args.dry_run else 'OK '}] {rel}: {char_summary}")

    if total_modified == 0:
        print("\nNenhum caractere suspeito encontrado — build Cowork-safe.", file=sys.stderr)
        return 0

    print(f"\nResumo:", file=sys.stderr)
    print(f"  Arquivos modificados: {total_modified}", file=sys.stderr)
    print(f"  Substituicoes totais: {total_changes}", file=sys.stderr)
    print(f"  Caracteres processados:", file=sys.stderr)
    for char, count in sorted(all_chars.items(), key=lambda x: -x[1]):
        codepoint = f"U+{ord(char):04X}"
        replacement = WHITELIST_REPLACEMENTS.get(char, "?")
        print(f"    '{char}' ({codepoint}) -> '{replacement}': {count}x", file=sys.stderr)

    if args.dry_run:
        print(f"\nDRY RUN — nenhum arquivo foi modificado. Rode sem --dry-run para aplicar.", file=sys.stderr)
    else:
        print(f"\nAplicado com sucesso. Build pode prosseguir.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
