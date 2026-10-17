"""Suíte de testes automatizados (Test Harness) utilizando pytest.

Cobre os Cenários 1 (Sucesso), 2 (Exceção) e Casos de Borda do Contrato SDD.
"""

import pytest
from src.task_analyzer import TaskValidationError, analyze_tasks


def test_cenario_1_sucesso_metricas():
    """Valida o cálculo correto das métricas com dados válidos (Cenário 1)."""
    tasks = [
        {
            "id": 1,
            "titulo": "Implementar Login",
            "prioridade": "ALTA",
            "status": "CONCLUIDA",
            "data_criacao": "2026-09-01T10:00:00",
            "data_conclusao": "2026-09-01T12:00:00",  # 2 horas
            "data_limite": "2026-09-01T13:00:00",      # No prazo
        },
        {
            "id": 2,
            "titulo": "Ajustar Layout",
            "prioridade": "ALTA",
            "status": "CONCLUIDA",
            "data_criacao": "2026-09-01T10:00:00",
            "data_conclusao": "2026-09-01T14:00:00",  # 4 horas
            "data_limite": "2026-09-01T12:00:00",      # Atrasado
        },
        {
            "id": 3,
            "titulo": "Documentar API",
            "prioridade": "BAIXA",
            "status": "PENDENTE",
            "data_criacao": "2026-09-01T10:00:00",
            "data_conclusao": None,
            "data_limite": "2026-09-01T18:00:00",
        },
    ]

    resultado = analyze_tasks(tasks)

    assert resultado["total_tarefas"] == 3
    assert resultado["total_concluidas"] == 2
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 3.0
    assert resultado["taxa_atraso_percentual"] == 50.0
    assert resultado["metricas_por_prioridade"]["ALTA"]["concluidas"] == 2
    assert resultado["metricas_por_prioridade"]["ALTA"]["tempo_medio_horas"] == 3.0


def test_cenario_2_excecao_datas_incoerentes():
    """Valida se a exceção TaskValidationError é disparada em datas inválidas (Cenário 2)."""
    tasks = [
        {
            "id": 99,
            "titulo": "Tarefa Invalida",
            "prioridade": "MEDIA",
            "status": "CONCLUIDA",
            "data_criacao": "2026-09-01T12:00:00",
            "data_conclusao": "2026-09-01T10:00:00",  # Conclusão antes da criação
            "data_limite": "2026-09-01T18:00:00",
        }
    ]

    with pytest.raises(TaskValidationError) as exc_info:
        analyze_tasks(tasks)

    assert "A data de conclusão não pode ser anterior à data de criação." in str(exc_info.value)


def test_caso_borda_lista_vazia():
    """Garante que lista vazia retorne 0.0 sem disparar exceção (Prevenção de Divisão por Zero)."""
    resultado = analyze_tasks([])

    assert resultado["total_tarefas"] == 0
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_caso_borda_apenas_tarefas_pendentes():
    """Garante que lista com 0 tarefas concluídas retorne médiaszeradas de forma segura."""
    tasks = [
        {
            "id": 1,
            "titulo": "Tarefa em Aberto",
            "prioridade": "ALTA",
            "status": "EM_ANDAMENTO",
            "data_criacao": "2026-09-01T10:00:00",
            "data_conclusao": None,
            "data_limite": "2026-09-01T18:00:00",
        }
    ]

    resultado = analyze_tasks(tasks)

    assert resultado["total_tarefas"] == 1
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0