# Apps Django

Cada domínio do sistema é isolado em seu próprio app, criado na raiz do projeto. A lista completa dos 22 apps planejados está no `PRD.md` §6.

## Apps existentes

| App | Responsabilidade |
| --- | --- |
| `core` | Pacote do projeto (`settings.py` único, `urls.py`, `celery.py`) e app principal: landing page, `/health/`, e futuramente `Tenant` e `Plan` |
| `base` | Recursos compartilhados: models abstratos, managers, middlewares, mixins, view de media protegida e management commands |
| `accounts` | Usuários com login por e-mail, papéis, convites, autenticação e recuperação de senha — ver [accounts](accounts.md) |

## Módulos do app `base`

| Módulo | Conteúdo |
| --- | --- |
| `constants.py` | `Role` — papéis `OWNER`, `AGENT`, `PRODUCER` |
| `context.py` | ContextVar do tenant corrente e `tenant_context` |
| `managers.py` | `TenantQuerySet` e `TenantManager` |
| `middleware.py` | `TenantMiddleware` |
| `mixins.py` | `TenantRequiredMixin`, `RolePermissionMixin` |
| `models.py` | `TimeStampedModel`, `TenantAwareModel` |
| `validators.py` | `validate_cnpj`, `format_cnpj` |

## Comandos do app `base`

| Comando | Função |
| --- | --- |
| `wait_for_db` | Aguarda o PostgreSQL aceitar conexões, com `--timeout` e `--interval` |
| `check_services` | Reporta o estado de PostgreSQL, Redis e do broker do Celery; `--fail-fast` encerra com código 1 |
| `check_tenant_isolation` | Sonda o isolamento multi-tenant contra o banco real, dentro de transação revertida; `--fail-fast` encerra com código 1 |

### `check_tenant_isolation` não deixa rastro

A sonda cria tabelas temporárias e duas corretoras fictícias, e **tudo é desfeito por
rollback** ao final — inclusive se uma checagem falhar. Rodar o comando repetidamente
sobre um banco com dados reais é seguro: verificado com 5 execuções consecutivas,
25/25 em todas, com contagem de usuários, corretoras e planos idêntica antes e depois.

Os CNPJs das corretoras-sonda são **gerados dinamicamente** e conferidos contra a
tabela antes do uso (`base.validators.build_cnpj`). Documentos fixos fariam o comando
abortar com `IntegrityError` em qualquer banco que já os contivesse.
