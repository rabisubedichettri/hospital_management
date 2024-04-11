# Generated by Django 5.0.4 on 2024-04-11 06:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patient', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('symptoms', models.TextField(max_length=2000)),
                ('gender', models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('other', 'Other')], max_length=10)),
                ('discharge', models.BooleanField(default=False)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
            ],
        ),
        migrations.CreateModel(
            name='AdmissionBill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bill_num', models.CharField(max_length=100)),
                ('bill_title', models.CharField(max_length=100)),
                ('bill_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paid', models.BooleanField(default=False)),
                ('paid_time', models.DateTimeField(blank=True, null=True)),
                ('admission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admission.admission')),
            ],
        ),
    ]