#!/usr/bin/env python3
"""
Hook UserPromptSubmit do plugin Previdenciario-Adv-OS.

Logica (D13 — Ativacao automatica por contexto):
1. Le o prompt via stdin (JSON padrao Claude Code hooks).
2. Detecta bypass explicito: flags `--no-corte`, `--quick`, `--no-suprema`, `/corte off`.
3. Detecta GATILHO PREVIDENCIARIO via keywords (3 niveis):
   - Gatilho 1: prompt contem palavra "previdenciario" (case insensitive)
   - Gatilho 2: keywords fortes do dominio (INSS, CNIS, aposentadoria, BPC, RMI, DER, etc.)
   - Gatilho 3: comandos `/start-previdenciario`, `/previdenciario-master`, etc.
4. Se gatilho dispara:
   - Verifica se `previdenciario/cowork-state.json` existe no path atual
   - SIM: injeta protocolo R1-R4 + aponta para skill `previdenciario-master`
   - NAO: sugere `/start-previdenciario` ao usuario (mas nao bloqueia)
5. Se ha bypass: reafirma em stdout que o bypass foi aceito (transparencia).
6. Se nao eh tarefa previdenciaria nem juridica geral: silencio (exit 0 sem output).

Tambem respeita state.json: se `suprema_corte.enabled = false`, nunca injeta R1-R4.

Stdlib only.
"""

from __future__ import annotations

import io
import json
import os
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location("hook_utils", PLUGIN_ROOT / "scripts" / "hook-utils.py")
hook_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_utils)


# Gatilho 1: palavra "previdenciario" (com/sem acento, case insensitive)
TRIGGER_PREVIDENCIARIO = [
    r"\bprevidenciario\b",
    r"\bprevidenciário\b",
    r"\bprevidenciaria\b",
    r"\bprevidenciária\b",
    r"\bprevidencia\b",
    r"\bprevidência\b",
]

# Gatilho 2: keywords fortes do dominio previdenciario brasileiro
DOMAIN_KEYWORDS = [
    # Regimes
    r"\bRGPS\b", r"\bRPPS\b", r"\bINSS\b", r"\bCRPS\b",
    # Beneficios
    r"\baposentadoria\b", r"\bpensao\b", r"\bpensão\b",
    r"\bauxilio[- ]doenca\b", r"\bauxílio[- ]doença\b",
    r"\bauxilio[- ]acidente\b", r"\bauxílio[- ]acidente\b",
    r"\bauxilio[- ]reclusao\b", r"\bauxílio[- ]reclusão\b",
    r"\bsalario[- ]maternidade\b", r"\bsalário[- ]maternidade\b",
    r"\bBPC\b", r"\bLOAS\b",
    # Documentos previdenciarios
    r"\bCNIS\b", r"\bPPP\b", r"\bLTCAT\b",
    # Termos tecnicos
    r"\bDER\b", r"\bDIB\b", r"\bDCB\b", r"\bRMI\b", r"\bRSA\b",
    r"\bsegurado\b", r"\bcarencia\b", r"\bcarência\b",
    r"\btempo\s+de\s+contribuicao\b", r"\btempo\s+de\s+contribuição\b",
    r"\bsalario[- ]de[- ]beneficio\b", r"\bsalário[- ]de[- ]benefício\b",
    # Atos administrativos
    r"\brequerimento\s+administrativo\b",
    r"\bjunta\s+de\s+recursos\b",
    r"\bcamaras?\s+de\s+julgamento\b", r"\bcâmaras?\s+de\s+julgamento\b",
    r"\bpericia\s+medica\b", r"\bperícia\s+médica\b",
    # Conceitos juridicos
    r"\bEC\s+103\b", r"\bregra\s+de\s+transicao\b", r"\bregra\s+de\s+transição\b",
    r"\bvida\s+toda\b",
    r"\baposentadoria\s+especial\b",
    r"\bdecadencia\b", r"\bdecadência\b",
    # Servidor publico (RPPS)
    r"\bservidor\s+publico\b", r"\bservidor\s+público\b",
    r"\babono\s+permanencia\b", r"\babono\s+permanência\b",
    r"\bparidade\b",
]

