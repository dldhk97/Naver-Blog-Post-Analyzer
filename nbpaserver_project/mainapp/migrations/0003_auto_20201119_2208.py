# Generated by Django 3.1.3 on 2020-11-19 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_auto_20201119_2201'),
    ]

    operations = [
        migrations.RenameField(
            model_name='analyzedinfo',
            old_name='sample1',
            new_name='sample_1',
        ),
        migrations.RenameField(
            model_name='analyzedinfo',
            old_name='sample2',
            new_name='sample_2',
        ),
        migrations.RenameField(
            model_name='analyzedinfo',
            old_name='sample3',
            new_name='sample_3',
        ),
    ]