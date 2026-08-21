"""Verificação manual sob demanda do isolamento multi-tenant.

Não é teste automatizado: nada aqui roda em CI nem no ciclo de build. É um
comando que a pessoa desenvolvedora dispara quando quer conferir, contra o
banco real, que as camadas de isolamento continuam de pé depois de uma
mudança em managers, middleware ou models.

Tudo acontece dentro de uma transação que sofre rollback no final, então o
banco fica exatamente como estava — mesmo se uma checagem falhar.
"""

import secrets

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, models, transaction

from base.context import get_current_tenant, tenant_context
from base.models import TenantAwareModel
from base.validators import build_cnpj, format_cnpj, validate_cnpj
from core.models import Plan, Tenant


class ProbePolicy(TenantAwareModel):
    """Stand-in de uma entidade de domínio, criada e destruída pelo comando."""

    number = models.CharField(max_length=30)

    class Meta:
        app_label = 'base'
        db_table = 'probe_tenant_isolation_policy'


class ProbeClaim(TenantAwareModel):
    """Filho de ProbePolicy, para exercitar a validação cross-tenant."""

    policy = models.ForeignKey(ProbePolicy, on_delete=models.CASCADE)

    class Meta:
        app_label = 'base'
        db_table = 'probe_tenant_isolation_claim'


class IsolationBreach(Exception):
    """Sinaliza que ao menos uma checagem falhou."""


