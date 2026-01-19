


from django.db import migrations, models
import datetime

class Migration(migrations.Migration):

    dependencies = [
        ('mck_master', '0002_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created_by',
            field=models.CharField(max_length=8, null=True, blank=True),  # allow NULL for existing rows
        ),
        migrations.AddField(
            model_name='profile',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True),  # allow NULL
        ),
        migrations.AddField(
            model_name='profile',
            name='datamode',
            field=models.CharField(
                max_length=20,
                choices=[('A', 'Active'), ('I', 'Inactivated'), ('D', 'Deleted')],
                default='A',
            ),
        ),
        migrations.AddField(
            model_name='profile',
            name='updated_by',
            field=models.CharField(max_length=8, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
