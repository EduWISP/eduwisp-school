# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("eduwisp_school", "0005_nascita_da_maggiore_eta")]

    operations = [migrations.RemoveField(model_name="student", name="adult_on")]
