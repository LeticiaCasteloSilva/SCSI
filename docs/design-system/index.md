# Design System

A fonte da verdade visual é `design_system/design-system.html`. O arquivo é o shell de uma SPA — **os tokens reais estão no bundle compilado** `design_system/css/index-CuopC2LA.css`.

## Características

- Bundle Tailwind/shadcn com paleta **neutra monocromática** (todos os tokens em hue 0, saturação 0%)
- `--radius: 0.5rem`
- Tipografia: **Inter** (300, 400, 500, 600, 700)
- Ícones: web component `iconify-icon`

Não existe cor de marca: o primário é preto no tema claro e branco no escuro. Cores de status e das etapas do CRM derivam desses tokens e de `--destructive`.

A tabela completa dos 23 tokens em claro e escuro está no `PRD.md` §11.2.

## Regras

- Nenhuma cor, fonte, raio ou componente fora do arquivo de referência.
- Nada de `#hex` ou `rgb()` em template ou CSS de app — apenas classes utilitárias mapeadas nos tokens.
- Componentes vivem uma única vez em `base/templates/base/components/`; apps não criam variantes próprias.

Implementação na Sprint 3.
