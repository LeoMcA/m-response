# Generated by Django 2.1.2 on 2018-10-26 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("users", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="languages",
            field=models.CharField(default="", max_length=500),
            preserve_default=False,
        )
    ]
