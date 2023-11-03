# Generated by Django 4.2.6 on 2023-11-01 16:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserLecture",
            fields=[
                (
                    "subject_num",
                    models.CharField(max_length=10, primary_key=True, serialize=False),
                ),
                ("subject_name", models.CharField(max_length=70)),
                ("classification", models.CharField(max_length=45)),
                ("classification_ge", models.CharField(max_length=45)),
                ("professor", models.CharField(max_length=50)),
                ("subject_credit", models.IntegerField()),
            ],
            options={
                "db_table": "lecture",
                "managed": False,
            },
        ),
        migrations.AlterModelOptions(
            name="lecture",
            options={"managed": False},
        ),
        migrations.AlterModelOptions(
            name="relation",
            options={"managed": False},
        ),
        migrations.AlterModelOptions(
            name="review",
            options={"managed": False},
        ),
        migrations.AlterModelOptions(
            name="standard",
            options={"managed": False},
        ),
        migrations.AlterModelOptions(
            name="userinfo",
            options={"managed": False},
        ),
    ]
