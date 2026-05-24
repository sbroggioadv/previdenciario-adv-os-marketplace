#!/usr/bin/env python3
"""
despersonalize.py — Substituições em massa para neutralizar identificadores pessoais.

Aplica regras de substituição (ordenadas por especificidade) a todos os arquivos
.md em .planning/, .skills/, .commands/, etc. (exceto audit/, .git/, _sandbox/).

Uso:
    python scripts/despersonalize.py          # aplica e mostra diff sumario
    python scripts/despersonalize.py --dry    # so mostra o que seria mudado
    python scripts/despersonalize.py --check  # exit 1 se algum arquivo precisaria mudar

Substituicoes sao ordenadas: longas/especificas PRIMEIRO, genericas DEPOIS,
para evitar shadowing (ex: "Dr. Luis Sbroggio" antes de "Sbroggio").
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Linhas que matcham qualquer padrao abaixo NAO sao tocadas.
# Preserva URLs do GitHub do workspace de publicacao (autorizado).
WHITELIST_LINE_PATTERNS = [
    re.compile(r"https?://github\.com/sbroggioadv/Plugin-Ia-Combativa-Adv-OS"),
    re.compile(r"sbroggioadv/Plugin-Ia-Combativa-Adv-OS"),
]


def is_whitelisted(line: str) -> bool:
    return any(p.search(line) for p in WHITELIST_LINE_PATTERNS)


# Substituicoes ordenadas: (regex, replacement). Mais especificas primeiro.
SUBSTITUTIONS: list[tuple[str, str]] = [
    # ------ Identidade pessoal completa (LONGAS PRIMEIRO) ------
    (r"Dr\. Luis Augusto Sbroggio Lacanna", "Mentor"),
    (r"Luis Augusto Sbroggio Lacanna", "Mentor"),
    (r"Dr\. Luis Sbroggio", "Mentor"),
    (r"Doc Luis Sbroggio", "Mentor"),
    (r"Luis Sbroggio", "Mentor"),
    (r"Sbroggio Lacanna", "Mentor"),
    (r"Dr\. Luis", "Mentor"),
    (r"Luis Augusto", "Mentor"),
    (r"\bLacanna\b", ""),
    (r"\bLuis\b", "Mentor"),

    # ------ Escritorio ------
    (r"Sbroggio Advocacia Empresarial e Franchising", "Escritorio de Referencia"),
    (r"Sbroggio Advocacia Empresarial", "Escritorio de Referencia"),
    (r"Sbroggio Advocacia", "Escritorio de Referencia"),

    # ------ OAB ------
    (r"OAB/SP\s*323\.065", "OAB do Mentor"),
    (r"OAB/SP\s*323065", "OAB do Mentor"),
    (r"OAB\s*323\.065", "OAB do Mentor"),
    (r"\b323\.065\b", "[REDACTED]"),
    (r"\b323065\b", "[REDACTED]"),
    (r"\(OAB/SP\s*323[^\)]*\)", ""),

    # ------ Email ------
    (r"sbroggioadv@gmail\.com", "[contato Mentoria Ia Combativa]"),
    (r"@sbroggio\.com\.br", "@[dominio-do-escritorio]"),

    # ------ Apelidos pessoais ------
    # Word-boundary catch-all (vai depois das regras especificas para nao quebrar substituicoes contextuais)
    (r"\bdo Doc\b", "do Mentor"),
    (r"\bao Doc\b", "ao Mentor"),
    (r"\bpelo Doc\b", "pelo Mentor"),
    (r"\bcom o Doc\b", "com o Mentor"),
    (r"\bo Doc\b", "o Mentor"),
    (r"\bDoc disse\b", "Mentor decidiu"),
    (r"\bDoc decidiu\b", "Mentor decidiu"),
    (r"\bDoc autorizou\b", "Mentor autorizou"),
    (r"\bDoc precisa\b", "Mentor precisa"),
    (r"\bDoc quer\b", "Mentor quer"),
    (r"\bDoc validar\b", "Mentor validar"),
    (r"\bDoc revisa\b", "Mentor revisa"),
    (r"\bDoc responde\b", "Mentor responde"),
    (r"\bDoc aprovar\b", "Mentor aprovar"),
    (r"\bDoc aprov\b", "Mentor aprov"),
    (r"\bDoc indicar\b", "Mentor indicar"),
    (r"\bDoc evolu\b", "Mentor evolu"),
    (r"\bDoc valida\b", "Mentor valida"),
    (r"\bDoc usar?\b", "Mentor usar"),
    (r"\bDoc usa\b", "Mentor usa"),
    (r"\bDoc autoriza\b", "Mentor autoriza"),
    (r"\bDoc estar\b", "Mentor estar"),
    (r"\bDoc cobre\b", "Mentor cobre"),
    (r"\bDoc roda\b", "Mentor roda"),
    (r"\bDoc \\xc3\\xa9\b", "Mentor é"),
    (r"\bDoc é\b", "Mentor é"),
    (r"\bDoc tem\b", "Mentor tem"),
    (r"\bDoc fez\b", "Mentor fez"),
    (r"\bDoc faz\b", "Mentor faz"),
    (r"\bDoc fala\b", "Mentor fala"),
    (r"\bDoc + \d", "Mentor + 1"),
    (r"\bao \"Doc\"\b", "ao Mentor"),
    (r"\bdo \"Doc\"\b", "do Mentor"),
    (r"\(Doc\)", "(Mentor)"),
    (r"^Doc,", "Mentor,"),
    (r"\nDoc,", "\nMentor,"),
    # CATCH-ALL de "Doc" como palavra
    (r"\bDoc\b", "Mentor"),

    # ------ Handles e usernames ------
    (r"luissbroggio", "[handle-mentor]"),
    (r"@luissbroggio", "[handle-mentor]"),

    # ------ Org/usernames sbroggio ------
    (r"\bsbroggioadv\b", "[org-mentor]"),
    (r"\bSbroggioadv\b", "[org-mentor]"),

    # ------ Padroes proprietarios nomeados ------
    (r"Padrao Sbroggio", "Padrao do Escritorio"),
    (r"Padrão Sbroggio", "Padrão do Escritório"),
    (r"Padrao Doc", "Padrao do Escritorio"),
    (r"Padrão Doc", "Padrão do Escritório"),
    (r"padrao sbroggio", "padrao do escritorio"),
    (r"padrão sbroggio", "padrão do escritório"),
    (r"PADRAO_SBROGGIO", "PADRAO_ESCRITORIO"),
    (r"TOM_VOZ_PADRAO_SBROGGIO", "TOM_VOZ_PADRAO_ESCRITORIO"),
    (r"LAYOUT_NOVO_2026_FINAL_-_SBROGGIO_DEFINITIVO", "LAYOUT_TEMPLATE_NEUTRO"),

    # ------ Plugins/skills com nome proprio ------
    (r"sbroggio-claude-agents", "arsenal de referencia"),
    (r"PLUGINS-FONTE/sbroggio-adv", "<PLUGIN_FONTE>"),
    (r"PLUGINS-FONTE/sbroggio-contabil", "<PLUGIN_CONTABIL_FONTE>"),
    (r"sbroggio-adv\.plugin", "<plugin-fonte>.plugin"),
    (r"sbroggio-contabil\.plugin", "<plugin-contabil-fonte>.plugin"),
    (r"`sbroggio-adv`", "`<plugin-fonte>`"),
    (r"`sbroggio-contabil`", "`<plugin-contabil-fonte>`"),
    (r"sbroggio-adv", "<plugin-fonte>"),
    (r"sbroggio-contabil", "<plugin-contabil-fonte>"),
    (r"sbroggio-master", "firm-master"),
    (r"-sbroggio\b", ""),
    (r"_sbroggio\b", ""),

    # ------ Cowork OS / iCloud paths ------
    (r"C:/Users/Administrator/iCloudDrive/Cowork OS", "<FONTE_REFERENCIA_READONLY>"),
    (r"iCloudDrive/Cowork OS", "<FONTE_REFERENCIA_READONLY>"),
    (r"\bCowork OS\b", "Workspace de Referencia"),
    (r"\biCloudDrive\b", "<SINCRONIZADOR>"),
    (r"\biCloud\b(?! Drive)", "<sincronizador>"),

    # ------ Maria Alice ------
    (r"Maria Alice", "[alpha tester]"),

    # ------ Ferramentas proprietarias do escritorio-modelo ------
    (r"\bASTREA\b", "[sistema de gestao processual]"),
    (r"\bAstrea\b", "[sistema de gestao processual]"),
    (r"\bFireflies\b", "[transcritor de reunioes]"),
    (r"\bfireflies\b", "[transcritor de reunioes]"),
    (r"\bHoppe\b", "[CRM do escritorio]"),
    (r"\bHOPPE\b", "[CRM do escritorio]"),
    (r"\bhoppe\b", "[CRM do escritorio]"),
    (r"\bKingHost\b", "[provedor de email]"),
    (r"\bkinghost\b", "[provedor de email]"),
    (r"\bASAAS\b", "[banco/PSP do escritorio]"),
    (r"\bAsaas\b", "[banco/PSP do escritorio]"),
    (r"\bCloudflare\b", "[provedor de infra]"),
    (r"\bcloudflare\b", "[provedor de infra]"),
    (r"\bStripe\b", "[processador de pagamentos]"),
    (r"\bstripe\b", "[processador de pagamentos]"),
    (r"\bBravy\b", "[mentoria de devops]"),
    (r"\bbravy\b", "[mentoria de devops]"),

    # ------ Dados de clientes vazados ------
    (r"\bAndreas Food\b", "[Cliente Anonimizado]"),
    (r"\bLucas H Ferreira\b", "[Contraparte Anonimizada]"),
    (r"\bIRX\b", "[Cliente Anonimizado]"),
    (r"\bDanilo\b", "[Pessoa Anonimizada]"),
    (r"\bBarretos\b", "[Localidade Anonimizada]"),
    (r"\bJurkovich\b", "[Contador Externo]"),

    # ------ Sbroggio (CATCH-ALL — depois de tudo especifico) ------
    (r"\bSbroggio\b", "Mentor"),
    (r"\bsbroggio\b", "mentor"),
    (r"\bSBROGGIO\b", "MENTOR"),
]


def apply_substitutions(content: str) -> tuple[str, int]:
    """Aplica todas as substituicoes ao conteudo. Retorna (novo, total_matches)."""
    total = 0
    new_content = content
    for pattern, replacement in SUBSTITUTIONS:
        new_content, n = re.subn(pattern, replacement, new_content)
        total += n
    return new_content, total


def find_target_files(repo_root: Path) -> list[Path]:
    """Encontra arquivos a auditar (.md, .json) excluindo audit/, .git/, _sandbox/."""
    targets: list[Path] = []
    for ext in ("*.md", "*.json", "*.yml", "*.yaml", "*.txt"):
        for p in repo_root.rglob(ext):
            parts_lower = [part.lower() for part in p.parts]
            if any(skip in parts_lower for skip in (".git", "audit", "_sandbox", "node_modules")):
                continue
            targets.append(p)
    return sorted(targets)


def main() -> int:
    parser = argparse.ArgumentParser(description="Despersonaliza arquivos do plugin.")
    parser.add_argument("--dry", action="store_true", help="So mostra o que seria mudado.")
    parser.add_argument("--check", action="store_true", help="Exit 1 se algum arquivo precisaria mudar.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    targets = find_target_files(repo_root)

    print(f"Repo: {repo_root}")
    print(f"Arquivos analisados: {len(targets)}")
    print()

    total_changes = 0
    files_changed = 0

    for path in targets:
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        # Aplica linha-a-linha respeitando whitelist
        new_lines: list[str] = []
        n_total = 0
        for line in original.splitlines(keepends=True):
            if is_whitelisted(line):
                new_lines.append(line)
                continue
            new_line, n = apply_substitutions(line)
            new_lines.append(new_line)
            n_total += n
        new_content = "".join(new_lines)

        if n_total > 0:
            files_changed += 1
            total_changes += n_total
            rel = path.relative_to(repo_root)
            print(f"  {rel}: {n_total} substituicao(oes)")

            if args.check:
                continue

            if not args.dry:
                path.write_text(new_content, encoding="utf-8")

    print()
    print(f"Total: {total_changes} substituicao(oes) em {files_changed} arquivo(s).")

    if args.check and total_changes > 0:
        return 1
    if args.dry:
        print("[DRY-RUN] Nenhum arquivo foi modificado.")
    elif total_changes > 0:
        print("[APLICADO] Arquivos modificados in-place.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
