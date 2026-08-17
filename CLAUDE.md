# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git: nunca commitar por conta própria

**Nunca execute `git add` nem `git commit`.** Quem decide e executa o commit é a pessoa usuária — sem exceção, e mesmo que o checklist de uma sprint no `PRD.md` traga "fazer o commit" como tarefa. Nesse caso a tarefa é entregar a recomendação, não executá-la; deixe o checkbox aberto para ela marcar depois de commitar.

Ao final de cada sprint — ou de qualquer conjunto significativo de tarefas — **apenas recomende**, com estas três partes:

1. **Quais arquivos** deveriam entrar no commit (e quais deliberadamente ficam de fora, quando relevante)
2. **O comando git** a ser executado
3. **Uma mensagem de commit** em [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`)

Entregue como um bloco de código pronto para copiar e colar.

Comandos git de **leitura** (`git status`, `git diff`, `git log`, `git show`) seguem liberados e são a forma correta de levantar o que mudou antes de recomendar. O que está vedado é qualquer comando que altere o índice, o histórico ou o remoto: `add`, `commit`, `push`, `rm --cached`, `restore`, `checkout`, `reset`, `stash`, `merge`, `rebase`, `tag`. Se algum desses for necessário, recomende-o em vez de rodá-lo.

## Estado atual

Repositório **greenfield**: existe apenas o `PRD.md` e a pasta `design_system/`. Nenhum código Django foi escrito ainda.

`PRD.md` é a especificação autoritativa do projeto. Antes de implementar qualquer coisa, leia a seção relevante dele. As seções mais consultadas:

| Precisa de | Seção do PRD |
| --- | --- |
| Campos e relacionamentos de um model | §7 Modelagem de Dados |
| Comportamento esperado de uma feature | §8 Requisitos Funcionais (RF01–RF17) |
| Camadas de isolamento multi-tenant | §5 |
| Tokens de cor e componentes | §11 Design System |
| Grafos, tools e guardrails de IA | §10 |
| Variáveis de ambiente | §14 |
| Plano de trabalho | §18 Sprints |

O trabalho é conduzido pelas **sprints do §18**, em ordem de dependência. Cada tarefa é um checkbox — marque `- [x]` ao concluir.

## Comandos

Ainda não existem (serão criados na Sprint 0). O PRD §13.4 define os comandos canônicos:

```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt          # após instalar qualquer dependência

python manage.py wait_for_db           # aguarda o Postgres antes de subir
python manage.py check_services        # verifica Postgres, Redis e o broker do Celery
python manage.py migrate
python manage.py seed_demo_data        # dados fake; --tenants --months --reset
python manage.py runserver

celery -A core worker -l info          # terminal separado
celery -A core beat -l info            # terminal separado

./tailwindcss -i static/src/input.css -o static/css/app.css --watch
mkdocs serve -a 127.0.0.1:8001
```

Serviços rodam **nativos** (Homebrew no macOS): `brew services start postgresql@16 redis`.

**Redis acumula três papéis** em databases distintos: `0` broker do Celery, `1` result backend, `2` cache da aplicação. Não há RabbitMQ no projeto — foi removido do escopo (PRD §18, nota de decisão).

**Não há testes automatizados neste projeto** — é uma decisão explícita, não uma lacuna. Não escreva testes nem sugira escrevê-los. Verificação é manual, com `seed_demo_data` como base.

## Invariantes de arquitetura

Estas são as regras cuja violação quebra o projeto. Elas não são deriváveis do código — leia antes de escrever.

**`core` é pacote do projeto E app principal.** Contém `settings.py` (arquivo **único**, sem `settings/` por ambiente), `celery.py` (por isso `celery -A core ...`), `urls.py` e os models `Tenant` e `Plan`. `base` é o app de recursos compartilhados: models abstratos, managers, middleware, mixins, `ProtectedMediaView` e os management commands.

**Multi-tenant shared schema.** Um banco, um schema, coluna `tenant_id` em toda entidade de domínio. Nunca schema-por-tenant nem banco-por-tenant. O isolamento tem cinco camadas encadeadas (PRD §5.2):

1. `TenantMiddleware` resolve o tenant do usuário e publica num `ContextVar`
2. `TenantManager` (o `objects` padrão) filtra automaticamente por esse ContextVar
3. `TenantAwareModel` injeta a FK `tenant` + `created_at`/`updated_at`
4. CBVs herdam `TenantRequiredMixin` e atribuem o tenant no `form_valid` — `tenant` **nunca** vem do POST
5. `RolePermissionMixin` filtra por papel sobre o filtro de tenant

`Model.all_tenants` é o manager irrestrito. Só pode aparecer no admin de superusuário, em management commands e nas tools de IA (que passam `tenant_id` explícito). **Nunca em views.**

**Media nunca é pública.** `MEDIA_URL` não é servida por `static()` nem por nada. Todo download passa por `base.views.ProtectedMediaView`, que checa autenticação → tenant → permissão sobre o objeto pai. Anexo de outro tenant retorna **404**, não 403.

**Nada pesado no request/response.** Toda chamada a LLM, geração de PDF volumoso e recálculo de comissão em lote roda em Celery. O padrão de UI é sempre: loading no botão → aviso "você será notificado" → `Notification` in-app ao concluir.

**Sinistro vincula a `PolicyItem`, não a `Policy`.** Apólice e cliente são derivados de `claim.policy_item.policy` — não duplique como FK. É o que torna estruturalmente impossível um sinistro fora de um item coberto.

**Hierarquia comercial:** Corretora → Agente → Produtor, com `Producer.agent` **nullable** (produtor pode reportar direto à corretora). A comissão vai da seguradora à corretora, que repassa a agente e/ou produtor via `CommissionRule` (resolvida da mais específica para a mais genérica, por `priority`).

## Convenções

- **Aspas simples** em Python. PEP 8, linhas até 100 chars.
- **Código em inglês** (variáveis, classes, funções, comentários, docstrings). **Interface em português brasileiro** (labels, mensagens, e-mails, erros).
- **Class Based Views sempre.** Prefira recursos nativos do Django (`ModelForm`, formsets, `messages`, `Paginator`, `auth`, `django.core.mail`) a equivalentes customizados.
- **Signals só em `signals.py`** do app, conectados via `ready()` do `AppConfig`. Nunca em `models.py` ou `apps.py`.
- Regra de negócio em `services.py`; tasks Celery em `tasks.py`, idempotentes, recebendo **IDs** e não instâncias.
- Todo model tem `created_at` e `updated_at`. Toda entidade de domínio tem `tenant`.
- Unicidade e índices sempre escopados: `UniqueConstraint(fields=['tenant', 'document'])`, índices compostos `(tenant_id, campo)`.
- Um app Django por domínio, criado na raiz (o PRD §6 lista os 22).
- Commits em Conventional Commits.

## Design System

`design_system/design-system.html` é a fonte da verdade visual — mas é só o shell de uma SPA. **Os tokens reais estão em `design_system/css/index-CuopC2LA.css`**: bundle Tailwind/shadcn, paleta neutra monocromática (todos os tokens em hue 0, sat 0%), `--radius: .5rem`, fonte **Inter**, ícones via web component `iconify-icon`. O PRD §11.2 tabela os 23 tokens em claro/escuro.

Não existe cor de marca nesse arquivo — o primário é preto no claro, branco no escuro. Cores de status e das etapas do CRM derivam desses tokens e de `--destructive`.

Nunca introduza cor, fonte, raio ou componente fora desse arquivo. Nada de `#hex` ou `rgb()` em template ou CSS de app: apenas classes utilitárias mapeadas nos tokens do `tailwind.config.js`. Componentes vivem uma única vez em `base/templates/base/components/` — apps não criam variantes próprias.

## IA

LangChain > 1.0 + LangGraph, modelo lido de `OPENAI_MODEL` no `.env` (`gpt-5.5-mini`). Dois agentes: resumo (`ai_agents`, via Celery) e chat (`ai_chat`, streaming SSE).

Toda tool recebe `tenant_id` e `user_id` no estado do grafo e **filtra obrigatoriamente por eles**. Tools são **somente leitura** — nenhuma escrita no banco. O chat aplica escopo duplo: tenant + papel do usuário (um `PRODUCER` só consulta a própria carteira).

## Fora de escopo

Esta fase é **desenvolvimento local nativo + GitHub**. Não gere, sugira ou planeje: conteinerização, orquestração, proxies reversos, gestão de DNS, certificados, provisionamento de servidor remoto, deploy em produção, registries de imagem ou scripts de backup de infraestrutura produtiva.

Se a instalação nativa de Postgres/Redis não for viável, a **única** alternativa aceitável é serviço gerenciado em nuvem no free tier, configurado por `.env`.

Também fora de escopo: testes automatizados, cobrança e planos pagos (só o plano Free é habilitado; os demais mostram "Em breve" desabilitado, sem pedir cartão).

## Documentação

`docs/` é obrigatória e servida por MkDocs Material com Mermaid habilitado (`pymdownx.superfences`). Uma sprint só está concluída com a documentação correspondente atualizada — ver PRD §17 para a estrutura e §19 para a Definition of Done completa.