# Gatilho 3: commands prefixados do plugin
PLUGIN_COMMANDS = [
    "/start-previdenciario",
    "/previdenciario-master",
    "/peticao-previdenciaria",
    "/recurso-previdenciario",
    "/parecer-previdenciario",
    "/calculo-previdenciario",
    "/revisao-previdenciaria-final",
    "/status-previdenciario",
]

# Keywords juridicas gerais (fallback — se prompt e juridico mas nao previdenciario,
# ainda assim aplica protocolo cauteloso de Suprema Corte)
LEGAL_KEYWORDS_GENERAL = [
    r"\bpeticao\b", r"\bpetição\b", r"\bcontestacao\b", r"\bcontestação\b",
    r"\brecurso\b", r"\bapelacao\b", r"\bapelação\b",
    r"\bembargos\b", r"\breplica\b", r"\bréplica\b",
    r"\bparecer\b", r"\bjurisprudencia\b", r"\bjurisprudência\b",
    r"\bsentenca\b", r"\bsentença\b", r"\bdecisao\b", r"\bdecisão\b",
    r"\baudiencia\b", r"\baudiência\b", r"\bprocesso\b",
]

BYPASS_TOKENS = [
    "--no-corte",
    "--no-suprema",
    "--quick",
    "/corte off",
    "/corte-off",
]


def _load_input() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception:
        return {}


