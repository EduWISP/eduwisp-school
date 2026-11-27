# SPDX-License-Identifier: AGPL-3.0-or-later
"""Ricava la data di nascita da quella della maggiore età già salvata (stesso dato)."""

from django.db import migrations


def avanti(apps, schema_editor):
    Student = apps.get_model("eduwisp_school", "Student")
    for s in Student.objects.filter(adult_on__isnull=False).only("pk", "adult_on"):
        d = s.adult_on
        try:
            nascita = d.replace(year=d.year - 18)
        except ValueError:  # 29 febbraio
            nascita = d.replace(year=d.year - 18, day=28)
        Student.objects.filter(pk=s.pk).update(birth_date=nascita)


def indietro(apps, schema_editor):
    Student = apps.get_model("eduwisp_school", "Student")
    for s in Student.objects.filter(birth_date__isnull=False).only("pk", "birth_date"):
        d = s.birth_date
        try:
            maggiore = d.replace(year=d.year + 18)
        except ValueError:
            maggiore = d.replace(year=d.year + 18, month=3, day=1)
        Student.objects.filter(pk=s.pk).update(adult_on=maggiore)


class Migration(migrations.Migration):
    dependencies = [("eduwisp_school", "0004_data_di_nascita")]

    operations = [migrations.RunPython(avanti, indietro)]
