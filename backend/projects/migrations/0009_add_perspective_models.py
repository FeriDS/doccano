from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0008_project_allow_member_to_create_label_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerspectiveField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('field_type', models.CharField(choices=[('Text', 'Text'), ('Number', 'Number'), ('Choice', 'Choice'), ('MultipleChoice', 'Multiple Choice'), ('Date', 'Date')], default='Text', max_length=20)),
                ('options', models.JSONField(blank=True, help_text='Options for choice fields in JSON format', null=True)),
                ('required', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectPerspective',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_required', models.BooleanField(default=True, help_text='Whether annotators must fill perspective before annotating')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fields', models.ManyToManyField(related_name='projects', to='projects.PerspectiveField')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perspective', to='projects.project')),
            ],
        ),
        migrations.CreateModel(
            name='UserPerspectiveAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='projects.perspectivefield')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_perspectives', to='projects.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='perspective_answers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'project', 'field')},
            },
        ),
    ] 