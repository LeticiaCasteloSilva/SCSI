# Modelagem de dados

O diagrama ER completo e o dicionário de dados de cada entidade estão especificados no `PRD.md` §7.

## Estado da implementação

Sprint 0 entregou apenas o model abstrato `base.models.TimeStampedModel`, que fornece os campos de auditoria obrigatórios em todo model do sistema:

| Campo | Tipo | Notas |
| --- | --- | --- |
| `created_at` | `DateTimeField` | `auto_now_add`, indexado |
| `updated_at` | `DateTimeField` | `auto_now` |

A Sprint 1 acrescentou o abstrato `base.models.TenantAwareModel`, que herda esses campos e injeta a FK `tenant`, e os dois primeiros models concretos:

| Model | App | Papel |
| --- | --- | --- |
| `Plan` | `core` | Catálogo de planos; só o Free tem `is_enabled=True` |
| `Tenant` | `core` | A corretora — raiz do isolamento, com Razão Social e CNPJ validado |

Nenhum dos dois é tenant-aware: `Plan` é catálogo global e `Tenant` é a própria raiz.

As demais entidades de domínio seguem pelas sprints seguintes, todas herdando de `TenantAwareModel`.
