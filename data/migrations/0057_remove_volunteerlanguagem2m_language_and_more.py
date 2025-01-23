from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0056_remove_opportunity_accomp_information_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="volunteerlanguagem2m",
            name="language",
        ),
        migrations.RemoveField(
            model_name="volunteerlanguagem2m",
            name="volunteerform",
        ),
        migrations.RemoveField(
            model_name="language",
            name="title",
        ),
        migrations.AlterField(
            model_name="language",
            name="iso_code",
            field=models.CharField(
                choices=[
                    ("EN", "English"),
                    ("ES", "Spanish"),
                    ("FR", "French"),
                    ("DE", "German"),
                    ("IT", "Italian"),
                ],
                max_length=2,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="opportunity",
            name="accomp_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name="opportunity",
            name="languages",
        ),
        migrations.AlterField(
            model_name="opportunity",
            name="last_edited_time_notion",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="opportunity",
            name="rac_address",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="opportunity",
            name="rac_email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name="opportunity",
            name="rac_full_name",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name="opportunity",
            name="rac_phone",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name="opportunity",
            name="rac_plz",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name="volunteerform",
            name="languages",
        ),
        migrations.DeleteModel(
            name="OpportunityLanguageM2M",
        ),
        migrations.DeleteModel(
            name="VolunteerLanguageM2M",
        ),
        migrations.AddField(
            model_name="opportunity",
            name="languages",
            field=models.ManyToManyField(to="data.language"),
        ),
        migrations.AddField(
            model_name="volunteerform",
            name="languages",
            field=models.ManyToManyField(to="data.language"),
        ),
    ]
