# Camada de IA

Dois agentes construídos com **LangChain > 1.0** e **LangGraph**, usando o modelo definido em `OPENAI_MODEL` no `.env`:

| Agente | App | Execução |
| --- | --- | --- |
| Resumo ("Resumir com IA") | `ai_agents` | Assíncrona via Celery |
| Chat | `ai_chat` | Streaming SSE |

## Princípios invioláveis

- Toda tool recebe `tenant_id` e `user_id` no estado do grafo e **filtra obrigatoriamente por eles**.
- Tools são **somente leitura** — nenhuma escrita no banco.
- Nenhuma chamada a LLM ocorre no ciclo request/response síncrono.
- O chat aplica escopo duplo: tenant + papel do usuário.

Especificação completa no `PRD.md` §10. Implementação nas Sprints 12 e 13.
