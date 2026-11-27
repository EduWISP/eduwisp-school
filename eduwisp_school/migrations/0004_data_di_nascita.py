# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("eduwisp_school", "0003_maggiorenni")]

    operations = [
        migrations.AddField(
            model_name="student",
            name="birth_date",
            field=models.DateField(
                blank=True,
                help_text="serve per l'età di ognuno (anche chi ripete l'anno): maggiore età e "
                "14 anni del consenso digitale (ADR-0018)",
                null=True,
                verbose_name="data di nascita",
            ),
        ),
    ]
