# SCSI — Documentação

**Sistema de Gestão para Corretora de Seguros Inteligente** — plataforma multi-tenant para corretoras de seguros, com agentes de IA construídos em LangChain e LangGraph.

A especificação completa do produto está no [`PRD.md`](https://github.com/LeticiaCasteloSilva/SCSI/blob/main/PRD.md) na raiz do repositório. Esta documentação registra o que já está **implementado**.

## Estado atual

Sprints 0 a 2 — fundação do ambiente, núcleo multi-tenant e autenticação.

| Componente | Estado |
| --- | --- |
| Python 3.13 + `.venv` | Pronto |
| Django 6.1 com `settings.py` único | Pronto |
| PostgreSQL 16 nativo | Pronto |
| Redis 7.4 nativo (cache, broker e result backend) | Pronto |
| Celery (worker + beat) com broker Redis | Pronto |
| Endpoint `GET /health/` | Pronto |
| Commands `wait_for_db` e `check_services` | Pronto |
| Núcleo multi-tenant (`Tenant`, `Plan`, managers, middleware, mixins) | Pronto |
| Autenticação por e-mail, papéis, convites e recuperação de senha | Pronto |

## Por onde começar

- [Ambiente local](setup/ambiente-local.md) — instalação dos serviços e execução do projeto
- [Arquitetura multi-tenant](arquitetura/multi-tenant.md) — como o isolamento entre corretoras funciona
- [accounts](apps/accounts.md) — login por e-mail, papéis e convites
