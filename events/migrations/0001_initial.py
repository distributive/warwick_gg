# Generated by Django 2.0.2 on 2018-05-19 11:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('start', models.DateTimeField(default=django.utils.timezone.now)),
                ('end', models.DateTimeField(default=django.utils.timezone.now)),
                ('signup_start', models.DateTimeField(default=django.utils.timezone.now)),
                ('signup_end', models.DateTimeField(default=django.utils.timezone.now)),
                ('signup_start_fresher', models.DateTimeField(blank=True)),
                ('signup_limit', models.IntegerField(default=70)),
                ('event_for', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('UWCS', 'Uni of Warwick Computing Society'), ('WE', 'Warwick Esports')], max_length=7)),
                ('cost_member', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('cost_nonmember', models.DecimalField(decimal_places=2, default=5, max_digits=3)),
                ('has_seating', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventSignup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.TextField(blank=True, max_length=1024)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='SeatingRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('seating_plan_svg', models.FileField(upload_to='seating/')),
                ('tables_raw', models.TextField(help_text='This field will contain a literal array of integers in JSON list notation ([2, 3, 4, 5]). Each position corresponds to a table, and the value is the total seats on that table. For example: [20, 20, 20, 10] would be the standard LIB2 set up.')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='seating_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='events.SeatingRoom'),
        ),
        migrations.AlterUniqueTogether(
            name='eventsignup',
            unique_together={('user', 'event')},
        ),
    ]