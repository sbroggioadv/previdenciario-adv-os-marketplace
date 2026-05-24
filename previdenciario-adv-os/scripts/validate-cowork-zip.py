#!/usr/bin/env python3
"""
validate-cowork-zip.py — Guardrail server-side simulado para ZIPs Cowork.

Abre o ZIP gerado e aplica TODAS as validacoes server-side conhecidas do Claude
Cowork (Claude Desktop) antes do upload. Output binario PASS/FAIL com
diagnostico detalhado. Falhas silenciosas no Cowork custam dias de bisseccao;
este script faz a bisseccao virtual em segundos.

VALIDACOES APLICADAS:
  1. Estrutura do ZIP (raiz so com .claude-plugin/ + skills/)
  2. plugin.json:
     a. Campos minimos: name, version, description (recomenda APENAS esses)
     b. plugin.name regex `^[a-z0-9]+(-[a-z0-9]+)*$` + max 64 chars
     c. plugin.description max 1024 chars
  3. Para cada skill:
     a. Folder name regex `^[a-z0-9-/]+$` + max 64 chars
     b. SKILL.md frontmatter `name` <= 64 chars e bate com folder name
     c. SKILL.md frontmatter `description` <= 1024 chars
     d. SKILL.md tamanho total <= 11000 bytes
     e. Frontmatter so contem `name` e `description` (warning se mais)
  4. Sem artefatos macOS (.DS_Store, __MACOSX/)
  5. Sem nomes de skill colidindo com plugin pai conhecido
  6. Limites globais do ZIP (200MB, 100k arquivos, ratio compressao 50:1)

USO:
  python3 scripts/validate-cowork-zip.py path/to/plugin.zip
  python3 scripts/validate-cowork-zip.py path/to/plugin.zip --json
  python3 scripts/validate-cowork-zip.py path/to/plugin.zip --allow-extra-fields

EXIT:
  0 = PASS (ZIP pronto pra upload)
  1 = FAIL (problemas encontrados)
  2 = erro de argumento ou IO
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# ----- Limites canonicos (decompile do app.asar do Claude Desktop) ----------

PLUGIN_NAME_REGEX = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKILL_NAME_REGEX = re.compile(r"^[a-z0-9-/]+$")

PLUGIN_NAME_MAX = 64
PLUGIN_DESCRIPTION_MAX = 1024
SKILL_NAME_MAX = 64
SKILL_DESCRIPTION_MAX = 1024
SKILL_FILE_SIZE_HARD = 11_000  # ~11 KB hard limit observado empiricamente
SKILL_FILE_SIZE_WARN = 10_500

ZIP_TOTAL_SIZE_MAX = 200 * 1024 * 1024  # 200 MB
ZIP_FILES_MAX = 100_000
ZIP_COMPRESS_RATIO_MAX = 50  # 50:1
ZIP_PATH_LENGTH_MAX = 1024

# Skills do plugin pai do mesmo operador no Cowork. Colisao = rejeicao silenciosa.
# Mantido sincronizado com scripts/check-skill-descriptions.py.
PLUGIN_PAI_SKILLS = {
    "analise-trilateral", "calculo-juridico", "compliance-lgpd",
    "comunicacao-cliente", "contrarrazoes-recursais",
    "contrato-social-holding", "contratos-societarios",
    "cowork-onboarding", "cowork-sync", "documentos-extrajudiciais",
    "due-diligence", "escritorio-advocacia", "estrategia-de-caso",
    "financeiro-juridico", "firm-master", "jurisprudencia-estrategica",
    "marketing-juridico", "memory-evolver", "minutas-contratuais",
    "parecer-juridico", "pecas-processuais", "peticao-universal",
    "replica-estrategica", "resumo-audiencia", "suprema-corte-r1-coleta",
    "suprema-corte-r2-base-juridica", "suprema-corte-r3-tese",
    "suprema-corte-r4-completude", "visual-law",
}

# Campos canonicos do plugin.json para Cowork. Tudo alem disso e desencorajado
# (ainda nao confirmado se rejeita ou ignora — testes empiricos sao instaveis).
PLUGIN_JSON_REQUIRED = {"name", "version", "description"}
PLUGIN_JSON_RECOMMENDED_EXTRA = set()  # nenhum por enquanto

# Frontmatter canonico de SKILL.md. Demais campos viram WARN, nao FAIL.
SKILL_FRONTMATTER_CANONICAL = {"name", "description"}


# ----- Resultado estruturado -----------------------------------------------

@dataclass
class Finding:
    severity: str  # "error" | "warn" | "info"
    code: str
    where: str
    message: str

    def fmt(self) -> str:
        return f"  [{self.severity.upper()}] {self.code} @ {self.where}: {self.message}"


@dataclass
class Report:
    zip_path: str
    findings: list[Finding] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warns(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warn"]

    def add(self, severity: str, code: str, where: str, message: str) -> None:
        self.findings.append(Finding(severity, code, where, message))

    def passed(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "zip": self.zip_path,
            "passed": self.passed(),
            "stats": self.stats,
            "findings": [
                {"severity": f.severity, "code": f.code, "where": f.where, "message": f.message}
                for f in self.findings
            ],
        }


# ----- Helpers --------------------------------------------------------------

def parse_frontmatter(skill_text: str) -> tuple[dict, str | None]:
    """Parse YAML frontmatter de SKILL.md (subset: scalar + folded scalar).
    Retorna ({fields}, error_or_none).
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", skill_text, re.DOTALL)
    if not m:
        return {}, "sem frontmatter delimitado por ---"
    fm = m.group(1)

    fields: dict[str, str] = {}
    lines = fm.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        # match `key: value` or `key: >` (folded) or `key: |` (block)
        kv = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
        if not kv:
            i += 1
            continue
        key = kv.group(1)
        rest = kv.group(2).strip()
        if rest in (">", "|", ">-", "|-"):
            # Folded/block: consome linhas indentadas seguintes
            i += 1
            buf: list[str] = []
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t") or lines[i] == ""):
                if lines[i] == "":
                    buf.append("")
                else:
                    buf.append(lines[i].lstrip())
                i += 1
            if rest.startswith(">"):
                # folded: linhas viram um paragrafo, blank lines viram \n
                paragraphs: list[str] = []
                cur: list[str] = []
                for b in buf:
                    if b == "":
                        if cur:
                            paragraphs.append(" ".join(cur))
                            cur = []
                    else:
                        cur.append(b)
                if cur:
                    paragraphs.append(" ".join(cur))
                fields[key] = "\n".join(paragraphs).strip()
            else:
                fields[key] = "\n".join(buf).rstrip()
        else:
            # inline scalar
            v = rest.strip()
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            fields[key] = v
            i += 1

    return fields, None


