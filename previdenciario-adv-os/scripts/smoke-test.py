#!/usr/bin/env python3
"""
smoke-test.py — Validacao end-to-end do plugin Previdenciario-Adv-OS.

Simula um /start completo e valida que:
1. State e criado e valido
2. Render gera todos os arquivos esperados
3. Placeholders foram resolvidos (nao ha {{VAR}} nos outputs)
4. Estrutura de pastas de area esta correta
5. Persona contem dados do escritorio
6. CLAUDE.md de area tem contexto especifico
7. Resolve-persona encontra a persona quando PREVIDENCIARIO_PERSONA setado
8. Idempotencia: rodar render 2x nao corrompe nada

Uso:
    python scripts/smoke-test.py                # roda todos os tests
    python scripts/smoke-test.py --keep         # preserva diretorio de teste para inspecao
    python scripts/smoke-test.py --verbose      # mais output

Exit 0 = todos os tests passaram. Exit 1 = algum teste falhou.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = PLUGIN_ROOT / "scripts"
PYTHON = sys.executable


class TestResult:
    def __init__(self, name: str, passed: bool, message: str = "") -> None:
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        msg = f" — {self.message}" if self.message else ""
        return f"  [{status}] {self.name}{msg}"


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", **kwargs)


def _is_windows() -> bool:
    return os.name == "nt"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_init_state(tmp: Path) -> TestResult:
    r = _run([PYTHON, str(SCRIPTS / "state.py"), "init", str(tmp),
              "--firm-name", "Silva Advocacia", "--firm-slug", "silva-advocacia",
              "--advogado", "Joao da Silva"])
    if r.returncode != 0:
        return TestResult("init state", False, f"exit {r.returncode}: {r.stderr[:200]}")
    if not (tmp / "previdenciario" / "cowork-state.json").exists():
        return TestResult("init state", False, "cowork-state.json nao foi criado")
    return TestResult("init state", True)


def test_validate_state(tmp: Path) -> TestResult:
    r = _run([PYTHON, str(SCRIPTS / "state.py"), "validate", str(tmp)])
    if r.returncode != 0:
        return TestResult("validate state", False, r.stdout + r.stderr)
    return TestResult("validate state", True)


def test_configure_state(tmp: Path) -> TestResult:
    """Adiciona areas, configura tom, marca skills opt-in."""
    # Areas
    areas = [
        {
            "slug": "CONTENCIOSO/CIVEL",
            "display_name": "Contencioso Civel",
            "tipo_atuacao": "contencioso",
            "polo_predominante": "ambos",
            "subfolders": ["Clientes", "Processos", "Modelos"],
            "skills_sugeridas": ["pecas-processuais", "peticao-universal"],
            "activated_at": "2026-04-17T18:00:00+00:00",
        },
        {
            "slug": "CONSULTIVO",
            "display_name": "Consultivo Empresarial",
            "tipo_atuacao": "consultivo",
            "polo_predominante": None,
            "subfolders": ["Clientes", "Pareceres", "Modelos"],
            "skills_sugeridas": ["parecer-juridico", "due-diligence"],
            "activated_at": "2026-04-17T18:00:00+00:00",
        },
    ]
    r = _run([PYTHON, str(SCRIPTS / "state.py"), "set", str(tmp), "areas", json.dumps(areas)])
    if r.returncode != 0:
        return TestResult("configure state (areas)", False, r.stderr[:200])

    # OAB
    for path, val in (
        ("identity.oab_numero", '"123456"'),
        ("identity.oab_uf", '"SP"'),
        ("identity.cidade", '"Recife"'),
        ("identity.uf", '"PE"'),
        ("identity.email", '"contato@silva.adv.br"'),
        ("tom_voz.perfil", '"tecnico-combativo"'),
        ("tom_voz.intensidade_combativa", "8"),
        ("skills.opt_in_active",
         json.dumps(["estrategia-de-caso", "analise-trilateral",
                    "jurisprudencia-estrategica", "pecas-processuais"])),
    ):
        r = _run([PYTHON, str(SCRIPTS / "state.py"), "set", str(tmp), path, val])
        if r.returncode != 0:
            return TestResult(f"configure state ({path})", False, r.stderr[:200])

    return TestResult("configure state", True)


def test_render_dry_run(tmp: Path) -> TestResult:
    r = _run([PYTHON, str(SCRIPTS / "render.py"), str(tmp), "--dry-run"])
    if r.returncode != 0:
        return TestResult("render --dry-run", False, r.stderr[:200])
    expected = ["persona.md", "CLAUDE.md", "MEMORY.md",
                "CONTENCIOSO", "CONSULTIVO"]
    missing = [s for s in expected if s not in r.stdout]
    if missing:
        return TestResult("render --dry-run", False, f"output nao menciona {missing}")
    return TestResult("render --dry-run", True)


def test_render_real(tmp: Path, workspace: Path) -> TestResult:
    r = _run([PYTHON, str(SCRIPTS / "render.py"), str(tmp), "--workspace", str(workspace)])
    if r.returncode != 0:
        return TestResult("render real", False, r.stderr[:200])
    return TestResult("render real", True)


def test_files_exist(tmp: Path, workspace: Path) -> TestResult:
    expected_files = [
        tmp / "previdenciario" / "cowork-state.json",
        tmp / "previdenciario" / "persona.md",
        tmp / "CLAUDE.md",
        tmp / "MEMORY.md",
        tmp / "CONTENCIOSO" / "CIVEL" / "CLAUDE.md",
        tmp / "CONTENCIOSO" / "CIVEL" / "MEMORY.md",
        tmp / "CONSULTIVO" / "CLAUDE.md",
        tmp / "CONSULTIVO" / "MEMORY.md",
        workspace / ".claude" / "settings.local.json",
    ]
    expected_dirs = [
        tmp / "CONTENCIOSO" / "CIVEL" / "Clientes",
        tmp / "CONTENCIOSO" / "CIVEL" / "Processos",
        tmp / "CONSULTIVO" / "Clientes",
        tmp / "CONSULTIVO" / "Pareceres",
    ]
    missing = [str(p.relative_to(tmp.parent)) for p in expected_files if not p.is_file()]
    missing += [str(p.relative_to(tmp.parent)) + "/" for p in expected_dirs if not p.is_dir()]
    if missing:
        return TestResult("files exist", False, f"ausentes: {missing[:5]}")
    return TestResult("files exist", True)


def test_placeholders_resolved(tmp: Path) -> TestResult:
    """Todos os arquivos gerados: sem {{VAR}} literal; todos devem ter firm_name; persona+raiz CLAUDE devem ter advogado_nome."""
    issues = []
    check_files = [
        (tmp / "previdenciario" / "persona.md", True, True),   # firm + advogado
        (tmp / "CLAUDE.md", True, True),                  # firm + advogado
        (tmp / "MEMORY.md", False, False),                # so nao deve ter placeholders
        (tmp / "CONTENCIOSO" / "CIVEL" / "CLAUDE.md", True, False),  # so firm
        (tmp / "CONSULTIVO" / "CLAUDE.md", True, False),  # so firm
    ]
    for p, must_have_firm, must_have_advogado in check_files:
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8")
        rel = str(p.relative_to(tmp))
        leftover = re.findall(r"\{\{[A-Z_][A-Z0-9_]*\}\}", content)
        if leftover:
            issues.append(f"{rel}: placeholders nao resolvidos: {set(leftover)}")
        if must_have_firm and "Silva Advocacia" not in content:
            issues.append(f"{rel}: nao contem 'Silva Advocacia'")
        if must_have_advogado and "Joao da Silva" not in content:
            issues.append(f"{rel}: nao contem 'Joao da Silva'")

    if issues:
        return TestResult("placeholders resolved", False, "; ".join(issues[:3]))
    return TestResult("placeholders resolved", True)


def test_area_claude_has_context(tmp: Path) -> TestResult:
    """CLAUDE.md de area deve ter contexto especifico da area."""
    contencioso = (tmp / "CONTENCIOSO" / "CIVEL" / "CLAUDE.md").read_text(encoding="utf-8")
    consultivo = (tmp / "CONSULTIVO" / "CLAUDE.md").read_text(encoding="utf-8")

    issues = []
    if "Contencioso Civel" not in contencioso:
        issues.append("CONTENCIOSO/CIVEL/CLAUDE.md sem 'Contencioso Civel'")
    if "ambos os polos" not in contencioso.lower() and "ambos" not in contencioso.lower():
        issues.append("CONTENCIOSO/CIVEL/CLAUDE.md sem mencao a polo 'ambos'")
    if "Consultivo" not in consultivo:
        issues.append("CONSULTIVO/CLAUDE.md sem 'Consultivo'")
    if "Pareceres" not in consultivo and "pareceres" not in consultivo.lower():
        issues.append("CONSULTIVO/CLAUDE.md sem mencao a pareceres")

    if issues:
        return TestResult("area CLAUDE context", False, "; ".join(issues))
    return TestResult("area CLAUDE context", True)


def test_resolve_persona_env(tmp: Path) -> TestResult:
    """Com PREVIDENCIARIO_PERSONA setado, resolve-persona deve encontrar a persona real."""
    env = os.environ.copy()
    env["PREVIDENCIARIO_PERSONA"] = str(tmp / "previdenciario" / "persona.md")
    r = subprocess.run([PYTHON, str(SCRIPTS / "resolve-persona.py")],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    if r.returncode != 0:
        return TestResult("resolve-persona (env)", False, r.stderr[:200])
    if "Silva Advocacia" not in r.stdout:
        return TestResult("resolve-persona (env)", False, "persona carregada nao contem 'Silva Advocacia'")
    if "FALLBACK" in r.stderr:
        return TestResult("resolve-persona (env)", False, "retornou FALLBACK com env setado")
    return TestResult("resolve-persona (env)", True)


def test_resolve_persona_fallback() -> TestResult:
    """Sem config, resolve-persona deve retornar fallback generico."""
    env = os.environ.copy()
    env.pop("PREVIDENCIARIO_PERSONA", None)
    # Roda em tmpdir sem settings.local.json
    with tempfile.TemporaryDirectory() as empty:
        r = subprocess.run([PYTHON, str(SCRIPTS / "resolve-persona.py")],
                           cwd=empty, capture_output=True, text=True,
                           encoding="utf-8", env=env)
    if r.returncode != 0:
        return TestResult("resolve-persona (fallback)", False, r.stderr[:200])
    if "FALLBACK" not in r.stderr:
        return TestResult("resolve-persona (fallback)", False, "stderr nao contem 'FALLBACK'")
    # Aceita "configurado" com ou sem acento
    if "configurado" not in r.stdout.lower() and "fallback" not in r.stdout.lower():
        return TestResult("resolve-persona (fallback)", False, "stdout nao menciona config/fallback")
    return TestResult("resolve-persona (fallback)", True)


def test_idempotency(tmp: Path) -> TestResult:
    """Rodar render 2x nao deve corromper. Arquivos user-owned (persona, MEMORY) devem ser preservados."""
    # Edita persona manualmente
    persona = tmp / "previdenciario" / "persona.md"
    original = persona.read_text(encoding="utf-8")
    marker = "\n<!-- edicao manual do usuario -->\n"
    persona.write_text(original + marker, encoding="utf-8")

    # Roda render sem --force
    r = _run([PYTHON, str(SCRIPTS / "render.py"), str(tmp)])
    if r.returncode != 0:
        return TestResult("idempotency (render sem force)", False, r.stderr[:200])

    new_persona = persona.read_text(encoding="utf-8")
    if marker not in new_persona:
        return TestResult("idempotency", False, "edicao manual foi sobrescrita (deveria preservar)")

    # Roda com --force e confirma que agora sobrescreve
    r = _run([PYTHON, str(SCRIPTS / "render.py"), str(tmp), "--force"])
    if r.returncode != 0:
        return TestResult("idempotency (render com force)", False, r.stderr[:200])
    new_persona = persona.read_text(encoding="utf-8")
    if marker in new_persona:
        return TestResult("idempotency", False, "edicao manual NAO foi sobrescrita com --force (deveria)")

    return TestResult("idempotency", True)


def test_find_cowork(tmp: Path) -> TestResult:
    """find-cowork com arg explicito deve retornar o path."""
    r = _run([PYTHON, str(SCRIPTS / "find-cowork.py"), str(tmp)])
    if r.returncode != 0:
        return TestResult("find-cowork", False, r.stderr[:200])
    found = r.stdout.strip()
    if Path(found).resolve() != tmp.resolve():
        return TestResult("find-cowork", False, f"retornou {found}, esperado {tmp}")
    return TestResult("find-cowork", True)


def test_audit_clean() -> TestResult:
    """Audit do plugin inteiro deve passar."""
    r = _run([PYTHON, str(PLUGIN_ROOT / "audit" / "audit.py"), "--quiet"])
    if r.returncode != 0:
        return TestResult("audit LIMPO", False, "audit detectou contaminacao")
    return TestResult("audit LIMPO", True)


def test_fingerprint_diff(cowork: Path) -> TestResult:
    """fingerprint --diff retorna JSON valido apos baseline."""
    r = _run([PYTHON, str(SCRIPTS / "fingerprint.py"),
              "--plugin-root", str(PLUGIN_ROOT),
              "--cowork", str(cowork),
              "--update-auto-deploy"])
    if r.returncode != 0:
        return TestResult("fingerprint baseline", False, r.stderr[:200])

    r = _run([PYTHON, str(SCRIPTS / "fingerprint.py"),
              "--plugin-root", str(PLUGIN_ROOT),
              "--cowork", str(cowork),
              "--diff"])
    if r.returncode != 0:
        return TestResult("fingerprint --diff", False, r.stderr[:200])

    import json as _json
    try:
        diff = _json.loads(r.stdout)
    except Exception as e:
        return TestResult("fingerprint --diff", False, f"JSON invalido: {e}")
    if diff.get("modified") or diff.get("added") or diff.get("removed"):
        return TestResult("fingerprint --diff",
                          False,
                          f"apos baseline deveria ser vazio, foi: {len(diff.get('modified', []))} modified")
    return TestResult("fingerprint --diff", True)


def test_post_edit_hook(cowork: Path) -> TestResult:
    """Hook post-edit registra pending para edicao em COWORK, ignora fora, debouncing."""
    import json as _json
    hook_script = PLUGIN_ROOT / "hooks" / "scripts" / "post-edit-evolve-memory.py"

    area_dir = cowork / "TESTE-AREA"
    area_dir.mkdir(exist_ok=True)
    target = area_dir / "arquivo.md"
    target.write_text("conteudo", encoding="utf-8")

    payload = _json.dumps({
        "tool_name": "Edit",
        "tool_input": {"file_path": str(target)},
        "tool_response": {"success": True},
    })

    r = _run([PYTHON, str(hook_script)], input=payload)
    if r.returncode != 0:
        return TestResult("post-edit hook", False, f"exit {r.returncode}: {r.stderr[:200]}")

    pending = cowork / "previdenciario" / ".memory-evolver-pending.json"
    if not pending.exists():
        return TestResult("post-edit hook", False, "pending nao foi criado")

    data = _json.loads(pending.read_text(encoding="utf-8"))
    if not any(e.get("file_path") == str(target) for e in data):
        return TestResult("post-edit hook", False, "path esperado nao esta em pending")

    # 2a chamada deve ser debounced (nao adiciona duplicata)
    r2 = _run([PYTHON, str(hook_script)], input=payload)
    data2 = _json.loads(pending.read_text(encoding="utf-8"))
    if len(data2) != len(data):
        return TestResult("post-edit hook", False, "debounce falhou, duplicou pending")

    return TestResult("post-edit hook", True)


def test_prompt_intercept_hook() -> TestResult:
    """Hook prompt-intercept injeta contexto previdenciario, juridico geral, ou silencia."""
    import json as _json
    hook_script = PLUGIN_ROOT / "hooks" / "scripts" / "prompt-intercept-corte.py"

    # Tarefa previdenciaria explicita
    r = _run([PYTHON, str(hook_script)],
             input=_json.dumps({"prompt": "Preciso revisar uma aposentadoria do INSS"}))
    if r.returncode != 0:
        return TestResult("prompt-intercept hook", False, f"exit {r.returncode}")
    if "previdenciario-adv-os" not in r.stdout.lower():
        return TestResult("prompt-intercept hook", False, "nao injetou contexto previdenciario")

    # Bypass
    r = _run([PYTHON, str(hook_script)],
             input=_json.dumps({"prompt": "Elabore peticao previdenciaria --no-corte"}))
    if "bypass" not in r.stdout.lower():
        return TestResult("prompt-intercept hook", False, "bypass --no-corte nao reconhecido")

    # Tarefa juridica geral (nao previdenciaria)
    r = _run([PYTHON, str(hook_script)],
             input=_json.dumps({"prompt": "Elabore uma peticao trabalhista"}))
    if "previdenciario-adv-os" not in r.stdout.lower():
        return TestResult("prompt-intercept hook", False, "nao processou tarefa juridica geral")

    # Nao-juridico
    r = _run([PYTHON, str(hook_script)],
             input=_json.dumps({"prompt": "Como vai voce?"}))
    if r.stdout.strip():
        return TestResult("prompt-intercept hook", False, f"nao deveria ter output, teve: {r.stdout[:100]}")

    return TestResult("prompt-intercept hook", True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test end-to-end")
    parser.add_argument("--keep", action="store_true", help="Preserva diretorio de teste")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    print("=" * 70)
    print("SMOKE TEST — Plugin Previdenciario-Adv-OS")
    print("=" * 70)
    print()

    workdir = Path(tempfile.mkdtemp(prefix="prev-smoke-"))
    cowork = workdir / "cowork-teste"
    workspace = workdir / "workspace-teste"
    cowork.mkdir()
    workspace.mkdir()

    print(f"Workdir: {workdir}")
    print()

    results: list[TestResult] = []

    # Roda tests em sequencia
    results.append(test_init_state(cowork))
    if not results[-1].passed:
        print(*results, sep="\n")
        return 1

    results.append(test_validate_state(cowork))
    results.append(test_configure_state(cowork))
    results.append(test_validate_state(cowork))  # valida depois de configurar
    results.append(test_render_dry_run(cowork))
    results.append(test_render_real(cowork, workspace))
    results.append(test_files_exist(cowork, workspace))
    results.append(test_placeholders_resolved(cowork))
    results.append(test_area_claude_has_context(cowork))
    results.append(test_resolve_persona_env(cowork))
    results.append(test_resolve_persona_fallback())
    results.append(test_idempotency(cowork))
    results.append(test_find_cowork(cowork))
    results.append(test_fingerprint_diff(cowork))
    results.append(test_post_edit_hook(cowork))
    results.append(test_prompt_intercept_hook())
    results.append(test_audit_clean())

    # Relatorio
    print("RESULTADOS")
    print("-" * 70)
    for r in results:
        print(r)

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    print("-" * 70)
    print(f"Total: {passed}/{total} passaram")
    print()

    # Cleanup
    if args.keep:
        print(f"Diretorio preservado: {workdir}")
    else:
        shutil.rmtree(workdir, ignore_errors=True)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
