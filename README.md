# SCSI — Sistema de Gestão para Corretora de Seguros Inteligente

Plataforma multi-tenant para corretoras de seguros, com agentes de IA construídos em LangChain e LangGraph.

Gestão completa da operação — clientes, seguradoras, ramos, itens cobertos, propostas, apólices, endossos, renovações, sinistros, comissões e pipeline comercial — somada a um agente de resumo automático e a um chat que responde perguntas sobre a carteira em linguagem natural.

> A especificação completa do produto está em [`PRD.md`](PRD.md). As diretrizes de implementação estão em [`CLAUDE.md`](CLAUDE.md).

## Stack

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.13 |
| Framework | Django 6.1 |
| Banco de dados | PostgreSQL 16 |
| Cache e result backend | Redis 7.4 |
| Broker de mensagens | RabbitMQ |
| Fila assíncrona | Celery 5.6 (worker + beat) |
| IA | LangChain > 1.0 + LangGraph |
| Documentação | MkDocs Material com Mermaid |

Todo o ambiente roda **nativamente**, sem containers.

## Pré-requisitos

- macOS ou Linux
- Python 3.13 ou superior
- PostgreSQL 16, Redis 7 e RabbitMQ

## 1. Serviços

### Linux

```bash
sudo apt install postgresql-16 redis-server rabbitmq-server
sudo systemctl enable --now postgresql redis-server rabbitmq-server
```

### macOS com Homebrew

```bash
brew install postgresql@16 redis rabbitmq
brew services start postgresql@16
brew services start redis
brew services start rabbitmq
```

### macOS 12 (Monterey) e anteriores

O Homebrew não suporta mais essas versões — não há bottles pré-compiladas e toda fórmula compila do source. O caminho testado neste projeto usa **Postgres.app** e **Redis compilado**, com o RabbitMQ em serviço gerenciado. O passo a passo completo está em [`docs/setup/ambiente-local.md`](docs/setup/ambiente-local.md).

### Banco e usuário

```bash
psql -d postgres <<'SQL'
CREATE ROLE scsi WITH LOGIN PASSWORD 'sua-senha-aqui' CREATEDB;
CREATE DATABASE scsi OWNER scsi ENCODING 'UTF8';
SQL
```

### Vhost do RabbitMQ

```bash
sudo rabbitmqctl add_user scsi sua-senha-aqui
sudo rabbitmqctl add_vhost scsi
sudo rabbitmqctl set_permissions -p scsi scsi '.*' '.*' '.*'
```

Se a instalação nativa do RabbitMQ não for viável, use um serviço gerenciado no free tier (CloudAMQP) e aponte `CELERY_BROKER_URL` para a URL fornecida.

## 2. Projeto

```bash
git clone https://github.com/LeticiaCasteloSilva/SCSI.git
cd SCSI

python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Variáveis de ambiente

```bash
cp .env.example .env
```

O `.env` fica na raiz e **nunca** é versionado. Gere uma `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

| Variável | Descrição |
| --- | --- |
| `SECRET_KEY` | Chave secreta do Django |
| `DEBUG` | `True` em desenvolvimento |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `DATABASE_URL` | `postgres://scsi:senha@127.0.0.1:5432/scsi` |
| `CELERY_BROKER_URL` | `amqp://scsi:senha@localhost:5672/scsi` |
| `CELERY_RESULT_BACKEND` | `redis://127.0.0.1:6379/1` |
| `REDIS_CACHE_URL` | `redis://127.0.0.1:6379/2` |
| `TIME_ZONE` | `America/Sao_Paulo` |
| `LANGUAGE_CODE` | `pt-br` |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` | Credenciais SMTP |
| `DEFAULT_FROM_EMAIL` | Remetente padrão |
| `OPENAI_API_KEY` | Chave da API da OpenAI |
| `OPENAI_MODEL` | Modelo dos agentes |
| `AI_MAX_TOOL_CALLS`, `AI_TIMEOUT_SECONDS` | Guardrails dos agentes |
| `MEDIA_ROOT` | Raiz dos arquivos protegidos |
| `MAX_UPLOAD_SIZE_MB` | Tamanho máximo de anexo |
| `WAIT_FOR_DB_TIMEOUT` | Timeout do `wait_for_db` |

Sem `EMAIL_HOST` definido e com `DEBUG=True`, os e-mails são impressos no console.

## 4. Subir a aplicação

```bash
python manage.py wait_for_db
python manage.py check_services
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Em terminais separados, sempre com o `.venv` ativado:

```bash
celery -A core worker -l info
celery -A core beat -l info
```

| Endereço | O que é |
| --- | --- |
| `http://127.0.0.1:8000/` | Aplicação |
| `http://127.0.0.1:8000/health/` | Health check, sem autenticação |
| `http://127.0.0.1:8000/admin/` | Admin do Django |
| `http://127.0.0.1:8000/admin/celery-panel/` | Painel de tasks do Celery |

## Comandos

| Objetivo | Comando |
| --- | --- |
| Aguardar o banco | `python manage.py wait_for_db` |
| Verificar serviços | `python manage.py check_services` |
| Aplicar migrações | `python manage.py migrate` |
| Carregar dados fake | `python manage.py seed_demo_data` |
| Subir a aplicação | `python manage.py runserver` |
| Worker Celery | `celery -A core worker -l info` |
| Beat Celery | `celery -A core beat -l info` |
| Compilar CSS | `./tailwindcss -i static/src/input.css -o static/css/app.css --watch` |
| Servir a documentação | `mkdocs serve -a 127.0.0.1:8001` |
| Atualizar dependências | `pip freeze > requirements.txt` |

## Documentação

```bash
mkdocs serve -a 127.0.0.1:8001
```

## Convenções

- PEP 8, aspas simples em Python
- Código-fonte em inglês, interface em português brasileiro
- Class Based Views e recursos nativos do Django
- Todo model tem `created_at` e `updated_at`; toda entidade de domínio tem `tenant`
- Signals exclusivamente em `signals.py` de cada app
- Arquivos de media nunca são servidos por URL pública
- Este projeto não usa testes automatizados (decisão explícita — `PRD.md` §2.2)