# ----- Validacoes -----------------------------------------------------------

def validate_zip(zip_path: Path, allow_extra_fields: bool = False) -> Report:
    rep = Report(zip_path=str(zip_path))

    if not zip_path.exists():
        rep.add("error", "ZIP_NOT_FOUND", str(zip_path), "arquivo nao encontrado")
        return rep

    zip_size = zip_path.stat().st_size
    rep.stats["zip_size_bytes"] = zip_size

    if zip_size > ZIP_TOTAL_SIZE_MAX:
        rep.add("error", "ZIP_TOO_BIG",
                str(zip_path),
                f"{zip_size} bytes > limite {ZIP_TOTAL_SIZE_MAX}")

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            rep.stats["zip_entries"] = len(names)

            if len(names) > ZIP_FILES_MAX:
                rep.add("error", "ZIP_TOO_MANY_FILES",
                        str(zip_path),
                        f"{len(names)} entries > limite {ZIP_FILES_MAX}")

            # ---- 1. Estrutura raiz ----
            top_dirs = set()
            for n in names:
                head = n.split("/", 1)[0]
                top_dirs.add(head)

            unexpected = top_dirs - {".claude-plugin", "skills"}
            for d in unexpected:
                rep.add("warn", "UNEXPECTED_TOP",
                        d,
                        "diretorio/arquivo na raiz alem de .claude-plugin/ e skills/")

            # ---- 2. Artefatos macOS ----
            ds_store = [n for n in names if n.endswith("/.DS_Store") or n == ".DS_Store"]
            for n in ds_store:
                rep.add("error", "MACOS_DS_STORE", n, "arquivo .DS_Store no ZIP")
            macosx = [n for n in names if "__MACOSX" in n]
            for n in macosx:
                rep.add("error", "MACOS_MACOSX_FOLDER", n, "pasta __MACOSX no ZIP")

            # ---- 3. plugin.json ----
            plugin_json_name = ".claude-plugin/plugin.json"
            if plugin_json_name not in names:
                rep.add("error", "PLUGIN_JSON_MISSING", plugin_json_name,
                        "plugin.json ausente em .claude-plugin/")
            else:
                raw = zf.read(plugin_json_name).decode("utf-8")
                try:
                    pj = json.loads(raw)
                except json.JSONDecodeError as e:
                    rep.add("error", "PLUGIN_JSON_INVALID", plugin_json_name,
                            f"JSON invalido: {e}")
                    pj = None

                if pj is not None:
                    rep.stats["plugin_json"] = {
                        "name": pj.get("name"),
                        "version": pj.get("version"),
                        "description_length": len(pj.get("description", "")),
                        "extra_keys": sorted(set(pj.keys()) - PLUGIN_JSON_REQUIRED),
                    }

                    # Campos obrigatorios
                    for f in PLUGIN_JSON_REQUIRED:
                        if f not in pj:
                            rep.add("error", "PLUGIN_JSON_MISSING_FIELD",
                                    plugin_json_name, f"campo '{f}' ausente")

                    # plugin.name
                    name = pj.get("name", "")
                    if name and not PLUGIN_NAME_REGEX.match(name):
                        rep.add("error", "PLUGIN_NAME_REGEX",
                                plugin_json_name,
                                f"name '{name}' nao bate com {PLUGIN_NAME_REGEX.pattern}")
                    if name and len(name) > PLUGIN_NAME_MAX:
                        rep.add("error", "PLUGIN_NAME_LONG",
                                plugin_json_name,
                                f"name tem {len(name)} chars > {PLUGIN_NAME_MAX}")

                    # plugin.description
                    desc = pj.get("description", "")
                    if len(desc) > PLUGIN_DESCRIPTION_MAX:
                        rep.add("error", "PLUGIN_DESCRIPTION_LONG",
                                plugin_json_name,
                                f"description tem {len(desc)} chars > {PLUGIN_DESCRIPTION_MAX}")

                    # Campos extras
                    extras = set(pj.keys()) - PLUGIN_JSON_REQUIRED
                    if extras and not allow_extra_fields:
                        rep.add("warn", "PLUGIN_JSON_EXTRA_FIELDS",
                                plugin_json_name,
                                f"campos alem do canonico (name/version/description): {sorted(extras)}. "
                                f"Cowork pode aceitar mas e mais seguro remover. "
                                f"Use --allow-extra-fields para silenciar.")

            # ---- 4. Skills ----
            # Agrupa por pasta
            skills_by_folder: dict[str, list[str]] = {}
            for n in names:
                m = re.match(r"^skills/([^/]+)/(.*)$", n)
                if not m:
                    continue
                folder, rel = m.group(1), m.group(2)
                if rel == "":
                    continue
                skills_by_folder.setdefault(folder, []).append(rel)

            rep.stats["skill_count"] = len(skills_by_folder)
            skill_collisions: list[str] = []
            skills_over_size: list[tuple[str, int]] = []
            skills_warn_size: list[tuple[str, int]] = []
            skills_desc_long: list[tuple[str, int]] = []

            for folder in sorted(skills_by_folder):
                where = f"skills/{folder}/"

                # 4a. folder name
                if not SKILL_NAME_REGEX.match(folder):
                    rep.add("error", "SKILL_FOLDER_REGEX",
                            where,
                            f"folder name '{folder}' nao bate com {SKILL_NAME_REGEX.pattern}")
                if len(folder) > SKILL_NAME_MAX:
                    rep.add("error", "SKILL_FOLDER_LONG",
                            where,
                            f"folder name tem {len(folder)} chars > {SKILL_NAME_MAX}")

                # 4b. SKILL.md presente
                skill_md_name = f"skills/{folder}/SKILL.md"
                if skill_md_name not in names:
                    rep.add("error", "SKILL_MD_MISSING", where, "SKILL.md ausente")
                    continue

                content = zf.read(skill_md_name).decode("utf-8")
                size_bytes = len(content.encode("utf-8"))

                # 4c. tamanho
                if size_bytes > SKILL_FILE_SIZE_HARD:
                    rep.add("error", "SKILL_MD_TOO_BIG",
                            skill_md_name,
                            f"{size_bytes} bytes > {SKILL_FILE_SIZE_HARD}")
                    skills_over_size.append((folder, size_bytes))
                elif size_bytes > SKILL_FILE_SIZE_WARN:
                    rep.add("warn", "SKILL_MD_NEAR_LIMIT",
                            skill_md_name,
                            f"{size_bytes} bytes (margem apertada, limite {SKILL_FILE_SIZE_HARD})")
                    skills_warn_size.append((folder, size_bytes))

                # 4d. frontmatter
                fm, err = parse_frontmatter(content)
                if err:
                    rep.add("error", "SKILL_FRONTMATTER_INVALID", skill_md_name, err)
                    continue

                fm_name = fm.get("name", "")
                fm_desc = fm.get("description", "")

                if not fm_name:
                    rep.add("error", "SKILL_NAME_MISSING", skill_md_name,
                            "frontmatter sem 'name'")
                else:
                    if len(fm_name) > SKILL_NAME_MAX:
                        rep.add("error", "SKILL_NAME_LONG", skill_md_name,
                                f"frontmatter name tem {len(fm_name)} chars > {SKILL_NAME_MAX}")
                    if not SKILL_NAME_REGEX.match(fm_name):
                        rep.add("error", "SKILL_NAME_REGEX", skill_md_name,
                                f"frontmatter name '{fm_name}' nao bate com {SKILL_NAME_REGEX.pattern}")
                    if fm_name != folder:
                        rep.add("error", "SKILL_NAME_FOLDER_MISMATCH", skill_md_name,
                                f"frontmatter name '{fm_name}' != folder name '{folder}'")

                if not fm_desc:
                    rep.add("error", "SKILL_DESCRIPTION_MISSING", skill_md_name,
                            "frontmatter sem 'description'")
                elif len(fm_desc) > SKILL_DESCRIPTION_MAX:
                    rep.add("error", "SKILL_DESCRIPTION_LONG", skill_md_name,
                            f"description tem {len(fm_desc)} chars > {SKILL_DESCRIPTION_MAX}")
                    skills_desc_long.append((folder, len(fm_desc)))

                # 4e. campos extras no frontmatter
                extras = set(fm.keys()) - SKILL_FRONTMATTER_CANONICAL
                if extras:
                    rep.add("warn", "SKILL_FRONTMATTER_EXTRA",
                            skill_md_name,
                            f"campos alem de name/description: {sorted(extras)}")

                # 4f. colisao com plugin pai
                if folder in PLUGIN_PAI_SKILLS:
                    rep.add("error", "SKILL_COLLISION_PARENT",
                            where,
                            f"name colide com skill do plugin pai (rejeicao silenciosa garantida)")
                    skill_collisions.append(folder)

            rep.stats["skills_over_size"] = skills_over_size
            rep.stats["skills_warn_size"] = skills_warn_size
            rep.stats["skills_desc_long"] = skills_desc_long
            rep.stats["skills_collide_parent"] = skill_collisions

            # ---- 5. Path length ----
            for n in names:
                if len(n) > ZIP_PATH_LENGTH_MAX:
                    rep.add("error", "PATH_TOO_LONG", n,
                            f"path tem {len(n)} chars > {ZIP_PATH_LENGTH_MAX}")

    except zipfile.BadZipFile as e:
        rep.add("error", "ZIP_CORRUPT", str(zip_path), f"ZIP corrompido: {e}")

    return rep


