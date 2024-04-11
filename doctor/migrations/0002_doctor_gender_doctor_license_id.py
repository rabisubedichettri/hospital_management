# Generated by Django 5.0.4 on 2024-04-11 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=50),
        ),
        migrations.AddField(
            model_name='doctor',
            name='license_id',
            field=models.CharField(default='Male', max_length=34),
            preserve_default=False,
        ),
    ]
