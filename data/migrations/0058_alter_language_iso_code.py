from django.db import migrations, models


def populate_languages(apps, schema_editor):
    Language = apps.get_model("data", "Language")
    languages = [
        ("ar", "Arabic"),
        ("hy", "Armenian"),
        ("be", "Belarusian"),
        ("ce", "Chechen"),
        ("zh", "Chinese"),
        ("cs", "Czech"),
        ("prs", "Dari"),
        ("nl", "Dutch"),
        ("en", "English"),
        ("fr", "French"),
        ("ka", "Georgian"),
        ("de", "German"),
        ("el", "Greek"),
        ("he", "Hebrew"),
        ("hi", "Hindi"),
        ("it", "Italian"),
        ("ku", "Kurdish"),
        ("ps", "Pashto"),
        ("fa", "Persian"),
        ("pl", "Polish"),
        ("pa", "Punjabi"),
        ("rom", "Romany"),
        ("ru", "Russian"),
        ("sr", "Serbian"),
        ("so", "Somali"),
        ("es", "Spanish"),
        ("sv", "Swedish"),
        ("tr", "Turkish"),
        ("uk", "Ukrainian"),
        ("ur", "Urdu"),
        ("vi", "Vietnamese"),
    ]

    for iso_code, title in languages:
        Language.objects.get_or_create(iso_code=iso_code, defaults={"title": title})


class Migration(migrations.Migration):
    dependencies = [
        ("data", "0057_remove_volunteerlanguagem2m_language_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="language",
            name="title",
            field=models.CharField(max_length=25, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="language",
            name="iso_code",
            field=models.CharField(
                choices=[
                    ("ar", "Arabic"),
                    ("hy", "Armenian"),
                    ("be", "Belarusian"),
                    ("ce", "Chechen"),
                    ("zh", "Chinese"),
                    ("cs", "Czech"),
                    ("prs", "Dari"),
                    ("nl", "Dutch"),
                    ("en", "English"),
                    ("fa", "Persian"),
                    ("fr", "French"),
                    ("ka", "Georgian"),
                    ("de", "German"),
                    ("el", "Greek"),
                    ("he", "Hebrew"),
                    ("hi", "Hindi"),
                    ("it", "Italian"),
                    ("ku", "Kurdish"),
                    ("ps", "Pashto"),
                    ("pl", "Polish"),
                    ("pa", "Punjabi"),
                    ("rom", "Romany"),
                    ("ru", "Russian"),
                    ("sr", "Serbian"),
                    ("so", "Somali"),
                    ("es", "Spanish"),
                    ("sv", "Swedish"),
                    ("tr", "Turkish"),
                    ("uk", "Ukrainian"),
                    ("ur", "Urdu"),
                    ("vi", "Vietnamese"),
                ],
                max_length=3,
                unique=True,
            ),
        ),
        migrations.RunPython(populate_languages),
    ]