# ----- CLI ------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="Guardrail Cowork: valida ZIP pre-upload")
    p.add_argument("zip", help="caminho do .zip a validar")
    p.add_argument("--json", action="store_true", help="output JSON estruturado")
    p.add_argument("--allow-extra-fields", action="store_true",
                   help="aceita campos extras em plugin.json sem WARN")
    args = p.parse_args()

    zip_path = Path(args.zip).expanduser().resolve()
    rep = validate_zip(zip_path, allow_extra_fields=args.allow_extra_fields)

    if args.json:
        print(json.dumps(rep.to_dict(), ensure_ascii=False, indent=2))
        return 0 if rep.passed() else 1

    # texto
    print(f"==> Validando {rep.zip_path}")
    print()
    if rep.stats:
        print("STATS:")
        for k, v in rep.stats.items():
            if isinstance(v, list) and len(v) > 3:
                print(f"  {k}: {len(v)} itens (mostrando 3) {v[:3]}")
            else:
                print(f"  {k}: {v}")
        print()

    if rep.errors:
        print(f"ERROS ({len(rep.errors)}):")
        for f in rep.errors:
            print(f.fmt())
        print()
    if rep.warns:
        print(f"WARNINGS ({len(rep.warns)}):")
        for f in rep.warns:
            print(f.fmt())
        print()

    if rep.passed():
        print("VEREDITO: PASS — ZIP pronto pra upload no Cowork.")
        return 0
    else:
        print(f"VEREDITO: FAIL — {len(rep.errors)} erro(s) bloqueiam upload.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
