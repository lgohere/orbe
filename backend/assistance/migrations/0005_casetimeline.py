# Generated migration for CaseTimeline model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistance', '0004_add_bank_info_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseTimeline',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[
                    ('case_created', 'Caso Criado'),
                    ('submitted_for_approval', 'Enviado para Aprovação'),
                    ('approved', 'Aprovado'),
                    ('rejected', 'Rejeitado'),
                    ('bank_info_submitted', 'Dados Bancários Informados'),
                    ('transfer_confirmed', 'Transferência Confirmada pelo Admin'),
                    ('member_proof_submitted', 'Comprovante do Membro Enviado'),
                    ('completed', 'Caso Concluído'),
                    ('attachment_uploaded', 'Anexo Adicionado'),
                    ('status_changed', 'Status Alterado'),
                    ('comment_added', 'Comentário Adicionado')
                ], db_index=True, max_length=50, verbose_name='Tipo de Evento')),
                ('description', models.TextField(blank=True, help_text='Descrição detalhada do evento', verbose_name='Descrição')),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Dados adicionais do evento (JSON)', verbose_name='Metadados')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Criado em')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeline_events', to='assistance.assistancecase', verbose_name='Caso')),
                ('user', models.ForeignKey(blank=True, help_text='Usuário que realizou a ação', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='case_events', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Evento da Timeline',
                'verbose_name_plural': 'Eventos da Timeline',
                'ordering': ['created_at'],
                'indexes': [
                    models.Index(fields=['case', 'created_at'], name='assistance_case_id_created_idx'),
                    models.Index(fields=['event_type', 'created_at'], name='assistance_event_type_created_idx'),
                ],
            },
        ),
    ]