class Command(BaseCommand):
    help = 'Verifica, contra o banco real, as camadas de isolamento multi-tenant.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fail-fast',
            action='store_true',
            help='Encerra com codigo 1 se alguma checagem falhar.',
        )

    def handle(self, *args, **options):
        self.passed = 0
        self.failed = []

        try:
            with transaction.atomic():
                self.setup_schema()
                self.run_checks()
                # A sonda não persiste nada: o rollback desfaz as tabelas
                # temporárias e todas as linhas criadas durante as checagens.
                raise IsolationBreach('rollback')
        except IsolationBreach:
            pass

        self.report(options['fail_fast'])

    # Infraestrutura da sonda

    def setup_schema(self):
        with connection.schema_editor() as editor:
            editor.create_model(ProbePolicy)
            editor.create_model(ProbeClaim)

    def assert_that(self, label, condition, detail=''):
        if condition:
            self.passed += 1
            mark = self.style.SUCCESS('OK')
        else:
            self.failed.append(label)
            mark = self.style.ERROR('FALHOU')
        suffix = f'  {detail}' if detail else ''
        self.stdout.write(f'  [{mark}] {label}{suffix}')

    def section(self, title):
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING(title))

    # Checagens

    def run_checks(self):
        alpha, beta = self.create_tenants()
        self.check_validators()
        self.check_model_wiring()
        self.check_read_isolation(alpha, beta)
        self.check_fail_closed(alpha)
        self.check_cross_tenant_clean(alpha, beta)
        self.check_context_nesting(alpha, beta)

    def build_unused_cnpj(self):
        """Mint a valid CNPJ that no tenant currently holds.

        Hardcoded documents would make the probe blow up with IntegrityError
        on any database that already contains them, so the sonda derives its
        own and checks them against the table before using them.
        """
        for _ in range(200):
            candidate = build_cnpj(f'{secrets.randbelow(10 ** 12):012d}')
            if not Tenant.objects.filter(cnpj=candidate).exists():
                return candidate
        raise CommandError('Nao foi possivel gerar um CNPJ livre para a sonda.')

    def create_tenants(self):
        plan = Plan.objects.filter(slug='free').first()
        if plan is None:
            plan = Plan.objects.create(
                slug='free', name='Free', is_enabled=True, max_users=3
            )

        suffix = secrets.token_hex(4)
        alpha = Tenant.objects.create(
            legal_name=f'Sonda Alpha {suffix} LTDA',
            trade_name=f'Sonda Alpha {suffix}',
            cnpj=self.build_unused_cnpj(),
            plan=plan,
        )
        beta = Tenant.objects.create(
            legal_name=f'Sonda Beta {suffix} LTDA',
            trade_name=f'Sonda Beta {suffix}',
            cnpj=self.build_unused_cnpj(),
            plan=plan,
        )
        return alpha, beta

    def check_validators(self):
        self.section('1. Validador de CNPJ')

        for valid in ['11.222.333/0001-81', '11222333000181']:
            try:
                validate_cnpj(valid)
                accepted = True
            except ValidationError:
                accepted = False
            self.assert_that(f'aceita CNPJ valido {valid}', accepted)

        for invalid, why in [
            ('11.222.333/0001-82', 'digito verificador errado'),
            ('11111111111111', 'digitos repetidos'),
            ('123', 'tamanho invalido'),
        ]:
            try:
                validate_cnpj(invalid)
                rejected = False
            except ValidationError:
                rejected = True
            self.assert_that(f'rejeita {invalid}', rejected, f'({why})')

        self.assert_that(
            'normaliza CNPJ sem mascara',
            format_cnpj('11222333000181') == '11.222.333/0001-81',
        )

    def check_model_wiring(self):
        self.section('2. Ligacao dos managers no model abstrato')

        field_names = [field.name for field in ProbePolicy._meta.fields]
        self.assert_that('TenantAwareModel injeta a FK tenant', 'tenant' in field_names)
        self.assert_that(
            'TenantAwareModel injeta created_at e updated_at',
            'created_at' in field_names and 'updated_at' in field_names,
        )
        self.assert_that(
            'default manager e o filtrado (TenantManager)',
            type(ProbePolicy._meta.default_manager).__name__ == 'TenantManager',
            '-> usado por views, forms e admin',
        )
        self.assert_that(
            'base manager e o irrestrito (all_tenants)',
            ProbePolicy._meta.base_manager.name == 'all_tenants',
            '-> usado pelos internos do Django',
        )

    def check_read_isolation(self, alpha, beta):
        self.section('3. Isolamento de leitura entre tenants')

        alpha_policy = ProbePolicy.all_tenants.create(tenant=alpha, number='AP-0001')
        beta_policy = ProbePolicy.all_tenants.create(tenant=beta, number='BP-0001')
        ProbePolicy.all_tenants.create(tenant=beta, number='BP-0002')

        self.assert_that(
            'sonda inseriu 3 apolices (1 Alpha, 2 Beta)',
            ProbePolicy.all_tenants.count() == 3,
        )

        with tenant_context(alpha):
            visible = list(ProbePolicy.objects.values_list('number', flat=True))
            self.assert_that(f'Alpha enxerga apenas {visible}', visible == ['AP-0001'])
            self.assert_that(
                'Alpha NAO alcanca apolice da Beta nem por pk',
                ProbePolicy.objects.filter(pk=beta_policy.pk).first() is None,
            )

        with tenant_context(beta):
            visible = sorted(ProbePolicy.objects.values_list('number', flat=True))
            self.assert_that(
                f'Beta enxerga apenas {visible}', visible == ['BP-0001', 'BP-0002']
            )
            self.assert_that(
                'Beta NAO alcanca apolice da Alpha nem por pk',
                ProbePolicy.objects.filter(pk=alpha_policy.pk).first() is None,
            )

        with tenant_context(alpha):
            ProbePolicy.objects.create(tenant=alpha, number='AP-0002')
            self.assert_that('escrita da Alpha eleva a contagem dela para 2',
                       ProbePolicy.objects.count() == 2)
        with tenant_context(beta):
            self.assert_that('Beta permanece com 2, intocada pela escrita da Alpha',
                       ProbePolicy.objects.count() == 2)

    def check_fail_closed(self, alpha):
        self.section('4. Fail-closed fora de contexto de tenant')

        self.assert_that(
            'sem tenant em contexto, objects retorna 0 linhas',
            ProbePolicy.objects.count() == 0,
            '-> falha fechado, nao vaza a tabela inteira',
        )
        self.assert_that(
            'all_tenants continua enxergando todas as 4',
            ProbePolicy.all_tenants.count() == 4,
        )
        with tenant_context(alpha):
            self.assert_that(
                'dentro do contexto o filtro volta a valer',
                ProbePolicy.objects.count() == 2,
            )

    def check_cross_tenant_clean(self, alpha, beta):
        self.section('5. Validacao cross-tenant no clean()')

        alpha_policy = ProbePolicy.all_tenants.filter(tenant=alpha).first()
        beta_policy = ProbePolicy.all_tenants.filter(tenant=beta).first()

        same_tenant = ProbeClaim(tenant=alpha, policy=alpha_policy)
        try:
            same_tenant.full_clean()
            accepted = True
            detail = ''
        except ValidationError as error:
            accepted = False
            detail = str(error.message_dict)
        self.assert_that('aceita filho apontando pai do mesmo tenant', accepted, detail)

        crossing = ProbeClaim(tenant=alpha, policy=beta_policy)
        try:
            crossing.full_clean()
            self.assert_that(
                'REJEITA filho da Alpha apontando pai da Beta',
                False,
                '-> VAZAMENTO: o clean() deixou passar',
            )
        except ValidationError as error:
            messages = error.message_dict.get('policy', [])
            self.assert_that(
                'REJEITA filho da Alpha apontando pai da Beta',
                'Este registro pertence a outra corretora.' in messages,
                f'-> {messages}',
            )

    def check_context_nesting(self, alpha, beta):
        self.section('6. Ciclo de vida do ContextVar')

        self.assert_that('fora de qualquer contexto, tenant e None',
                   get_current_tenant() is None)

        with tenant_context(alpha):
            outer_before = get_current_tenant()
            with tenant_context(beta):
                inner = get_current_tenant()
            outer_after = get_current_tenant()

        self.assert_that(
            'contexto aninhado empilha e desempilha corretamente',
            outer_before == alpha and inner == beta and outer_after == alpha,
            f'-> {outer_before} > {inner} > {outer_after}',
        )
        self.assert_that('ao sair, o contexto volta a ficar vazio',
                   get_current_tenant() is None)

    # Relatório

    def report(self, fail_fast):
        total = self.passed + len(self.failed)
        self.stdout.write('')

        if self.failed:
            self.stdout.write(
                self.style.ERROR(f'{len(self.failed)} de {total} checagens falharam:')
            )
            for label in self.failed:
                self.stdout.write(self.style.ERROR(f'  - {label}'))
            self.stdout.write('')
            if fail_fast:
                raise CommandError(
                    f'{len(self.failed)} checagem(ns) de isolamento falharam.'
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'{self.passed} de {total} checagens passaram. '
                    'Isolamento multi-tenant integro.'
                )
            )
        self.stdout.write(
            'Nenhum dado persistido: a sonda roda dentro de uma transacao revertida.'
        )
