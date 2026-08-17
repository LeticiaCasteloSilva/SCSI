# PRD — SCSI (Sistema de Gestão para Corretora de Seguros Inteligente)

| Campo | Valor |
| --- | --- |
| Produto | SCSI — Sistema de Gestão para Corretora de Seguros Inteligente |
| Versão do documento | 1.0 |
| Data | 2026-08-13 |
| Responsável técnico | Engenharia SCSI |
| Status | Aprovado para desenvolvimento |
| Escopo desta versão | Desenvolvimento **local nativo** + versionamento no **GitHub** |

---

## Índice

1. [Visão Geral do Produto](#1-visão-geral-do-produto)
2. [Escopo e Não-Escopo](#2-escopo-e-não-escopo)
3. [Personas e Papéis](#3-personas-e-papéis)
4. [Stack Tecnológica](#4-stack-tecnológica)
5. [Arquitetura Multi-Tenant](#5-arquitetura-multi-tenant)
6. [Estrutura de Apps Django](#6-estrutura-de-apps-django)
7. [Modelagem de Dados](#7-modelagem-de-dados)
8. [Requisitos Funcionais](#8-requisitos-funcionais)
9. [Requisitos Não Funcionais](#9-requisitos-não-funcionais)
10. [Camada de IA (LangChain + LangGraph)](#10-camada-de-ia-langchain--langgraph)
11. [Design System](#11-design-system)
12. [Segurança e Arquivos de Media Protegidos](#12-segurança-e-arquivos-de-media-protegidos)
13. [Infraestrutura de Desenvolvimento Local (Nativa)](#13-infraestrutura-de-desenvolvimento-local-nativa)
14. [Variáveis de Ambiente](#14-variáveis-de-ambiente)
15. [Estrutura de Pastas](#15-estrutura-de-pastas)
16. [Convenções de Código](#16-convenções-de-código)
17. [Documentação (MkDocs)](#17-documentação-mkdocs)
18. [Sprints de Desenvolvimento](#18-sprints-de-desenvolvimento)
19. [Definition of Done](#19-definition-of-done)
20. [Matriz de Rastreabilidade](#20-matriz-de-rastreabilidade)

---

## 1. Visão Geral do Produto

### 1.1 Resumo

O **SCSI** é uma plataforma SaaS multi-tenant de gestão para corretoras de seguros. Cada corretora (tenant) opera dentro de um espaço de dados rigidamente isolado, gerenciando toda a cadeia operacional do negócio: clientes, seguradoras, ramos, itens cobertos, propostas, apólices, endossos, renovações, sinistros, comissões e pipeline comercial (CRM).

A camada diferencial do produto é a **inteligência aplicada**: agentes de IA construídos com LangChain e LangGraph, com acesso controlado ao banco de dados da própria corretora, capazes de (a) resumir automaticamente registros complexos e (b) responder perguntas em linguagem natural sobre a operação, via chat com resposta em streaming.

### 1.2 Problema

Corretoras de seguros de pequeno e médio porte operam hoje com planilhas, e-mail e sistemas legados fragmentados. Como consequência:

- Perdem renovações por falta de alerta e acompanhamento.
- Não têm visibilidade sobre o funil comercial nem sobre a produtividade de agentes e produtores.
- Calculam comissões manualmente, com erro frequente no repasse em cadeia (corretora → agente → produtor).
- Gastam tempo relendo históricos longos de sinistros e apólices para entender o contexto de um caso.

### 1.3 Proposta de valor

| Dor | Resposta do SCSI |
| --- | --- |
| Dados espalhados em planilhas | Cadastro único e relacionado de toda a operação |
| Renovações perdidas | App de Renovações com controle de vencimento e status |
| Comissão calculada à mão | Motor de regras de comissão com repasse em cadeia e relatórios |
| Funil comercial invisível | CRM em grid e kanban + gráfico de funil no dashboard |
| Leitura lenta de históricos | Botão "Resumir com IA" em Cliente, Proposta, Apólice, Sinistro e Negociação |
| Perguntas operacionais sem resposta rápida | Chat com agente de IA, com tools de consulta ao banco do tenant |
| Anexos sensíveis expostos | Media servida exclusivamente por view protegida com checagem de tenant e permissão |

### 1.4 Objetivos desta fase

1. Sistema completo funcionando em ambiente **local nativo**, sem containers.
2. Código versionado no **GitHub**, com histórico limpo e `README.md` de setup reproduzível.
3. Base de dados fake carregável por management command, cobrindo múltiplos cenários e datas variadas, suficiente para demonstração ponta a ponta.
4. Documentação viva em `docs/`, servida via MkDocs, com diagramas Mermaid.

### 1.5 Métricas de sucesso da fase

| Métrica | Alvo |
| --- | --- |
| Setup local a partir do `README.md` | Ambiente rodando em < 30 minutos |
| Cobertura dos 17 requisitos funcionais | 100% |
| Rotas sensíveis sem autenticação | 0 |
| Vazamento cross-tenant em qualquer listagem | 0 |
| Operação de IA bloqueando o request/response | 0 |

---

## 2. Escopo e Não-Escopo

### 2.1 No escopo

- Aplicação Django multi-tenant (shared schema) rodando localmente via `runserver`.
- PostgreSQL e Redis instalados nativamente no sistema operacional.
- Celery worker e beat executados localmente em terminais separados.
- Agentes de IA com LangChain e LangGraph via API da OpenAI.
- Interface web responsiva server-rendered, aderente ao design system.
- Documentação MkDocs e carga de dados fake.
- Versionamento no GitHub.

### 2.2 Fora do escopo (decisão explícita)

Os itens abaixo estão **excluídos por decisão de produto** e não devem ser produzidos, sugeridos ou planejados nesta fase:

- Qualquer forma de conteinerização ou orquestração de containers.
- Provisionamento de servidores remotos ou deploy em ambiente de produção.
- Balanceadores, proxies reversos, gestão de DNS ou emissão de certificados.
- Registries de imagens, pipelines de publicação ou scripts de backup de infraestrutura produtiva.
- Testes automatizados (regra técnica explícita: **não implementar testes** nesta fase).
- Cobrança, gateway de pagamento ou planos pagos ativos (somente o plano **Free** é habilitado).

Qualquer ambiguidade futura deve ser resolvida sempre na direção que mantém o escopo em **desenvolvimento local nativo + GitHub**.

---

## 3. Personas e Papéis

### 3.1 Papéis do sistema

| Papel | Código | Descrição | Visibilidade de dados |
| --- | --- | --- | --- |
| Dono / Admin | `OWNER` | Dono da corretora. Configura o tenant, convida usuários, define regras de comissão e pipelines. | Todos os dados do tenant |
| Agente | `AGENT` | Pessoa física ou empresa parceira que agrega produtores. | Dados próprios + dos produtores vinculados a ele |
| Produtor | `PRODUCER` | Corretor final, origina o negócio. Pode ou não estar vinculado a um agente. | Somente os dados de que é proprietário |

O papel é atributo do usuário dentro do tenant. Um usuário pertence a **exatamente um** tenant.

### 3.2 Hierarquia comercial

```mermaid
graph TD
    T[Corretora / Tenant] --> A1[Agente A]
    T --> A2[Agente B]
    T --> P3[Produtor C - direto da corretora]
    A1 --> P1[Produtor A1]
    A1 --> P2[Produtor A2]
    A2 --> P4[Produtor B1]
```

Regras da hierarquia:

- Uma corretora possui **N** agentes.
- Um agente possui **N** produtores.
- Um produtor pode estar vinculado a um agente **ou** reportar diretamente à corretora (`agent` nulo).
- A comissão é paga pela **seguradora → corretora**. A corretora repassa percentuais configuráveis para **agente** e/ou **produtor**.

---

## 4. Stack Tecnológica

### 4.1 Núcleo

| Camada | Tecnologia | Versão | Justificativa |
| --- | --- | --- | --- |
| Linguagem | Python | > 3.13 | Padrão obrigatório do projeto |
| Framework web | Django | > 6.0 | Class Based Views, ORM, admin, auth e e-mail nativos |
| Banco de dados | PostgreSQL | 16+ | Obrigatório; suporte a índices compostos e JSONB |
| Cache | Redis | 7+ | Cache da aplicação, broker e result backend do Celery |
| Broker de mensagens | Redis | 7+ | Broker do Celery, em database dedicado |
| Fila assíncrona | Celery | 5.4+ | Tarefas pesadas, especialmente IA |
| Agendamento | Celery Beat | 5.4+ | Rotinas periódicas (renovações, alertas) |
| Observabilidade de tasks | `dj-celery-panel` | última | Visualização das tasks no admin do Django |
| Configuração | `django-environ` | última | Leitura de `.env` no `settings.py` |
| Ambiente virtual | `venv` (`.venv`) | — | Obrigatório na raiz do projeto |

### 4.2 Inteligência artificial

| Componente | Tecnologia | Papel |
| --- | --- | --- |
| Orquestração | LangChain > 1.0 | Abstração de LLM, tools e prompts |
| Grafo de agentes | LangGraph | Fluxo de estados dos agentes (resumo e chat) |
| Modelo | `gpt-5.5-mini` via API da OpenAI | Único modelo permitido; id lido do `.env` |
| Execução | Celery | Resumos assíncronos, nunca no request |
| Streaming | `StreamingHttpResponse` (SSE) | Resposta do chat em efeito stream |

### 4.3 Frontend e documentos

| Necessidade | Tecnologia | Observação |
| --- | --- | --- |
| Renderização | Django Templates | Server-side rendering, CBVs |
| CSS | Tailwind CSS (CLI standalone) | Tokens extraídos do design system |
| Interatividade | HTMX + Alpine.js | Parciais, modais, polling de notificação |
| Drag & drop (kanban) | SortableJS | Cards arrastáveis entre etapas |
| Gráficos | Chart.js | Dashboard, incluindo gráfico de funil |
| Ícones | Iconify (`iconify-icon`) | Já presente no design system |
| Tipografia | Inter | Fonte oficial do design system |
| Markdown → HTML | `markdown` + `bleach` (servidor) / `marked` (stream) | Renderização das respostas do chat |
| PDF | **ReportLab** + **PyPDF** | Obrigatório para todos os relatórios em PDF |
| CSV | `csv` (stdlib) + `StreamingHttpResponse` | Exportação de relatórios |
| Documentação | MkDocs + Material + Mermaid | Pasta `docs/` sempre atualizada |

### 4.4 Dependências principais (`requirements.txt`)

O arquivo `requirements.txt` fica **na raiz** e deve ser atualizado a cada nova dependência instalada.

> `kombu` é a camada de transporte do próprio Celery — é ela que implementa `kombu.transport.redis`. Ela puxa `amqp` como dependência transitiva mesmo sem RabbitMQ no projeto; nenhum dos dois deve ser removido.

```
Django>=6.0
psycopg[binary]
django-environ
celery
kombu
redis
django-redis
dj-celery-panel
langchain
langgraph
langchain-openai
openai
reportlab
pypdf
markdown
bleach
Pillow
python-magic
mkdocs
mkdocs-material
pymdown-extensions
Faker
```

---

## 5. Arquitetura Multi-Tenant

### 5.1 Modelo adotado — Shared Schema

O SCSI usa **exclusivamente** o modelo de **schema compartilhado**: um único banco PostgreSQL, um único schema, e uma coluna `tenant_id` em toda tabela de domínio. Não existe schema por tenant nem banco por tenant.

| Aspecto | Decisão |
| --- | --- |
| Banco | Único, compartilhado |
| Schema | Único (`public`) |
| Discriminador | Coluna `tenant_id` (FK para `core.Tenant`) |
| Isolamento | Manager/QuerySet + middleware + permissões |
| Migrações | Uma execução única de `migrate` para todos os tenants |

### 5.2 Camadas de isolamento

```mermaid
graph TD
    R[Request HTTP] --> AM[AuthenticationMiddleware]
    AM --> TM[TenantMiddleware]
    TM --> CV[ContextVar: current_tenant]
    CV --> V[Class Based View + TenantRequiredMixin]
    V --> M[TenantManager filtra por current_tenant]
    M --> DB[(PostgreSQL - shared schema)]
    V --> P[Checagem de papel: OWNER / AGENT / PRODUCER]
```

**Camada 1 — Middleware.** `base.middleware.TenantMiddleware` resolve o tenant a partir de `request.user.tenant`, publica-o em um `ContextVar` e o anexa como `request.tenant`. Usuário autenticado sem tenant ativo é deslogado.

**Camada 2 — Manager e QuerySet.** `base.managers.TenantQuerySet` e `TenantManager` filtram automaticamente por `current_tenant` do contexto. O manager padrão (`objects`) é sempre o filtrado. Um manager irrestrito (`all_tenants`) existe apenas para uso do admin de superusuário e de management commands, nunca em views.

**Camada 3 — Model abstrato.** Toda entidade de domínio herda de `base.models.TenantAwareModel`, que injeta `tenant` (FK obrigatória, `on_delete=CASCADE`, `db_index=True`) e os campos de auditoria.

**Camada 4 — Views.** Todas as CBVs herdam de `base.mixins.TenantRequiredMixin` (que compõe `LoginRequiredMixin`) e, quando aplicável, `RolePermissionMixin`. Todo formulário atribui o tenant no `form_valid`, nunca aceitando `tenant` como campo do POST.

**Camada 5 — Permissões por papel.** Sobre o filtro de tenant aplica-se o filtro de escopo por papel: `OWNER` vê tudo do tenant; `AGENT` vê o próprio escopo e o dos produtores vinculados; `PRODUCER` vê apenas o que lhe pertence.

### 5.3 Models base (app `base`)

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantAwareModel(TimeStampedModel):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE, db_index=True)

    objects = TenantManager()
    all_tenants = models.Manager()

    class Meta:
        abstract = True
```

> **Regra invariante:** todo model do sistema possui `created_at` e `updated_at`. Toda entidade de domínio possui `tenant`.

### 5.4 Regras de integridade cross-tenant

- Toda FK entre entidades de domínio é validada no `clean()` para garantir que ambos os lados pertencem ao mesmo tenant.
- Índices compostos `(tenant_id, <campo de busca>)` em todos os campos usados em filtros e ordenações.
- Constraints de unicidade sempre escopadas ao tenant: `UniqueConstraint(fields=['tenant', 'document'])`.

---

## 6. Estrutura de Apps Django

Cada domínio é isolado em seu próprio app, criado na **raiz do projeto**.

| # | App | Responsabilidade | Models principais |
| --- | --- | --- | --- |
| 1 | `core` | App principal e pacote do projeto: `settings.py` único, `urls.py`, `celery.py`, tenant/corretora, planos, landing page, `/health/` | `Tenant`, `Plan` |
| 2 | `base` | Recursos compartilhados: models abstratos, managers, middlewares, mixins, permissões, view de media protegida, management commands, template tags | — (abstratos) |
| 3 | `accounts` | Usuários com login por e-mail, papéis, convites, autenticação e recuperação de senha | `User`, `Invitation` |
| 4 | `clients` | Cadastro de clientes PF e PJ | `Client`, `ClientContact` |
| 5 | `insurers` | Cadastro de seguradoras | `Insurer` |
| 6 | `lines` | Cadastro de ramos de seguro | `InsuranceLine` |
| 7 | `covered_items` | Itens cobertos (veículo, imóvel, frota, viagem, vida etc.) | `CoveredItem` |
| 8 | `proposals` | Propostas e geração de apólice | `Proposal`, `ProposalItem` |
| 9 | `policies` | Apólices e parcelas | `Policy`, `PolicyItem`, `PolicyInstallment` |
| 10 | `endorsements` | Endossos sobre apólices | `Endorsement` |
| 11 | `renewals` | Renovações de apólices | `Renewal` |
| 12 | `claims` | Sinistros vinculados a item coberto de apólice | `Claim`, `ClaimEvent` |
| 13 | `attachments` | Anexos genéricos e entrega protegida de media | `Attachment` |
| 14 | `agents` | Agentes (pessoa ou empresa parceira) | `Agent` |
| 15 | `producers` | Produtores (corretor final) | `Producer` |
| 16 | `commissions` | Regras, cálculo e repasse de comissões | `CommissionRule`, `CommissionEntry` |
| 17 | `crm` | Pipeline personalizável, negociações, grid e kanban | `Pipeline`, `PipelineStage`, `Deal`, `DealActivity` |
| 18 | `dashboard` | Métricas agregadas, gráficos e funil | — (serviços de agregação) |
| 19 | `reports` | Tela de relatórios, exportação PDF e CSV | `ReportExecution` |
| 20 | `notifications` | Notificações in-app | `Notification` |
| 21 | `ai_agents` | Agente de resumo (LangGraph), tools de banco, tasks Celery | `AISummaryRun` |
| 22 | `ai_chat` | Chat com sessões salvas e resposta em stream | `ChatSession`, `ChatMessage` |

> `core` acumula o papel de pacote do projeto (onde vivem `settings.py` e `celery.py`, permitindo `celery -A core worker`) e de app principal registrado em `INSTALLED_APPS`.

---

## 7. Modelagem de Dados

### 7.1 Diagrama de relacionamentos

```mermaid
erDiagram
    TENANT ||--o{ USER : possui
    TENANT ||--o{ AGENT : possui
    TENANT ||--o{ PRODUCER : possui
    TENANT ||--o{ CLIENT : possui
    TENANT ||--o{ INSURER : possui
    TENANT ||--o{ INSURANCE_LINE : possui
    AGENT ||--o{ PRODUCER : agrega
    CLIENT ||--o{ COVERED_ITEM : possui
    CLIENT ||--o{ PROPOSAL : origina
    PROPOSAL ||--o{ PROPOSAL_ITEM : contem
    COVERED_ITEM ||--o{ PROPOSAL_ITEM : referencia
    PROPOSAL ||--o| POLICY : gera
    POLICY ||--o{ POLICY_ITEM : contem
    COVERED_ITEM ||--o{ POLICY_ITEM : referencia
    POLICY ||--o{ POLICY_INSTALLMENT : parcela
    POLICY ||--o{ ENDORSEMENT : altera
    POLICY ||--o| RENEWAL : renova
    POLICY_ITEM ||--o{ CLAIM : sofre
    POLICY ||--o{ COMMISSION_ENTRY : gera
    PIPELINE ||--o{ PIPELINE_STAGE : contem
    PIPELINE_STAGE ||--o{ DEAL : agrupa
    DEAL ||--o| PROPOSAL : converte
    TENANT ||--o{ ATTACHMENT : possui
    TENANT ||--o{ NOTIFICATION : possui
    USER ||--o{ CHAT_SESSION : possui
    CHAT_SESSION ||--o{ CHAT_MESSAGE : contem
```

### 7.2 `core`

**`Plan`** — planos comerciais. Somente o plano Free fica habilitado.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `name` | CharField | Free, Pro, Business |
| `slug` | SlugField | único |
| `price` | DecimalField | informativo |
| `is_enabled` | BooleanField | `True` apenas no Free |
| `max_users` | PositiveIntegerField | limite do plano |
| `description` | TextField | exibido na landing |
| `created_at` / `updated_at` | DateTimeField | auditoria |

**`Tenant`** — a corretora.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `legal_name` | CharField | **Razão Social — obrigatório** |
| `trade_name` | CharField | nome fantasia |
| `cnpj` | CharField(18) | **obrigatório e único**, validado |
| `slug` | SlugField | único |
| `plan` | FK → `Plan` | Free por padrão |
| `email`, `phone` | CharField | contato |
| `susep_code` | CharField | registro SUSEP, opcional |
| `logo` | ImageField | media protegida |
| `is_active` | BooleanField | — |
| `created_at` / `updated_at` | DateTimeField | auditoria |

### 7.3 `accounts`

**`User`** — herda de `AbstractBaseUser` + `PermissionsMixin`.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `email` | EmailField | **único; `USERNAME_FIELD = 'email'`** |
| `full_name` | CharField | — |
| `tenant` | FK → `Tenant` | nulo somente para superusuário |
| `role` | CharField(choices) | `OWNER`, `AGENT`, `PRODUCER` |
| `phone` | CharField | — |
| `avatar` | ImageField | media protegida |
| `is_active`, `is_staff` | BooleanField | — |
| `created_at` / `updated_at` | DateTimeField | auditoria |

Não existe campo `username`. `REQUIRED_FIELDS = ['full_name']`. `UserManager` customizado com `create_user` / `create_superuser` por e-mail.

**`Invitation`** — convite de usuário para o tenant: `tenant`, `email`, `role`, `token`, `expires_at`, `accepted_at`, auditoria.

### 7.4 `agents` e `producers`

**`Agent`**: `tenant`, `user` (OneToOne opcional), `kind` (`INDIVIDUAL` / `COMPANY`), `name`, `document` (CPF/CNPJ), `email`, `phone`, `default_commission_percentage`, `is_active`, auditoria. Unicidade `(tenant, document)`.

**`Producer`**: `tenant`, `user` (OneToOne opcional), `agent` (FK **nullable** → `Agent`), `name`, `document`, `email`, `phone`, `default_commission_percentage`, `is_active`, auditoria. `agent` nulo significa produtor direto da corretora.

### 7.5 Cadastros base

**`Client`**: `tenant`, `kind` (`INDIVIDUAL` / `COMPANY`), `name`, `legal_name`, `document`, `birth_date`, `email`, `phone`, endereço completo, `producer` (FK), `agent` (FK), `notes`, `ai_summary`, `ai_summary_generated_at`, `is_active`, auditoria.

**`Insurer`**: `tenant`, `name`, `cnpj`, `susep_code`, `contact_email`, `contact_phone`, `website`, `logo`, `is_active`, auditoria.

**`InsuranceLine`** (Ramo): `tenant`, `code`, `name`, `category` (`AUTO`, `PROPERTY`, `FLEET`, `TRAVEL`, `LIFE`, `HEALTH`, `OTHER`), `description`, `is_active`, auditoria.

**`CoveredItem`**: `tenant`, `client` (FK), `line` (FK), `item_type` (`VEHICLE`, `PROPERTY`, `FLEET`, `TRAVEL`, `LIFE`, `OTHER`), `description`, `insured_value`, `attributes` (JSONField com os campos específicos do tipo — placa/chassi/ano para veículo, endereço/metragem para imóvel, destino/datas para viagem, beneficiários para vida), `is_active`, auditoria.

### 7.6 Propostas e apólices

**`Proposal`**: `tenant`, `number` (único por tenant), `client`, `insurer`, `line`, `producer`, `agent`, `status` (`DRAFT`, `SENT`, `UNDER_ANALYSIS`, `APPROVED`, `REJECTED`, `CONVERTED`), `premium_amount`, `net_amount`, `commission_percentage`, `valid_until`, `coverage_start`, `coverage_end`, `payment_method`, `installments_count`, `notes`, `ai_summary`, `ai_summary_generated_at`, `generated_policy` (OneToOne nullable → `Policy`), auditoria.

**`ProposalItem`**: `tenant`, `proposal`, `covered_item`, `insured_value`, `premium_amount`, `deductible`, `coverages` (JSONField), auditoria. Uma proposta tem **N** itens cobertos.

**`Policy`**: `tenant`, `number`, `proposal` (FK nullable — origem), `client`, `insurer`, `line`, `producer`, `agent`, `status` (`ACTIVE`, `EXPIRED`, `CANCELLED`, `RENEWED`), `premium_amount`, `net_amount`, `commission_percentage`, `start_date`, `end_date`, `payment_method`, `installments_count`, `ai_summary`, `ai_summary_generated_at`, auditoria. Índices `(tenant, status)` e `(tenant, end_date)`.

**`PolicyItem`**: `tenant`, `policy`, `covered_item`, `insured_value`, `premium_amount`, `deductible`, `coverages` (JSONField), auditoria. **É a este model que o sinistro se vincula.**

**`PolicyInstallment`**: `tenant`, `policy`, `number`, `due_date`, `amount`, `status` (`PENDING`, `PAID`, `OVERDUE`), `paid_at`, auditoria.

**`Endorsement`**: `tenant`, `policy`, `number`, `kind` (`INCLUSION`, `EXCLUSION`, `CHANGE`, `CANCELLATION`, `VALUE_ADJUSTMENT`), `description`, `effective_date`, `premium_difference`, `status` (`DRAFT`, `SENT`, `APPROVED`, `REJECTED`), auditoria.

**`Renewal`**: `tenant`, `original_policy`, `new_policy` (nullable), `status` (`PENDING`, `IN_NEGOTIATION`, `RENEWED`, `LOST`), `due_date`, `renewed_premium_amount`, `responsible` (FK → `User`), `notes`, auditoria.

### 7.7 `claims`

**`Claim`**: `tenant`, `number`, `policy_item` (FK **obrigatória** → `PolicyItem`), `occurred_at`, `reported_at`, `kind`, `description`, `status` (`OPENED`, `UNDER_ANALYSIS`, `APPROVED`, `DENIED`, `SETTLED`, `CLOSED`), `claimed_amount`, `settled_amount`, `insurer_protocol`, `responsible`, `ai_summary`, `ai_summary_generated_at`, auditoria.

> A apólice e o cliente do sinistro são derivados de `policy_item.policy` — nunca duplicados como FK direta, garantindo que **todo sinistro esteja sempre vinculado a um item coberto de uma apólice**.

**`ClaimEvent`**: `tenant`, `claim`, `event_type`, `description`, `occurred_at`, `created_by`, auditoria — timeline do sinistro.

### 7.8 `commissions`

**`CommissionRule`**: `tenant`, `name`, `insurer` (nullable), `line` (nullable), `agent` (nullable), `producer` (nullable), `agent_percentage`, `producer_percentage`, `priority`, `valid_from`, `valid_to`, `is_active`, auditoria.

A regra aplicável é resolvida da mais específica para a mais genérica, por `priority`.

**`CommissionEntry`**: `tenant`, `policy`, `installment` (nullable), `beneficiary_type` (`BROKERAGE`, `AGENT`, `PRODUCER`), `agent` (nullable), `producer` (nullable), `base_amount`, `percentage`, `amount`, `due_date`, `status` (`PENDING`, `PAID`, `CANCELLED`), `paid_at`, auditoria.

Fluxo do cálculo: a seguradora paga o valor bruto à corretora → o motor gera uma entrada `BROKERAGE` com o total → gera entradas `AGENT` e `PRODUCER` com os repasses conforme a regra → o líquido da corretora é o total menos os repasses.

### 7.9 `crm`

**`Pipeline`**: `tenant`, `name`, `is_default`, `is_active`, auditoria.

**`PipelineStage`**: `tenant`, `pipeline`, `name`, `color` (hex, restrito à paleta do design system), `order`, `is_won`, `is_lost`, auditoria. **Etapas, cores e nomes são personalizáveis pelo usuário.**

**`Deal`** (negociação/lead): `tenant`, `pipeline`, `stage`, `title`, `client` (nullable — lead ainda sem cadastro), `lead_name`, `lead_email`, `lead_phone`, `insurer`, `line`, `estimated_value`, `probability`, `expected_close_date`, `owner` (FK → `User`), `producer`, `agent`, `proposal` (nullable — conversão), `status` (`OPEN`, `WON`, `LOST`), `lost_reason`, `position` (ordenação dentro da etapa), `ai_summary`, `ai_summary_generated_at`, auditoria.

**`DealActivity`**: `tenant`, `deal`, `activity_type` (`NOTE`, `CALL`, `EMAIL`, `MEETING`, `STAGE_CHANGE`), `description`, `created_by`, auditoria.

### 7.10 `attachments`

**`Attachment`**: `tenant`, `content_type` + `object_id` (GenericForeignKey para `Client`, `Proposal`, `Policy`, `Claim`), `file` (FileField com `upload_to` particionado por tenant), `original_name`, `mime_type`, `size`, `description`, `uploaded_by`, auditoria.

Caminho de upload: `MEDIA_ROOT/tenant_<tenant_id>/<app_label>/<object_id>/<uuid>_<slug>.<ext>`. `MEDIA_ROOT` fica **fora** de qualquer diretório servido estaticamente.

### 7.11 `notifications`

**`Notification`**: `tenant`, `user`, `title`, `message`, `level` (`INFO`, `SUCCESS`, `WARNING`, `ERROR`), `url`, `is_read`, `read_at`, auditoria.

### 7.12 `ai_agents` e `ai_chat`

**`AISummaryRun`**: `tenant`, `content_type` + `object_id`, `status` (`QUEUED`, `RUNNING`, `SUCCESS`, `FAILED`), `celery_task_id`, `requested_by`, `prompt_version`, `input_tokens`, `output_tokens`, `duration_ms`, `error_message`, auditoria.

**`ChatSession`**: `tenant`, `user`, `title`, `is_archived`, `last_message_at`, auditoria.

**`ChatMessage`**: `tenant`, `session`, `role` (`USER`, `ASSISTANT`, `SYSTEM`, `TOOL`), `content` (Markdown), `tool_name`, `tool_payload` (JSONField), `input_tokens`, `output_tokens`, auditoria.

### 7.13 `reports`

**`ReportExecution`**: `tenant`, `report_key`, `filters` (JSONField), `output_format` (`PDF`, `CSV`), `status`, `file` (FileField em media protegida), `requested_by`, `celery_task_id`, auditoria.

---

## 8. Requisitos Funcionais

### RF01 — Gestão de usuários, autenticação e permissões

- Model `User` customizado com `USERNAME_FIELD = 'email'`; login exclusivamente por e-mail.
- Autenticação pelo sistema **nativo** do Django (`django.contrib.auth`), com `LoginView`, `LogoutView`, `PasswordResetView`, `PasswordResetConfirmView`.
- Papéis `OWNER`, `AGENT`, `PRODUCER` com escopo de visibilidade conforme a seção 3.1.
- CRUD de usuários do tenant (restrito a `OWNER`), com convite por e-mail.
- Ativação/desativação de usuário sem exclusão de histórico.

### RF02 — Cadastro de Clientes, Seguradoras e Ramos

- CRUD completo (listar, criar, detalhar, editar, desativar) para as três entidades, em CBVs.
- Busca por nome/documento, filtros por status e ordenação; paginação em todas as listagens.
- Validação de CPF/CNPJ e unicidade escopada ao tenant.

### RF03 — Gestão de Propostas e Apólices

- CRUD completo de propostas e apólices com formset de itens cobertos.
- Fluxo de status da proposta e da apólice conforme a seção 7.6.
- Filtros por cliente, seguradora, ramo, status, produtor, agente e intervalo de datas.
- Geração automática de parcelas da apólice a partir de `installments_count`.

### RF04 — Botão "Gerar Apólice"

- Botão exibido no detalhe da Proposta apenas quando `status == APPROVED` e ainda não existe apólice gerada.
- Ação transacional (`transaction.atomic`) que copia cliente, seguradora, ramo, produtor, agente, valores, vigência e **todos** os `ProposalItem` como `PolicyItem`.
- Gera as parcelas e dispara o cálculo de comissões.
- Marca a proposta como `CONVERTED` e cria o vínculo `proposal.generated_policy`.
- Redireciona para o detalhe da apólice criada com mensagem de sucesso em português.

### RF05 — Gestão de Sinistros

- Sinistro **sempre** vinculado a um `PolicyItem` — o formulário exige selecionar a apólice e, em seguida, o item coberto (carregado via HTMX).
- Timeline de eventos (`ClaimEvent`) no detalhe.
- Filtros por status, período de ocorrência, seguradora e ramo.

### RF06 — Anexos com controle de permissão

- Upload de múltiplos formatos (PDF, imagens, documentos de escritório, arquivos compactados) em Clientes, Propostas, Apólices e Sinistros.
- Validação de extensão, MIME type real e tamanho máximo.
- **Nenhum arquivo é servido por URL pública.** Todo download passa por view protegida (seção 12).
- Exclusão de anexo restrita a `OWNER` ou ao usuário que o enviou.

### RF07 — Tela de Relatórios com exportação PDF e CSV

- Tela dedicada com catálogo de relatórios: Produção por período, Comissões por agente, Comissões por produtor, Apólices a vencer, Renovações, Sinistralidade, Funil comercial.
- Filtros por período, seguradora, ramo, agente, produtor e status.
- Exportação em **PDF** gerada com **ReportLab** (layout, tabelas e cabeçalho com identidade do tenant) e pós-processada com **PyPDF** (mesclagem, numeração de páginas, metadados).
- Exportação em **CSV** com resposta em streaming.
- Geração executada em task Celery quando o volume exceder o limite configurado, com notificação in-app ao concluir.

### RF08 — Dashboard

- Cartões de métrica: apólices ativas, prêmio emitido no mês, comissão a receber, sinistros abertos, renovações do mês, propostas em aberto.
- Gráficos: produção mensal (linha), distribuição por ramo (rosca), ranking de seguradoras (barra), sinistralidade (barra empilhada).
- **Gráfico de funil** de negociações/leads, com um nível por etapa do pipeline, exibindo quantidade, valor total e taxa de conversão entre níveis.
- Filtro global de período; agregações em uma única query por gráfico, com cache em Redis.

### RF09 — Gestão de Itens Cobertos

- CRUD de itens cobertos com formulário dinâmico conforme o `item_type` (veículo, imóvel, frota, viagem, vida e outros), gravando os campos específicos em `attributes` (JSONField).
- Um item pertence a um cliente e pode ser vinculado a **várias** propostas e apólices.
- Cada proposta e cada apólice pode conter **mais de um** item coberto.

### RF10 — Gestão de Renovações

- Listagem de apólices com vencimento em janelas configuráveis (30/60/90 dias).
- Registro de renovação com status e responsável; ao concluir, gera nova apólice vinculada à original.
- Task periódica no Celery Beat que cria os registros de renovação pendentes e notifica os responsáveis.

### RF11 — Agentes, Produtores e Comissões

- CRUD de agentes e produtores respeitando a hierarquia da seção 3.2 (produtor com `agent` opcional).
- Cadastro de regras de comissão por seguradora, ramo, agente e produtor, com vigência e prioridade.
- Cálculo automático das entradas de comissão na emissão da apólice e na baixa de cada parcela.
- Controle de status de pagamento do repasse (pendente/pago) e relatórios dedicados por agente e por produtor.

### RF12 — CRM em grid e kanban

- Alternância entre visão **grid** (tabela com filtros, ordenação e paginação) e visão **kanban**.
- Pipeline **personalizável**: criar, renomear, reordenar e colorir etapas; marcar etapas de ganho e perda.
- Cards **arrastáveis** entre etapas (SortableJS), com persistência via requisição assíncrona e atualização otimista da UI.
- Registro automático de `DealActivity` do tipo `STAGE_CHANGE` a cada movimentação.
- Conversão de negociação em proposta a partir do card.

### RF13 — Gestão de Endossos

- CRUD de endossos vinculados a uma apólice, com tipo, descrição, data de efeito e diferença de prêmio.
- Endosso aprovado atualiza os valores da apólice e recalcula as comissões afetadas.
- Histórico de endossos exibido no detalhe da apólice.

### RF14 — Django Admin

- Todas as entidades registradas com `ModelAdmin` completo: `list_display`, `list_filter`, `search_fields`, `date_hierarchy`, `autocomplete_fields`, `readonly_fields` de auditoria e inlines nos relacionamentos naturais.
- Admin filtrado por tenant para usuários staff não-superusuários.
- `dj-celery-panel` registrado para visualização das tasks do Celery dentro do admin.

### RF15 — Landing page, cadastro e recuperação de senha

- Landing page institucional na **raiz** (`/`), pública, responsiva, com seções de proposta de valor, funcionalidades, planos e rodapé, além dos botões **"Criar Conta"** e **"Login"**.
- Cadastro em etapa única criando `Tenant` + `User` `OWNER`, com **CNPJ e Razão Social obrigatórios** e validados.
- Seleção de plano: **somente o plano Free é selecionável**; os demais aparecem com selo **"Em breve"**, desabilitados. **Nenhum cartão de crédito é solicitado.**
- Recuperação de senha via fluxo nativo do Django, enviando e-mail por `django.core.mail` com credenciais lidas do `.env`.

### RF16 — Agente de IA de resumo ("Resumir com IA")

- Botão **"Resumir com IA"** disponível no detalhe de **Cliente, Apólice, Sinistro, Proposta e Negociação**.
- Ao clicar: o botão entra em estado de carregamento, exibe-se o aviso "Você será notificado quando o resumo estiver pronto" e uma task Celery é enfileirada. **O request retorna imediatamente.**
- O agente é um grafo LangGraph com tools de leitura ao banco, **sempre escopadas ao tenant** do registro.
- O resultado é gravado no campo de texto `ai_summary` da entidade, com `ai_summary_generated_at`, e a execução registrada em `AISummaryRun`.
- Ao concluir, cria-se uma `Notification` in-app apontando para o registro; a UI atualiza o resumo sem recarregar a página.

### RF17 — Chat com o Agente de IA

- Item **"Chat IA"** no menu lateral, com tela dedicada.
- **Sessões salvas por usuário**, listadas em barra lateral, com renomear, arquivar e excluir; título gerado a partir da primeira mensagem.
- Tools de consulta à base da corretora (clientes, apólices, propostas, sinistros, comissões, funil), sempre filtradas pelo tenant e pelo escopo do papel do usuário.
- Resposta em **efeito stream** via SSE, token a token.
- **Renderização de Markdown → HTML** com sanitização, incluindo tabelas, listas e blocos de código.

---

## 9. Requisitos Não Funcionais

### RNF01 — Responsividade

Interface totalmente responsiva em mobile, tablet e desktop, com abordagem mobile-first e os breakpoints do design system. Menu lateral colapsável, tabelas com scroll horizontal controlado e kanban com scroll horizontal por coluna no mobile.

### RNF02 — Segurança

- Nenhuma rota sensível acessível sem autenticação e sem checagem de permissão.
- Isolamento rígido entre tenants em todas as camadas (seção 5.2).
- Arquivos de media servidos exclusivamente por view protegida (seção 12).
- CSRF ativo em todos os formulários; `SECURE_*`, `SESSION_COOKIE_HTTPONLY` e `X_FRAME_OPTIONS` configurados.

### RNF03 — UI/UX e acessibilidade

Aderência rigorosa ao design system, contraste mínimo WCAG AA (4.5:1 em texto), foco visível em todos os elementos interativos, estados de carregamento, vazio e erro definidos para toda listagem, e mensagens sempre em português brasileiro.

### RNF04 — Nada bloqueante na interface

Toda tarefa pesada — em especial as de IA, geração de PDF volumoso e recálculo de comissões em lote — roda em Celery. O padrão obrigatório de interação é: **estado de carregamento no botão → aviso de notificação futura → notificação in-app ao concluir**. Nenhuma chamada a LLM ocorre dentro do ciclo request/response síncrono.

### RNF05 — Desempenho

- `select_related` e `prefetch_related` em todas as listagens; zero N+1.
- Índices compostos `(tenant_id, campo)` nos campos filtráveis e ordenáveis.
- Paginação obrigatória (padrão 25 itens).
- Agregações do dashboard em cache Redis com TTL curto e invalidação por evento.
- Exportações grandes em streaming ou via task assíncrona.

### RNF06 — Inicialização ordenada do ambiente

Management command `wait_for_db` que aguarda o PostgreSQL responder antes de subir a aplicação, com tentativas e timeout configuráveis, evitando falhas silenciosas por dependência indisponível. Um comando análogo (`check_services`) reporta o estado do PostgreSQL, do Redis de cache e do broker do Celery.

### RNF07 — Gestão de segredos

Senha do banco, credenciais do broker, chave da OpenAI e credenciais de e-mail vivem **apenas** no `.env` local, que está no `.gitignore`. O repositório versiona somente `.env.example` com chaves vazias e comentadas. Nenhum segredo em texto puro em qualquer arquivo versionado.

---

## 10. Camada de IA (LangChain + LangGraph)

### 10.1 Princípios

| Princípio | Implementação |
| --- | --- |
| Modelo único | `gpt-5.5-mini` via API da OpenAI, id lido de `OPENAI_MODEL` no `.env` |
| Isolamento de tenant nas tools | Toda tool recebe `tenant_id` e `user_id` no contexto do grafo e filtra obrigatoriamente por eles |
| Nada síncrono | Resumos sempre em Celery; chat em streaming fora do ciclo de escrita |
| Somente leitura | As tools do agente executam apenas consultas; nenhuma escrita no banco |
| Rastreabilidade | Toda execução registra tokens, duração e status |

### 10.2 Agente de resumo (`ai_agents`)

```mermaid
graph LR
    S[Start] --> L[load_context]
    L --> P[plan_tools]
    P --> T[run_tools]
    T --> D{contexto suficiente?}
    D -- nao --> P
    D -- sim --> G[generate_summary]
    G --> V[validate_output]
    V --> E[persist_and_notify]
```

Estado do grafo: `tenant_id`, `user_id`, `entity_type`, `entity_id`, `collected_context`, `tool_calls`, `summary`, `errors`.

Tools por entidade: `get_client_overview`, `get_client_policies`, `get_proposal_detail`, `get_policy_detail`, `get_policy_claims`, `get_claim_timeline`, `get_deal_activities`. Todas assinam `(tenant_id, object_id)` e usam o manager irrestrito com filtro explícito de tenant.

Execução: `ai_agents.tasks.generate_summary_task(entity_type, entity_id, tenant_id, user_id)`, com `max_retries=2`, backoff exponencial e registro em `AISummaryRun`.

### 10.3 Agente de chat (`ai_chat`)

- Grafo LangGraph do tipo ReAct com memória da sessão (`ChatMessage` como histórico).
- Tools de consulta agregada: `search_clients`, `list_policies`, `list_expiring_policies`, `list_open_claims`, `commission_summary`, `sales_funnel_summary`.
- Escopo duplo: filtro por tenant **e** filtro pelo papel do usuário (um `PRODUCER` só consulta a própria carteira).
- Streaming: view CBV que retorna `StreamingHttpResponse` com `text/event-stream`, consumindo os eventos do grafo; a mensagem completa é persistida ao final.
- Renderização: acumulação do Markdown no cliente com highlight incremental e sanitização; ao recarregar a sessão, o Markdown persistido é convertido no servidor com `markdown` + `bleach`.

### 10.4 Guardrails

- Limite de tokens de entrada por execução e truncamento do histórico por janela.
- Limite de chamadas de tool por execução do grafo.
- Timeout por execução; falha registra erro e notifica o usuário sem quebrar a interface.
- Prompt de sistema versionado (`prompt_version`) e armazenado em arquivos Python do app.

---

## 11. Design System

### 11.1 Fonte da verdade

O arquivo **`design_system/design-system.html`** e seu bundle CSS são a **única** fonte de verdade visual do produto. Nenhuma cor, fonte, raio, sombra ou componente fora desse arquivo pode ser introduzido no sistema.

### 11.2 Tokens de cor

O design system adota paleta neutra monocromática em HSL, com suporte a tema claro e escuro. Os tokens são replicados no CSS do projeto como variáveis e mapeados na configuração do Tailwind.

| Token | Claro | Escuro |
| --- | --- | --- |
| `--background` | `0 0% 100%` | `0 0% 9%` |
| `--foreground` | `0 0% 9%` | `0 0% 98%` |
| `--card` | `0 0% 98%` | `0 0% 11%` |
| `--card-foreground` | `0 0% 9%` | `0 0% 98%` |
| `--popover` | `0 0% 98%` | `0 0% 11%` |
| `--popover-foreground` | `0 0% 9%` | `0 0% 98%` |
| `--primary` | `0 0% 9%` | `0 0% 98%` |
| `--primary-foreground` | `0 0% 98%` | `0 0% 9%` |
| `--secondary` | `0 0% 96%` | `0 0% 13%` |
| `--secondary-foreground` | `0 0% 9%` | `0 0% 98%` |
| `--muted` | `0 0% 96%` | `0 0% 13%` |
| `--muted-foreground` | `0 0% 45%` | `0 0% 65%` |
| `--accent` | `0 0% 96%` | `0 0% 13%` |
| `--accent-foreground` | `0 0% 9%` | `0 0% 98%` |
| `--destructive` | `0 84% 60%` | `0 63% 31%` |
| `--destructive-foreground` | `0 0% 98%` | `0 0% 98%` |
| `--border` | `0 0% 90%` | `0 0% 20%` |
| `--ring` | `0 0% 80%` | `0 0% 20%` |
| `--sidebar-background` | `0 0% 98%` | `0 0% 9%` |
| `--sidebar-foreground` | `0 0% 9%` | `0 0% 98%` |
| `--sidebar-accent` | `0 0% 96%` | `0 0% 15%` |
| `--sidebar-border` | `0 0% 90%` | `0 0% 20%` |
| `--sidebar-ring` | `0 0% 80%` | `0 0% 20%` |

Cores de status funcionais (badges de apólice, sinistro, comissão) e as cores selecionáveis das etapas do CRM são derivadas exclusivamente desses tokens e de `--destructive`, mantendo contraste mínimo AA.

### 11.3 Tipografia

| Uso | Fonte | Origem |
| --- | --- | --- |
| Toda a interface | **Inter** (300, 400, 500, 600, 700) | Declarada no `<head>` do design system, carregada via Google Fonts |

Escala tipográfica, pesos e alturas de linha seguem o bundle do design system. Nenhuma família adicional é permitida.

### 11.4 Outros tokens

| Token | Valor |
| --- | --- |
| `--radius` | `0.5rem` (com as variações `sm`, `md`, `lg` derivadas) |
| Ícones | Web component `iconify-icon` (`design_system/js/iconify-icon.min.js`) |
| Espaçamento, sombras e breakpoints | Escala padrão do bundle Tailwind do design system |

### 11.5 Componentes canônicos

Botão (primário, secundário, destrutivo, ghost, com estado de carregamento), input, select, textarea, checkbox, radio, switch, card, badge, tabela, paginação, modal/dialog, dropdown, tooltip, tabs, breadcrumb, alerta, toast, sidebar, skeleton, avatar, progress, empty state.

Todos são implementados uma única vez como `{% include %}` reutilizáveis em `base/templates/base/components/` e consumidos por todos os apps. Nenhum app cria variante própria de componente.

### 11.6 Regras de aplicação

- Textos da interface **sempre em português brasileiro**; código-fonte sempre em inglês.
- Contraste mínimo 4.5:1 entre texto e fundo, verificado em ambos os temas.
- Nenhuma cor literal (`#hex`, `rgb()`) em template ou CSS de app: apenas classes utilitárias mapeadas nos tokens.
- Todo novo componente exige registro na documentação em `docs/`.

---

## 12. Segurança e Arquivos de Media Protegidos

### 12.1 Entrega protegida de media

**Nenhum arquivo de media é servido por URL pública direta.** `MEDIA_URL` não é exposta por `static()` nem por qualquer servidor de arquivos.

Fluxo obrigatório:

```mermaid
graph TD
    U[Usuario] --> R["GET /media/attachment/uuid/"]
    R --> LR{Autenticado?}
    LR -- nao --> D1[302 para login]
    LR -- sim --> TC{Anexo pertence ao tenant do usuario?}
    TC -- nao --> D2[404]
    TC -- sim --> PC{Papel do usuario permite ver o objeto pai?}
    PC -- nao --> D3[403]
    PC -- sim --> F[FileResponse com Content-Disposition]
```

Implementação: `base.views.ProtectedMediaView`, uma CBV baseada em `View` com `LoginRequiredMixin`, que resolve o `Attachment` por UUID, compara `attachment.tenant_id` com `request.tenant.id`, verifica a permissão do usuário sobre o objeto pai e só então devolve `FileResponse`. Tenant divergente retorna **404** (nunca 403, para não revelar existência). Todo acesso é registrado em log.

O mesmo mecanismo cobre logos de tenant, avatares de usuário e arquivos gerados de relatório.

### 12.2 Validação de upload

- Whitelist de extensões e verificação do MIME type real do conteúdo (`python-magic`), não apenas do header enviado.
- Tamanho máximo por arquivo configurável no `.env`.
- Nome de arquivo sempre reescrito com UUID; o nome original é guardado em coluna separada.
- Arquivos gravados sob `MEDIA_ROOT/tenant_<id>/…`, fora de qualquer diretório estático.

### 12.3 Demais controles

| Controle | Implementação |
| --- | --- |
| Autenticação | Sistema nativo do Django, login por e-mail |
| Autorização | `TenantRequiredMixin` + `RolePermissionMixin` em todas as CBVs |
| CSRF | Ativo em todos os formulários e requisições HTMX |
| Enumeração de objetos | UUID público nas rotas de anexo; 404 para objeto de outro tenant |
| Senhas | Validadores nativos do Django + hasher padrão |
| Sessão | `HTTPONLY`, `SAMESITE=Lax`, expiração configurável |
| Logs | Toda ação de acesso a media e toda execução de IA registradas |

---

## 13. Infraestrutura de Desenvolvimento Local (Nativa)

### 13.1 Princípio

Todo o ambiente roda **nativamente no sistema operacional**, sem containers. PostgreSQL e Redis são instalados diretamente na máquina; a aplicação Django roda dentro do `.venv` via `runserver`. Caso a instalação nativa de algum serviço não seja viável na máquina do desenvolvedor, a **única** alternativa aceitável é um serviço gerenciado em nuvem no free tier, configurado por `.env`.

### 13.2 Serviços locais

| Serviço | Papel | Porta padrão | Instalação (macOS / Homebrew) | Alternativa gerenciada (free tier) |
| --- | --- | --- | --- | --- |
| PostgreSQL 16 | Banco de dados | 5432 | `brew install postgresql@16` + `brew services start postgresql@16` | Neon / Supabase |
| Redis 7 | Cache, broker e result backend do Celery | 6379 | `brew install redis` + `brew services start redis` | Upstash |
| Django | Aplicação web | 8000 | `python manage.py runserver` no `.venv` | — |
| Celery worker | Processamento assíncrono | — | `celery -A core worker -l info` | — |
| Celery beat | Agendamento | — | `celery -A core beat -l info` | — |
| MkDocs | Documentação | 8001 | `mkdocs serve -a 127.0.0.1:8001` | — |

Em Linux, os mesmos serviços são instalados pelo gerenciador de pacotes da distribuição e gerenciados por `systemctl`. O `README.md` documenta ambos os caminhos.

### 13.3 Ordem de inicialização

```mermaid
graph LR
    A[Iniciar PostgreSQL e Redis] --> B[Ativar .venv]
    B --> C[python manage.py wait_for_db]
    C --> D[python manage.py migrate]
    D --> E[python manage.py runserver]
    D --> F[celery -A core worker -l info]
    D --> G[celery -A core beat -l info]
```

Cada processo Django/Celery roda em um terminal separado, sempre com o `.venv` ativado.

### 13.4 Comandos principais

| Objetivo | Comando |
| --- | --- |
| Criar ambiente virtual | `python3.13 -m venv .venv` |
| Ativar ambiente | `source .venv/bin/activate` |
| Instalar dependências | `pip install -r requirements.txt` |
| Congelar dependências | `pip freeze > requirements.txt` |
| Aguardar o banco | `python manage.py wait_for_db` |
| Verificar serviços | `python manage.py check_services` |
| Aplicar migrações | `python manage.py migrate` |
| Criar superusuário | `python manage.py createsuperuser` |
| Subir a aplicação | `python manage.py runserver` |
| Worker Celery | `celery -A core worker -l info` |
| Beat Celery | `celery -A core beat -l info` |
| Carregar dados fake | `python manage.py seed_demo_data` |
| Compilar CSS | `./tailwindcss -i static/src/input.css -o static/css/app.css --watch` |
| Servir a documentação | `mkdocs serve -a 127.0.0.1:8001` |

### 13.5 Carga de dados fake

Management command `seed_demo_data` (app `base`), com argumentos `--tenants`, `--months` e `--reset`, gerando com `Faker` (locale `pt_BR`) e **datas variadas ao longo do tempo**:

- Múltiplos tenants, cada um com dono, agentes e produtores (incluindo produtores diretos da corretora).
- Clientes PF e PJ, seguradoras, ramos e itens cobertos de todos os tipos.
- Propostas em todos os status; apólices ativas, vencidas, canceladas e renovadas.
- Apólices com múltiplos itens cobertos e parcelas em diferentes estados de pagamento.
- Sinistros em todos os status, vinculados a itens cobertos.
- Endossos de todos os tipos e renovações em todas as etapas.
- Regras e lançamentos de comissão com repasses pendentes e pagos.
- Pipelines com etapas coloridas e negociações distribuídas por todas as fases do funil.
- Anexos de exemplo e notificações in-app.

---

## 14. Variáveis de Ambiente

O `settings.py` é **único** e lê todas as configurações do `.env` via `django-environ`. O `.env` está no `.gitignore`; o repositório versiona apenas `.env.example`.

| Variável | Descrição | Exemplo |
| --- | --- | --- |
| `SECRET_KEY` | Chave secreta do Django | `django-insecure-…` |
| `DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `DATABASE_URL` | Conexão PostgreSQL | `postgres://scsi:senha@localhost:5432/scsi` |
| `CELERY_BROKER_URL` | Broker Redis (database dedicado) | `redis://127.0.0.1:6379/0` |
| `CELERY_RESULT_BACKEND` | Result backend Redis | `redis://127.0.0.1:6379/1` |
| `REDIS_CACHE_URL` | Cache da aplicação | `redis://127.0.0.1:6379/2` |
| `TIME_ZONE` | Fuso horário | `America/Sao_Paulo` |
| `LANGUAGE_CODE` | Idioma da interface | `pt-br` |
| `EMAIL_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `EMAIL_PORT` | Porta SMTP | `587` |
| `EMAIL_HOST_USER` | Usuário SMTP | — |
| `EMAIL_HOST_PASSWORD` | Senha SMTP | — |
| `EMAIL_USE_TLS` | TLS no SMTP | `True` |
| `DEFAULT_FROM_EMAIL` | Remetente padrão | `nao-responda@scsi.local` |
| `OPENAI_API_KEY` | Chave da API OpenAI | — |
| `OPENAI_MODEL` | Modelo dos agentes | `gpt-5.5-mini` |
| `AI_MAX_TOOL_CALLS` | Limite de tools por execução | `8` |
| `AI_TIMEOUT_SECONDS` | Timeout do agente | `120` |
| `MEDIA_ROOT` | Raiz dos arquivos protegidos | `./media` |
| `MAX_UPLOAD_SIZE_MB` | Tamanho máximo de anexo | `20` |
| `WAIT_FOR_DB_TIMEOUT` | Timeout do `wait_for_db` | `60` |

---

## 15. Estrutura de Pastas

```
SCSI/
├── .venv/                          # ambiente virtual (gitignored)
├── .env                            # segredos locais (gitignored)
├── .env.example                    # modelo versionado, sem valores
├── .gitignore
├── README.md                       # setup local nativo completo
├── PRD.md                          # este documento
├── requirements.txt                # dependências, sempre atualizado
├── manage.py
├── mkdocs.yml
├── tailwind.config.js
│
├── core/                           # app principal + pacote do projeto
│   ├── __init__.py
│   ├── settings.py                 # ÚNICO arquivo de settings
│   ├── urls.py
│   ├── celery.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── models.py                   # Tenant, Plan
│   ├── admin.py
│   ├── views.py                    # landing page, health check
│   ├── forms.py
│   ├── signals.py
│   └── templates/core/
│
├── base/                           # recursos compartilhados
│   ├── models.py                   # TimeStampedModel, TenantAwareModel
│   ├── managers.py                 # TenantQuerySet, TenantManager
│   ├── middleware.py               # TenantMiddleware
│   ├── mixins.py                   # TenantRequiredMixin, RolePermissionMixin
│   ├── permissions.py
│   ├── context.py                  # ContextVar do tenant corrente
│   ├── views.py                    # ProtectedMediaView
│   ├── validators.py
│   ├── templatetags/
│   ├── management/commands/
│   │   ├── wait_for_db.py
│   │   ├── check_services.py
│   │   └── seed_demo_data.py
│   └── templates/base/
│       ├── layouts/
│       ├── components/
│       └── partials/
│
├── accounts/
├── clients/
├── insurers/
├── lines/
├── covered_items/
├── proposals/
├── policies/
├── endorsements/
├── renewals/
├── claims/
├── attachments/
├── agents/
├── producers/
├── commissions/
├── crm/
├── dashboard/
├── reports/
├── notifications/
├── ai_agents/
│   ├── graphs/
│   ├── tools/
│   ├── prompts/
│   └── tasks.py
├── ai_chat/
│   ├── graphs/
│   ├── tools/
│   ├── prompts/
│   └── views.py
│
├── design_system/                  # fonte da verdade visual (referência)
│   ├── design-system.html
│   ├── css/
│   ├── js/
│   └── images/
│
├── static/
│   ├── src/input.css
│   ├── css/app.css
│   ├── js/
│   └── img/
│
├── media/                          # gitignored, servido só por view protegida
│
└── docs/
    ├── index.md
    ├── arquitetura/
    ├── modelagem/
    ├── apps/
    ├── ia/
    ├── design-system/
    └── setup/
```

Cada app segue o layout padrão: `models.py`, `managers.py` (quando necessário), `forms.py`, `views.py`, `urls.py`, `admin.py`, `signals.py`, `services.py`, `tasks.py`, `migrations/` e `templates/<app>/`.

---

## 16. Convenções de Código

| Regra | Detalhe |
| --- | --- |
| Estilo | PEP 8 rigoroso; linhas de até 100 caracteres |
| Strings | **Sempre aspas simples** em Python |
| Idioma do código | Inglês em variáveis, classes, funções, docstrings e comentários |
| Idioma da interface | Português brasileiro em labels, mensagens, e-mails e erros |
| Views | **Class Based Views sempre**; function based views apenas quando a CBV for comprovadamente inviável |
| Recursos nativos | Preferir sempre `ModelForm`, `formset`, `messages`, `paginator`, `auth`, `django.core.mail` a soluções customizadas equivalentes |
| Signals | Exclusivamente em `signals.py` do app, conectados via `ready()` do `AppConfig` — **nunca** em `models.py` ou `apps.py` |
| Regras de negócio | Em `services.py` do app, não na view nem no model |
| Tasks Celery | Em `tasks.py` do app, idempotentes, recebendo IDs (nunca instâncias) |
| Simplicidade | Preferir código legível a abstração excessiva |
| Migrações | Uma migração por mudança lógica, com nome descritivo |
| Testes | **Não implementar testes automatizados nesta fase** |
| Commits | Conventional Commits, em inglês |

---

## 17. Documentação (MkDocs)

A pasta `docs/` é obrigatória e deve estar **sempre atualizada**, servida por MkDocs com tema Material e **renderização de diagramas Mermaid** habilitada.

Configuração mínima (`mkdocs.yml`):

```yaml
site_name: SCSI — Documentação
theme:
  name: material
markdown_extensions:
  - admonition
  - tables
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

Conteúdo mínimo:

| Seção | Conteúdo |
| --- | --- |
| `index.md` | Visão geral do produto |
| `setup/` | Instalação nativa dos serviços, `.venv`, variáveis de ambiente, comandos |
| `arquitetura/` | Multi-tenant shared schema, camadas de isolamento, diagramas Mermaid |
| `modelagem/` | Diagrama ER e dicionário de dados por app |
| `apps/` | Uma página por app: responsabilidade, models, rotas, permissões |
| `ia/` | Grafos LangGraph, tools, prompts, guardrails |
| `design-system/` | Tokens, componentes e regras de uso |

Toda entrega de sprint só é considerada concluída com a documentação correspondente atualizada.

---

## 18. Sprints de Desenvolvimento

As sprints estão em ordem lógica de dependência: fundação → autenticação → cadastros base → features → IA → refinamento.

### Sprint 0 — Fundação do projeto e ambiente local

- [x] Instalar Python 3.13 e confirmar a versão com `python3.13 --version`
- [x] Criar o repositório no GitHub e inicializar o Git local
- [x] Criar o ambiente virtual `.venv` na raiz do projeto
- [x] Criar o `.gitignore` incluindo `.venv/`, `.env`, `media/`, `__pycache__/`, `*.sqlite3` e `staticfiles/`
- [x] Instalar Django > 6.0 e criar o projeto com o pacote `core`
- [x] Criar o `requirements.txt` na raiz e registrar as dependências iniciais
- [x] Instalar PostgreSQL nativamente e iniciar o serviço
- [x] Criar o banco `scsi` e o usuário de aplicação no PostgreSQL
- [x] Instalar Redis nativamente e iniciar o serviço
- [x] Configurar o Redis como broker do Celery em database dedicado
- [x] Instalar `django-environ` e criar o `.env` e o `.env.example` na raiz
- [x] Configurar o `settings.py` único lendo todas as variáveis do `.env`
- [x] Configurar o PostgreSQL como banco padrão via `DATABASE_URL`
- [x] Configurar `TIME_ZONE = 'America/Sao_Paulo'`, `LANGUAGE_CODE = 'pt-br'` e `USE_TZ = True`
- [x] Configurar o Redis como backend de cache da aplicação
- [x] Criar o app `base` na raiz e registrá-lo em `INSTALLED_APPS`
- [x] Implementar `TimeStampedModel` com `created_at` e `updated_at` em `base/models.py`
- [x] Implementar o management command `wait_for_db` com tentativas e timeout configuráveis
- [x] Implementar o management command `check_services` verificando PostgreSQL, Redis e o broker do Celery
- [x] Implementar o endpoint `GET /health/` retornando 200, sem acessar o banco e sem autenticação
- [x] Configurar `core/celery.py` com Redis como broker e result backend, em databases distintos
- [x] Validar `celery -A core worker` e `celery -A core beat` com uma task de teste
- [x] Instalar e registrar o `dj-celery-panel` no admin do Django
- [x] Criar a pasta `docs/`, o `mkdocs.yml` com tema Material e o suporte a Mermaid
- [x] Criar o `README.md` inicial com o passo a passo do setup local nativo
- [x] Fazer o primeiro commit e o push para o GitHub

> **Nota de ambiente (2026-08-13).** Este ambiente roda macOS 12.7.6, que o Homebrew não
> suporta mais (sem bottles; toda fórmula compila do source). Conforme §13.1, PostgreSQL 16
> e Redis 7.4 foram instalados nativamente — Postgres.app e build do source,
> respectivamente.

> **Nota de decisão (2026-08-16).** O RabbitMQ foi **removido do escopo do projeto**. O
> Redis passa a ser o broker único do Celery, acumulando os papéis de broker, result
> backend e cache da aplicação, em databases distintos para evitar colisão de dados:
> `0` broker, `1` result backend, `2` cache. As duas tarefas antes bloqueadas pelo
> RabbitMQ foram concluídas com essa configuração.

### Sprint 1 — Núcleo multi-tenant

- [ ] Criar o app `core` como app principal registrado em `INSTALLED_APPS`
- [ ] Modelar `Plan` com `is_enabled` (habilitado apenas no Free)
- [ ] Modelar `Tenant` com Razão Social e CNPJ obrigatórios e validados
- [ ] Criar a migração inicial e o data migration que popula os planos Free, Pro e Business
- [ ] Implementar o `ContextVar` de tenant corrente em `base/context.py`
- [ ] Implementar `TenantQuerySet` e `TenantManager` com filtro automático por tenant
- [ ] Implementar o model abstrato `TenantAwareModel` com FK `tenant` e auditoria
- [ ] Implementar `TenantMiddleware` resolvendo o tenant a partir do usuário autenticado
- [ ] Registrar o `TenantMiddleware` após o `AuthenticationMiddleware` no `settings.py`
- [ ] Implementar `TenantRequiredMixin` compondo `LoginRequiredMixin`
- [ ] Implementar `RolePermissionMixin` com o escopo de visibilidade por papel
- [ ] Implementar a validação de integridade cross-tenant no `clean()` dos models de domínio
- [ ] Registrar `Tenant` e `Plan` no admin com filtros e busca
- [ ] Documentar a arquitetura multi-tenant em `docs/arquitetura/` com diagrama Mermaid

### Sprint 2 — Autenticação e usuários

- [ ] Criar o app `accounts` na raiz
- [ ] Implementar o model `User` com `USERNAME_FIELD = 'email'` e sem campo `username`
- [ ] Implementar o `UserManager` com `create_user` e `create_superuser` por e-mail
- [ ] Adicionar os papéis `OWNER`, `AGENT` e `PRODUCER` como choices em `role`
- [ ] Configurar `AUTH_USER_MODEL` no `settings.py` e gerar a migração
- [ ] Configurar o backend de e-mail nativo com as credenciais lidas do `.env`
- [ ] Implementar a tela de login por e-mail com `LoginView` e template do design system
- [ ] Implementar o logout com `LogoutView`
- [ ] Implementar a recuperação de senha com as views nativas e templates de e-mail em português
- [ ] Implementar o model `Invitation` com token e expiração
- [ ] Implementar o CRUD de usuários do tenant restrito ao papel `OWNER`
- [ ] Implementar o envio de convite por e-mail e a tela de aceite com definição de senha
- [ ] Registrar `User` e `Invitation` no admin com filtros por papel e status
- [ ] Documentar o fluxo de autenticação em `docs/apps/accounts.md`

### Sprint 3 — Layout base e design system

- [ ] Extrair os tokens de cor, tipografia e raio do `design_system/design-system.html`
- [ ] Configurar o `tailwind.config.js` mapeando todos os tokens extraídos
- [ ] Configurar o Tailwind CLI standalone e o script de build do CSS
- [ ] Criar o `static/src/input.css` com as variáveis de tema claro e escuro
- [ ] Carregar a fonte Inter conforme declarado no design system
- [ ] Integrar o web component `iconify-icon` para os ícones
- [ ] Criar o layout autenticado com sidebar, topbar e área de conteúdo
- [ ] Criar o layout público para a landing page e as telas de autenticação
- [ ] Implementar os componentes de botão em todas as variantes, incluindo estado de carregamento
- [ ] Implementar os componentes de formulário: input, select, textarea, checkbox, radio e switch
- [ ] Implementar os componentes de card, badge, tabela e paginação
- [ ] Implementar os componentes de modal, dropdown, tooltip, tabs e breadcrumb
- [ ] Implementar os componentes de alerta, toast, skeleton, avatar e empty state
- [ ] Integrar HTMX e Alpine.js no layout base
- [ ] Validar a responsividade dos layouts em mobile, tablet e desktop
- [ ] Validar o contraste mínimo AA em todos os componentes nos dois temas
- [ ] Documentar os componentes em `docs/design-system/`

### Sprint 4 — Landing page e cadastro de corretora

- [ ] Implementar a landing page institucional pública na raiz `/`
- [ ] Implementar as seções de proposta de valor, funcionalidades, planos e rodapé
- [ ] Adicionar os botões "Criar Conta" e "Login" no cabeçalho e nas chamadas de ação
- [ ] Implementar a seção de planos exibindo somente o Free habilitado
- [ ] Exibir os demais planos com o selo "Em breve" e o botão desabilitado
- [ ] Implementar o formulário de cadastro com Razão Social e CNPJ obrigatórios
- [ ] Implementar o validador de CNPJ e a checagem de unicidade
- [ ] Criar o `Tenant` e o `User` `OWNER` em uma única transação atômica
- [ ] Garantir que nenhum dado de cartão de crédito seja solicitado no cadastro
- [ ] Enviar e-mail de boas-vindas em português usando `django.core.mail`
- [ ] Redirecionar para o dashboard após o cadastro concluído
- [ ] Validar a responsividade completa da landing page

### Sprint 5 — Cadastros base

- [ ] Criar o app `clients` e modelar `Client` e `ClientContact`
- [ ] Implementar o CRUD de clientes em CBVs com busca, filtros e paginação
- [ ] Implementar os validadores de CPF e CNPJ com unicidade por tenant
- [ ] Criar o app `insurers` e modelar `Insurer`
- [ ] Implementar o CRUD de seguradoras em CBVs
- [ ] Criar o app `lines` e modelar `InsuranceLine`
- [ ] Implementar o CRUD de ramos em CBVs
- [ ] Criar o app `covered_items` e modelar `CoveredItem` com `attributes` em JSONField
- [ ] Implementar o formulário dinâmico por tipo de item coberto via HTMX
- [ ] Implementar o CRUD de itens cobertos vinculados ao cliente
- [ ] Registrar todas as entidades no admin com filtros, busca e autocomplete
- [ ] Criar os índices compostos `(tenant, campo)` nos campos filtráveis
- [ ] Documentar os cadastros base em `docs/apps/`

### Sprint 6 — Hierarquia comercial e comissões

- [ ] Criar o app `agents` e modelar `Agent` com tipo pessoa ou empresa
- [ ] Implementar o CRUD de agentes em CBVs
- [ ] Criar o app `producers` e modelar `Producer` com `agent` opcional
- [ ] Implementar o CRUD de produtores, permitindo vínculo direto à corretora
- [ ] Implementar a visualização em árvore da hierarquia corretora → agente → produtor
- [ ] Criar o app `commissions` e modelar `CommissionRule` com vigência e prioridade
- [ ] Modelar `CommissionEntry` com tipo de beneficiário e status de pagamento
- [ ] Implementar o CRUD de regras de comissão
- [ ] Implementar o serviço de resolução da regra aplicável, do mais específico ao mais genérico
- [ ] Implementar o serviço de cálculo das entradas de comissão da corretora, agente e produtor
- [ ] Implementar a baixa de pagamento de repasse com registro de data
- [ ] Aplicar o filtro por papel para que agentes e produtores vejam apenas suas comissões
- [ ] Registrar as entidades no admin com filtros por beneficiário e status
- [ ] Documentar o motor de comissões em `docs/apps/commissions.md`

### Sprint 7 — Propostas, apólices, endossos e renovações

- [ ] Criar o app `proposals` e modelar `Proposal` e `ProposalItem`
- [ ] Implementar o CRUD de propostas com formset de múltiplos itens cobertos
- [ ] Implementar as transições de status da proposta com validação
- [ ] Criar o app `policies` e modelar `Policy`, `PolicyItem` e `PolicyInstallment`
- [ ] Implementar o CRUD de apólices com formset de múltiplos itens cobertos
- [ ] Implementar a geração automática de parcelas a partir da quantidade informada
- [ ] Implementar o botão "Gerar Apólice" no detalhe da proposta aprovada
- [ ] Implementar o serviço transacional de conversão de proposta em apólice com todos os itens
- [ ] Disparar o cálculo de comissões na geração da apólice
- [ ] Marcar a proposta como convertida e vincular a apólice gerada
- [ ] Bloquear a geração duplicada de apólice para a mesma proposta
- [ ] Criar o app `endorsements` e modelar `Endorsement`
- [ ] Implementar o CRUD de endossos vinculados à apólice
- [ ] Implementar a aplicação do endosso aprovado sobre os valores da apólice
- [ ] Recalcular as comissões afetadas pelo endosso
- [ ] Criar o app `renewals` e modelar `Renewal`
- [ ] Implementar a listagem de apólices a vencer em janelas de 30, 60 e 90 dias
- [ ] Implementar o registro de renovação com status e responsável
- [ ] Implementar a geração da nova apólice a partir da renovação concluída
- [ ] Implementar a task periódica do Celery Beat que cria as renovações pendentes
- [ ] Registrar todas as entidades no admin com filtros e inlines
- [ ] Documentar o ciclo de vida da apólice em `docs/apps/policies.md`

### Sprint 8 — Sinistros e anexos protegidos

- [ ] Criar o app `claims` e modelar `Claim` com FK obrigatória para `PolicyItem`
- [ ] Modelar `ClaimEvent` para a timeline do sinistro
- [ ] Implementar o CRUD de sinistros em CBVs
- [ ] Implementar a seleção encadeada de apólice e item coberto via HTMX
- [ ] Implementar a timeline de eventos no detalhe do sinistro
- [ ] Implementar os filtros por status, período, seguradora e ramo
- [ ] Criar o app `attachments` e modelar `Attachment` com GenericForeignKey
- [ ] Implementar o `upload_to` particionado por tenant fora de diretórios estáticos
- [ ] Implementar a validação de extensão, MIME type real e tamanho máximo
- [ ] Implementar `ProtectedMediaView` com checagem de autenticação, tenant e permissão
- [ ] Retornar 404 para anexo de outro tenant, sem revelar existência
- [ ] Garantir que `MEDIA_URL` não seja servida publicamente em nenhuma configuração
- [ ] Implementar o componente de upload múltiplo reutilizável
- [ ] Integrar os anexos em Clientes, Propostas, Apólices e Sinistros
- [ ] Implementar o log de acesso a arquivos protegidos
- [ ] Registrar as entidades no admin
- [ ] Documentar a política de media protegida em `docs/arquitetura/media.md`

### Sprint 9 — CRM em grid e kanban

- [ ] Criar o app `crm` e modelar `Pipeline`, `PipelineStage`, `Deal` e `DealActivity`
- [ ] Implementar o CRUD de pipelines com marcação de pipeline padrão
- [ ] Implementar o CRUD de etapas com nome, cor e ordem personalizáveis
- [ ] Restringir o seletor de cor de etapa à paleta do design system
- [ ] Implementar o CRUD de negociações, com suporte a lead sem cliente cadastrado
- [ ] Implementar a visão grid com filtros, ordenação e paginação
- [ ] Implementar a visão kanban com uma coluna por etapa
- [ ] Integrar o SortableJS para arrastar cards entre etapas
- [ ] Implementar a persistência assíncrona da mudança de etapa e da ordenação
- [ ] Registrar automaticamente a atividade de mudança de etapa
- [ ] Implementar a conversão de negociação em proposta a partir do card
- [ ] Implementar o registro manual de atividades na negociação
- [ ] Garantir a usabilidade do kanban com scroll horizontal no mobile
- [ ] Registrar as entidades no admin
- [ ] Documentar o CRM em `docs/apps/crm.md`

### Sprint 10 — Dashboard e relatórios

- [ ] Criar o app `dashboard` e implementar os serviços de agregação
- [ ] Implementar os cartões de métrica da corretora
- [ ] Implementar o gráfico de produção mensal com Chart.js
- [ ] Implementar o gráfico de distribuição por ramo
- [ ] Implementar o gráfico de ranking de seguradoras
- [ ] Implementar o gráfico de sinistralidade
- [ ] Implementar o gráfico de funil de negociações com um nível por etapa do pipeline
- [ ] Exibir quantidade, valor e taxa de conversão em cada nível do funil
- [ ] Implementar o filtro global de período do dashboard
- [ ] Cachear as agregações no Redis com TTL curto e invalidação por evento
- [ ] Criar o app `reports` e modelar `ReportExecution`
- [ ] Implementar a tela de catálogo de relatórios com filtros
- [ ] Implementar o relatório de produção por período
- [ ] Implementar os relatórios de comissões por agente e por produtor
- [ ] Implementar os relatórios de apólices a vencer, renovações, sinistralidade e funil
- [ ] Implementar a exportação em PDF com ReportLab, com cabeçalho e identidade do tenant
- [ ] Implementar o pós-processamento em PyPDF com numeração de páginas e metadados
- [ ] Implementar a exportação em CSV com resposta em streaming
- [ ] Implementar a geração assíncrona em Celery para relatórios volumosos
- [ ] Entregar os arquivos gerados exclusivamente pela view de media protegida
- [ ] Documentar os relatórios em `docs/apps/reports.md`

### Sprint 11 — Notificações in-app

- [ ] Criar o app `notifications` e modelar `Notification`
- [ ] Implementar o serviço de criação de notificação por usuário
- [ ] Implementar o indicador de notificações não lidas na topbar
- [ ] Implementar o dropdown com as notificações recentes
- [ ] Implementar a atualização do contador via polling HTMX
- [ ] Implementar a marcação de notificação como lida, individual e em lote
- [ ] Implementar a tela de listagem completa de notificações com paginação
- [ ] Conectar os signals de eventos relevantes em `signals.py` dos apps correspondentes
- [ ] Registrar a entidade no admin
- [ ] Documentar as notificações em `docs/apps/notifications.md`

### Sprint 12 — Agente de IA de resumo

- [ ] Criar o app `ai_agents` e modelar `AISummaryRun`
- [ ] Adicionar os campos `ai_summary` e `ai_summary_generated_at` em Cliente, Proposta, Apólice, Sinistro e Negociação
- [ ] Configurar o cliente LangChain com o modelo lido de `OPENAI_MODEL` no `.env`
- [ ] Implementar as tools de leitura ao banco com filtro obrigatório por tenant
- [ ] Implementar o grafo LangGraph de resumo com os nós de contexto, tools, geração e validação
- [ ] Implementar os prompts de sistema versionados por entidade
- [ ] Implementar a task Celery de geração de resumo com retry e backoff
- [ ] Persistir o resultado no campo de texto da entidade e registrar a execução
- [ ] Implementar o botão "Resumir com IA" nos detalhes das cinco entidades
- [ ] Aplicar o estado de carregamento no botão e o aviso de notificação futura
- [ ] Garantir que o request retorne imediatamente após enfileirar a task
- [ ] Criar a notificação in-app ao concluir o resumo
- [ ] Atualizar o resumo na interface sem recarregar a página
- [ ] Implementar os guardrails de limite de tokens, limite de tools e timeout
- [ ] Tratar falhas notificando o usuário sem quebrar a interface
- [ ] Registrar `AISummaryRun` no admin com filtros por status e entidade
- [ ] Documentar o agente de resumo em `docs/ia/summary-agent.md`

### Sprint 13 — Chat com o agente de IA

- [ ] Criar o app `ai_chat` e modelar `ChatSession` e `ChatMessage`
- [ ] Implementar as tools de consulta agregada à base da corretora
- [ ] Aplicar nas tools o filtro por tenant e por escopo do papel do usuário
- [ ] Implementar o grafo LangGraph de chat com memória da sessão
- [ ] Implementar a tela de chat acessível pelo menu lateral
- [ ] Implementar a barra lateral de sessões salvas por usuário
- [ ] Implementar criar, renomear, arquivar e excluir sessão
- [ ] Gerar o título da sessão a partir da primeira mensagem
- [ ] Implementar a view de streaming com `StreamingHttpResponse` e SSE
- [ ] Implementar a renderização incremental do Markdown durante o stream
- [ ] Implementar a conversão de Markdown para HTML com sanitização ao recarregar a sessão
- [ ] Persistir as mensagens de usuário, assistente e tools com contagem de tokens
- [ ] Implementar o indicador visual de execução de tool durante a resposta
- [ ] Implementar os guardrails de janela de histórico e limite de tools
- [ ] Garantir a usabilidade completa do chat no mobile
- [ ] Registrar as entidades no admin
- [ ] Documentar o agente de chat em `docs/ia/chat-agent.md`

### Sprint 14 — Dados de demonstração e admin completo

- [ ] Implementar o management command `seed_demo_data` com Faker em locale pt_BR
- [ ] Suportar os argumentos `--tenants`, `--months` e `--reset`
- [ ] Gerar múltiplos tenants com donos, agentes e produtores, incluindo produtores diretos
- [ ] Gerar clientes PF e PJ, seguradoras, ramos e itens cobertos de todos os tipos
- [ ] Gerar propostas em todos os status com datas variadas ao longo do tempo
- [ ] Gerar apólices ativas, vencidas, canceladas e renovadas, com múltiplos itens cobertos
- [ ] Gerar parcelas em diferentes estados de pagamento
- [ ] Gerar sinistros em todos os status vinculados a itens cobertos
- [ ] Gerar endossos de todos os tipos e renovações em todas as etapas
- [ ] Gerar regras e lançamentos de comissão com repasses pendentes e pagos
- [ ] Gerar pipelines com etapas coloridas e negociações em todas as fases do funil
- [ ] Gerar anexos de exemplo e notificações in-app
- [ ] Revisar todos os `ModelAdmin` garantindo `list_display`, `list_filter`, `search_fields` e `date_hierarchy`
- [ ] Configurar `autocomplete_fields` em todas as FKs de alto volume
- [ ] Configurar os inlines nos relacionamentos naturais de cada entidade
- [ ] Marcar `created_at` e `updated_at` como somente leitura em todos os admins
- [ ] Filtrar o admin por tenant para usuários staff não-superusuários
- [ ] Validar a visualização das tasks do Celery pelo `dj-celery-panel`

### Sprint 15 — Refinamento, desempenho e fechamento

- [ ] Auditar todas as rotas garantindo autenticação e permissão nas sensíveis
- [ ] Auditar todas as queries eliminando N+1 com `select_related` e `prefetch_related`
- [ ] Revisar e completar os índices compostos por tenant nos campos filtráveis
- [ ] Confirmar a paginação em todas as listagens do sistema
- [ ] Testar manualmente o isolamento entre tenants em todas as telas e exportações
- [ ] Testar manualmente o acesso negado a anexos de outro tenant
- [ ] Revisar os estados de carregamento, vazio e erro de todas as telas
- [ ] Revisar todos os textos da interface garantindo português brasileiro correto
- [ ] Revisar todo o código-fonte garantindo nomes e comentários em inglês
- [ ] Revisar a aderência de cores, tipografia e componentes ao design system
- [ ] Validar o contraste AA em todas as telas nos temas claro e escuro
- [ ] Validar a responsividade completa em mobile, tablet e desktop
- [ ] Confirmar que nenhuma chamada de LLM ocorre no ciclo request/response
- [ ] Executar `pip freeze > requirements.txt` e confirmar o arquivo atualizado na raiz
- [ ] Confirmar que o `.env` está fora do versionamento e o `.env.example` está completo
- [ ] Confirmar que os signals estão exclusivamente em `signals.py` de cada app
- [ ] Confirmar o uso de aspas simples e a conformidade com a PEP 8 em todo o código
- [ ] Atualizar integralmente a documentação em `docs/` e validar os diagramas Mermaid
- [ ] Finalizar o `README.md` com o setup nativo completo e todos os comandos
- [ ] Executar o setup do zero seguindo o `README.md` e corrigir divergências
- [ ] Publicar a versão final no GitHub com tag de release

---

## 19. Definition of Done

Uma tarefa só é considerada concluída quando:

- [ ] O código segue PEP 8 e usa aspas simples em Python.
- [ ] Nomes, funções, classes e comentários estão em inglês; a interface está em português brasileiro.
- [ ] Todo model criado possui `created_at`, `updated_at` e, quando de domínio, `tenant`.
- [ ] A view é Class Based e aplica os mixins de tenant e permissão.
- [ ] Nenhuma consulta escapa do filtro de tenant.
- [ ] Nenhum arquivo de media é acessível sem passar pela view protegida.
- [ ] Nenhuma operação pesada roda no ciclo request/response.
- [ ] A interface respeita integralmente o design system e é responsiva.
- [ ] Signals, quando usados, estão em `signals.py`.
- [ ] O `requirements.txt` da raiz está atualizado.
- [ ] Nenhum segredo foi versionado.
- [ ] A documentação em `docs/` foi atualizada.
- [ ] O commit foi enviado ao GitHub.

---

## 20. Matriz de Rastreabilidade

### 20.1 Regras técnicas → seções do PRD

| Regra | Descrição resumida | Onde está atendida |
| --- | --- | --- |
| 1 | Python > 3.13 | §4.1, Sprint 0 |
| 2 | `.venv` na raiz | §13.4, §15, Sprint 0 |
| 3 | `requirements.txt` na raiz e atualizado | §4.4, §15, Sprint 0, Sprint 15 |
| 4 | Multi-tenant shared schema | §5 (inteira) |
| 5 | Media sempre por view protegida | §12.1, RF06, Sprint 8 |
| 6 | Auth nativa do Django | §8/RF01, Sprint 2 |
| 7 | Login por e-mail (`USERNAME_FIELD`) | §7.3, RF01, Sprint 2 |
| 8 | E-mail via `django.core.mail` | §8/RF15, §14, Sprint 2 |
| 9 | Um app por domínio, na raiz | §6, §15 |
| 10 | Apps `core` e `base` | §6, §15 |
| 11 | Código em inglês, UI em pt-BR | §11.6, §16, Sprint 15 |
| 12 | Timezone `America/Sao_Paulo` | §14, Sprint 0 |
| 13 | `created_at` e `updated_at` em todo model | §5.3, §7, §19 |
| 14 | Sem testes automatizados | §2.2, §16 |
| 15 | Credenciais em `.env` com `django-environ` | §14, §9/RNF07 |
| 16 | Um único `settings.py` | §14, §15 |
| 17 | PostgreSQL | §4.1, §13.2 |
| 18 | Ambiente local nativo, sem containers | §13 (inteira) |
| 19 | Celery para tarefas pesadas | §4.1, §9/RNF04, §13.4 |
| 20 | Redis como broker, result backend e cache | §4.1, §13.2, §14 |
| 21 | `dj-celery-panel` no admin | §4.1, RF14, Sprint 0, Sprint 14 |
| 22 | Class Based Views e recursos nativos | §16, todas as sprints de feature |
| 23 | Signals em `signals.py` | §15, §16, §19 |
| 24 | PDF com ReportLab e PyPDF | §4.3, RF07, Sprint 10 |
| 25 | `docs/` com MkDocs e Mermaid | §17, Sprint 0 |
| 26 | Command de carga de dados fake | §13.5, Sprint 14 |
| 27 | Design system como fonte única | §11 (inteira) |
| 28 | LangChain > 1.0 + LangGraph + `gpt-5.5-mini` | §10 (inteira) |
| 29 | `GET /health/` sem banco e sem auth | §8, Sprint 0 |
| 30 | `README.md` com setup local nativo | §13.4, §15, Sprint 0, Sprint 15 |

### 20.2 Requisitos funcionais → sprints

| RF | Descrição | Sprint |
| --- | --- | --- |
| RF01 | Usuários, autenticação e papéis | 2 |
| RF02 | Clientes, Seguradoras e Ramos | 5 |
| RF03 | Propostas e Apólices | 7 |
| RF04 | Botão "Gerar Apólice" | 7 |
| RF05 | Sinistros | 8 |
| RF06 | Anexos com controle de permissão | 8 |
| RF07 | Relatórios em PDF e CSV | 10 |
| RF08 | Dashboard com funil | 10 |
| RF09 | Itens Cobertos | 5 |
| RF10 | Renovações | 7 |
| RF11 | Agentes, Produtores e Comissões | 6 |
| RF12 | CRM grid e kanban | 9 |
| RF13 | Endossos | 7 |
| RF14 | Django Admin completo | 14 |
| RF15 | Landing page, cadastro e recuperação de senha | 4 |
| RF16 | Agente de IA de resumo | 12 |
| RF17 | Chat com o agente de IA | 13 |

### 20.3 Requisitos não funcionais → seções

| RNF | Descrição | Onde está atendida |
| --- | --- | --- |
| RNF01 | Responsividade total | §11, Sprint 3, Sprint 15 |
| RNF02 | Segurança e isolamento | §5.2, §12, Sprint 15 |
| RNF03 | UI/UX e contraste | §11.6, Sprint 3, Sprint 15 |
| RNF04 | Nada bloqueante na interface | §9/RNF04, §10, Sprint 12, Sprint 13 |
| RNF05 | Desempenho | §9/RNF05, Sprint 15 |
| RNF06 | Inicialização ordenada com `wait_for_db` | §13.3, Sprint 0 |
| RNF07 | Segredos apenas no `.env` | §14, §9/RNF07 |

---

**Fim do documento.**
