# Generated by Django 4.0.2 on 2022-03-04 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_alter_plant_plant_main_img'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['title', 'author']},
        ),
    ]
