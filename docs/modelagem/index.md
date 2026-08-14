# Modelagem de dados

O diagrama ER completo e o dicionário de dados de cada entidade estão especificados no `PRD.md` §7.

## Estado da implementação

Sprint 0 entregou apenas o model abstrato `base.models.TimeStampedModel`, que fornece os campos de auditoria obrigatórios em todo model do sistema:

| Campo | Tipo | Notas |
| --- | --- | --- |
| `created_at` | `DateTimeField` | `auto_now_add`, indexado |
| `updated_at` | `DateTimeField` | `auto_now` |

As entidades de domínio começam na Sprint 1 (`core.Tenant`, `core.Plan`) e seguem pelas sprints seguintes.
