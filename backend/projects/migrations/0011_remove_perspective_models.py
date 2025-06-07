from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_project_allow_member_to_create_label_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userperspectiveanswer',
            name='field',
        ),
        migrations.RemoveField(
            model_name='userperspectiveanswer',
            name='project',
        ),
        migrations.RemoveField(
            model_name='userperspectiveanswer',
            name='user',
        ),
        migrations.RemoveField(
            model_name='projectperspective',
            name='fields',
        ),
        migrations.RemoveField(
            model_name='projectperspective',
            name='project',
        ),
        migrations.DeleteModel(
            name='PerspectiveField',
        ),
        migrations.DeleteModel(
            name='ProjectPerspective',
        ),
        migrations.DeleteModel(
            name='UserPerspectiveAnswer',
        ),
    ] 