def _matches_any(text: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _is_previdenciario(prompt: str) -> bool:
    """Detecta se o prompt e do dominio previdenciario (gatilhos 1, 2 ou 3)."""
    # Gatilho 1: palavra "previdenciario"
    if _matches_any(prompt, TRIGGER_PREVIDENCIARIO):
        return True
    # Gatilho 2: keyword forte do dominio
    if _matches_any(prompt, DOMAIN_KEYWORDS):
        return True
    # Gatilho 3: command do plugin
    low = prompt.lower()
    for cmd in PLUGIN_COMMANDS:
        if cmd.lower() in low:
            return True
    return False


def _is_legal_general(prompt: str) -> bool:
    """Detecta se e tarefa juridica em geral (mesmo nao sendo previdenciaria)."""
    return _matches_any(prompt, LEGAL_KEYWORDS_GENERAL)


def _has_bypass(prompt: str) -> str | None:
    low = prompt.lower()
    for token in BYPASS_TOKENS:
        if token in low:
            return token
    return None


def _has_previdenciario_state(cowork: Path | None) -> bool:
    """Verifica se existe `previdenciario/cowork-state.json` no path."""
    if cowork is None:
        return False
    return (cowork / "previdenciario" / "cowork-state.json").exists()


def _suprema_corte_enabled(cowork: Path | None) -> bool:
    """Le state.json e verifica suprema_corte.enabled. Default true se ausente."""
    if cowork is None:
        return True
    sf = cowork / "previdenciario" / "cowork-state.json"
    if not sf.exists():
        return True
    try:
        state = json.loads(sf.read_text(encoding="utf-8"))
        return bool(state.get("suprema_corte", {}).get("enabled", True))
    except Exception:
        return True


def _resolve_cowork() -> Path | None:
    """Resolve COWORK root via env PREVIDENCIARIO_COWORK_PATH ou cwd ancestral."""
    # Prefere env nova
    env = os.environ.get("PREVIDENCIARIO_COWORK_PATH") or os.environ.get("COWORK_PATH")
    if env:
        p = Path(env)
        if (p / "previdenciario" / "cowork-state.json").exists():
            return p
    # Fallback: hook_utils.find_cowork procura ancestralmente
    return hook_utils.find_cowork(Path.cwd())


def main() -> int:
    payload = _load_input()
    prompt = payload.get("prompt") or payload.get("user_prompt") or ""
    if not isinstance(prompt, str) or not prompt.strip():
        return 0

    cowork = _resolve_cowork()
    bypass = _has_bypass(prompt)

    is_prev = _is_previdenciario(prompt)
    is_legal_other = _is_legal_general(prompt) and not is_prev

    # Caso 1: bypass explicito
    if bypass and (is_prev or is_legal_other):
        sys.stdout.write(
            f"[previdenciario-adv-os] Bypass detectado ({bypass}). "
            "Pecas, recursos, pareceres e calculos serao entregues SEM validacao "
            "da Suprema Corte (R1-R4). Use por sua conta e risco.\n"
        )
        return 0

    # Caso 2: tarefa previdenciaria + plugin configurado
    if is_prev and _has_previdenciario_state(cowork):
        if not _suprema_corte_enabled(cowork):
            # Operador desabilitou Suprema Corte na configuracao — apenas notifica
            sys.stdout.write(
                "[previdenciario-adv-os] Demanda previdenciaria detectada. "
                "Suprema Corte DESATIVADA na configuracao. Aciono apenas a cadeia de skills.\n"
                "Acionar skill: previdenciario-master.\n"
            )
        else:
            sys.stdout.write(
                "[previdenciario-adv-os] Demanda previdenciaria detectada. Plugin ativado.\n"
                "\n"
                "PROTOCOLO AUTOMATICO:\n"
                "1. Acionar skill `previdenciario-master` (Tier 0 — sempre ativa)\n"
                "2. Aplicar Hierarquia das 4 Camadas (1-Proibicoes, 2-Protocolos, 3-Estilo, 4-Skills)\n"
                "3. Verificar 22 Proibicoes Absolutas (PA-01 a PA-22), com atencao especial:\n"
                "   - PA-09: decadencia/prescricao em revisoes\n"
                "   - PA-13: CNIS obrigatorio\n"
                "   - PA-14: requerimento administrativo (Tema 350 STF)\n"
                "   - PA-15: competencia (RGPS=Justica Federal, RPPS=Comum, Acidentario=Comum)\n"
                "   - PA-21: zero CDC contra INSS\n"
                "4. Acionar Protocolos da Camada 2 conforme demanda\n"
                "5. Antes de entregar: Suprema Corte R1->R2->R3->R4 (PA-22)\n"
                "\n"
                "Bypass disponivel: `--no-corte`, `--quick`, `/corte off`.\n"
            )
        return 0

    # Caso 3: tarefa previdenciaria mas plugin NAO configurado
    if is_prev and not _has_previdenciario_state(cowork):
        sys.stdout.write(
            "[previdenciario-adv-os] Detectei demanda previdenciaria, mas o plugin "
            "ainda nao foi configurado neste diretorio.\n"
            "\n"
            "RECOMENDACAO: rode /start-previdenciario para configurar (~5 min).\n"
            "Vou criar uma pasta `previdenciario/` aqui com sua identidade, tom de voz "
            "e configuracao das skills previdenciarias.\n"
            "\n"
            "Caso queira prosseguir SEM configurar, trabalho em modo fallback generico "
            "(persona neutra, qualidade reduzida). Apenas avise.\n"
        )
        return 0

    # Caso 4: tarefa juridica geral (nao previdenciaria) — manter protocolo cauteloso original
    if is_legal_other:
        sys.stdout.write(
            "[previdenciario-adv-os] Tarefa juridica detectada (nao especificamente previdenciaria). "
            "Aplique protocolo padrao:\n"
            "1. Questionamento previo (sem suposicoes silenciosas).\n"
            "2. Apresentar estrutura + premissas antes de redigir.\n"
            "3. Aguardar confirmacao do usuario.\n"
            "4. Antes de entregar: executar Suprema Corte R1-R4 se aplicavel.\n"
            "Bypass: `--no-corte`, `--quick`, `/corte off`.\n"
        )
        return 0

    # Caso default: nao e tarefa juridica, nem previdenciaria — silencio
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
