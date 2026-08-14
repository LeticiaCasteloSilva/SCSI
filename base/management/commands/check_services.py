from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    """Report the availability of every external service the project depends on."""

    help = 'Verifica a disponibilidade de PostgreSQL, Redis e RabbitMQ.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fail-fast',
            action='store_true',
            help='Encerra com codigo 1 se algum servico estiver indisponivel.',
        )

    def handle(self, *args, **options):
        results = [
            self.check_postgres(),
            self.check_redis(),
            self.check_rabbitmq(),
        ]

        self.stdout.write('')
        for name, ok, detail in results:
            label = self.style.SUCCESS('OK') if ok else self.style.ERROR('FALHOU')
            self.stdout.write(f'{name:<12} {label:<10} {detail}')

        failed = [name for name, ok, _ in results if not ok]
        self.stdout.write('')

        if failed:
            self.stdout.write(
                self.style.WARNING(f'Servicos indisponiveis: {", ".join(failed)}')
            )
            if options['fail_fast']:
                raise SystemExit(1)
        else:
            self.stdout.write(self.style.SUCCESS('Todos os servicos estao disponiveis.'))

    def check_postgres(self):
        try:
            connection = connections['default']
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute('select version()')
                version = cursor.fetchone()[0]
            return 'PostgreSQL', True, version.split(' on ')[0]
        except Exception as error:
            return 'PostgreSQL', False, str(error).strip().splitlines()[0]

    def check_redis(self):
        url = settings.CACHES['default']['LOCATION']
        try:
            import redis

            client = redis.Redis.from_url(url, socket_connect_timeout=3)
            client.ping()
            version = client.info('server').get('redis_version', 'desconhecida')
            return 'Redis', True, f'versao {version} em {self.safe(url)}'
        except Exception as error:
            return 'Redis', False, str(error).strip().splitlines()[0]

    def check_rabbitmq(self):
        url = settings.CELERY_BROKER_URL
        if not url:
            return 'RabbitMQ', False, 'CELERY_BROKER_URL nao configurada no .env'
        try:
            from kombu import Connection

            with Connection(url, connect_timeout=5) as connection:
                connection.connect()
            return 'RabbitMQ', True, f'broker conectado em {self.safe(url)}'
        except Exception as error:
            return 'RabbitMQ', False, str(error).strip().splitlines()[0]

    @staticmethod
    def safe(url):
        """Return the url without its credentials, safe to print in a terminal."""
        parsed = urlparse(url)
        host = parsed.hostname or ''
        port = f':{parsed.port}' if parsed.port else ''
        return f'{parsed.scheme}://{host}{port}{parsed.path}'
