# Generated by Django 2.1.2 on 2018-10-11 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Keywords_Count',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Keywords_Search',
            fields=[
                ('keyword', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('search', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Urls',
            fields=[
                ('url', models.CharField(max_length=2083, primary_key=True, serialize=False)),
                ('title', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='keywords_count',
            name='keyword',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='search1.Keywords_Search'),
        ),
        migrations.AddField(
            model_name='keywords_count',
            name='url',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='search1.Urls'),
        ),
    ]