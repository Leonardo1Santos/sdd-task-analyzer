"""Módulo principal do TaskAnalyzer.

Gera métricas determinísticas de produtividade a partir de um conjunto de tarefas.
Código gerado via Assistente de IA e homologado pelo desenvolvedor humano.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configuração de logging estruturado
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TaskValidationError(Exception):
    """Exceção customizada para erros de validação temporal ou estrutural de tarefas."""
    pass


def _parse_datetime(dt_value: Optional[Any]) -> Optional[datetime]:
    """Converte valores de data em formato string ISO para objetos datetime."""
    if dt_value is None:
        return None
    if isinstance(dt_value, datetime):
        return dt_value
    if isinstance(dt_value, str):
        try:
            return datetime.fromisoformat(dt_value)
        except ValueError as err:
            raise TaskValidationError(f"Formato de data inválido: {dt_value}") from err
    return None


def analyze_tasks(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analisa um conjunto de tarefas e calcula métricas de produtividade."""
    logger.info("Iniciando análise de %d tarefas.", len(tasks))

    total_tarefas: int = len(tasks)
    total_concluidas: int = 0
    total_pendentes: int = 0
    duracao_total_horas: float = 0.0
    tarefas_atrasadas: int = 0

    metricas_prioridade: Dict[str, Dict[str, Any]] = {
        "BAIXA": {"total": 0, "concluidas": 0, "tempo_medio_horas": 0.0, "taxa_atraso": 0.0, "_duracao_total": 0.0, "_atrasadas": 0},
        "MEDIA": {"total": 0, "concluidas": 0, "tempo_medio_horas": 0.0, "taxa_atraso": 0.0, "_duracao_total": 0.0, "_atrasadas": 0},
        "ALTA": {"total": 0, "concluidas": 0, "tempo_medio_horas": 0.0, "taxa_atraso": 0.0, "_duracao_total": 0.0, "_atrasadas": 0},
    }

    for task in tasks:
        prioridade: str = str(task.get("prioridade", "BAIXA")).upper()
        status: str = str(task.get("status", "PENDENTE")).upper()

        if prioridade in metricas_prioridade:
            metricas_prioridade[prioridade]["total"] += 1

        if status == "CONCLUIDA":
            total_concluidas += 1
            if prioridade in metricas_prioridade:
                metricas_prioridade[prioridade]["concluidas"] += 1

            dt_criacao = _parse_datetime(task.get("data_criacao"))
            dt_conclusao = _parse_datetime(task.get("data_conclusao"))
            dt_limite = _parse_datetime(task.get("data_limite"))

            if dt_conclusao and dt_criacao and dt_conclusao < dt_criacao:
                logger.error("Incoerência de data detectada na tarefa ID %s.", task.get("id"))
                raise TaskValidationError("A data de conclusão não pode ser anterior à data de criação.")

            if dt_conclusao and dt_criacao:
                duracao: float = (dt_conclusao - dt_criacao).total_seconds() / 3600.0
                duracao_total_horas += duracao
                if prioridade in metricas_prioridade:
                    metricas_prioridade[prioridade]["_duracao_total"] += duracao

            if dt_limite and dt_conclusao and dt_conclusao > dt_limite:
                tarefas_atrasadas += 1
                if prioridade in metricas_prioridade:
                    metricas_prioridade[prioridade]["_atrasadas"] += 1

        elif status in ["PENDENTE", "EM_ANDAMENTO"]:
            total_pendentes += 1

    tempo_medio_conclusao_horas: float = (
        round(duracao_total_horas / total_concluidas, 2) if total_concluidas > 0 else 0.0
    )
    taxa_atraso_percentual: float = (
        round((tarefas_atrasadas / total_concluidas) * 100.0, 2) if total_concluidas > 0 else 0.0
    )

    for prio, dados in metricas_prioridade.items():
        qtd_conc = dados["concluidas"]
        dados["tempo_medio_horas"] = round(dados["_duracao_total"] / qtd_conc, 2) if qtd_conc > 0 else 0.0
        dados["taxa_atraso"] = round((dados["_atrasadas"] / qtd_conc) * 100.0, 2) if qtd_conc > 0 else 0.0
        del dados["_duracao_total"]
        del dados["_atrasadas"]

    return {
        "total_tarefas": total_tarefas,
        "total_concluidas": total_concluidas,
        "total_pendentes": total_pendentes,
        "tempo_medio_conclusao_horas": tempo_medio_conclusao_horas,
        "taxa_atraso_percentual": taxa_atraso_percentual,
        "metricas_por_prioridade": metricas_prioridade,
    }