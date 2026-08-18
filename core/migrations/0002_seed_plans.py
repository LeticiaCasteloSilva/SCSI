from django.db import migrations

PLANS = [
    {
        'slug': 'free',
        'name': 'Free',
        'price': '0.00',
        'is_enabled': True,
        'max_users': 3,
        'description': 'Plano gratuito para começar a operar a corretora.',
    },
    {
        'slug': 'pro',
        'name': 'Pro',
        'price': '0.00',
        'is_enabled': False,
        'max_users': 15,
        'description': 'Em breve.',
    },
    {
        'slug': 'business',
        'name': 'Business',
        'price': '0.00',
        'is_enabled': False,
        'max_users': 50,
        'description': 'Em breve.',
    },
]


def create_plans(apps, schema_editor):
    Plan = apps.get_model('core', 'Plan')
    for plan in PLANS:
        Plan.objects.update_or_create(slug=plan['slug'], defaults=plan)


def delete_plans(apps, schema_editor):
    Plan = apps.get_model('core', 'Plan')
    Plan.objects.filter(slug__in=[plan['slug'] for plan in PLANS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_plans, delete_plans),
    ]
