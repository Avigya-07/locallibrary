# Generated by Django 4.0.2 on 2022-02-24 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_plant_alter_bookinstance_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plant',
            name='plant_main_img',
            field=models.ImageField(upload_to='media/images/'),
        ),
    ]
