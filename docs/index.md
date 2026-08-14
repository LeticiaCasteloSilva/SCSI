# SCSI — Documentação

**Sistema de Gestão para Corretora de Seguros Inteligente** — plataforma multi-tenant para corretoras de seguros, com agentes de IA construídos em LangChain e LangGraph.

A especificação completa do produto está no [`PRD.md`](https://github.com/LeticiaCasteloSilva/SCSI/blob/main/PRD.md) na raiz do repositório. Esta documentação registra o que já está **implementado**.

## Estado atual

Sprint 0 — Fundação do projeto e ambiente local.

| Componente | Estado |
| --- | --- |
| Python 3.13 + `.venv` | Pronto |
| Django 6.1 com `settings.py` único | Pronto |
| PostgreSQL 16 nativo | Pronto |
| Redis 7.4 nativo | Pronto |
| RabbitMQ (broker do Celery) | Pendente de configuração |
| Endpoint `GET /health/` | Pronto |
| Commands `wait_for_db` e `check_services` | Pronto |

## Por onde começar

- [Ambiente local](setup/ambiente-local.md) — instalação dos serviços e execução do projeto
- [Arquitetura multi-tenant](arquitetura/multi-tenant.md) — como o isolamento entre corretoras funciona
