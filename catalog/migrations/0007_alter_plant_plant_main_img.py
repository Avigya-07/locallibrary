# Generated by Django 4.0.2 on 2022-02-25 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_alter_plant_plant_main_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='plant_main_img',
            field=models.ImageField(upload_to='media/media/images/'),
        ),
    ]
