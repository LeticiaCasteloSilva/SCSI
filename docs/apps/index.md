# Apps Django

Cada domínio do sistema é isolado em seu próprio app, criado na raiz do projeto. A lista completa dos 22 apps planejados está no `PRD.md` §6.

## Apps existentes

| App | Responsabilidade |
| --- | --- |
| `core` | Pacote do projeto (`settings.py` único, `urls.py`, `celery.py`) e app principal: landing page, `/health/`, e futuramente `Tenant` e `Plan` |
| `base` | Recursos compartilhados: models abstratos, managers, middlewares, mixins, view de media protegida e management commands |

## Comandos do app `base`

| Comando | Função |
| --- | --- |
| `wait_for_db` | Aguarda o PostgreSQL aceitar conexões, com `--timeout` e `--interval` |
| `check_services` | Reporta o estado de PostgreSQL, Redis e RabbitMQ; `--fail-fast` encerra com código 1 |
