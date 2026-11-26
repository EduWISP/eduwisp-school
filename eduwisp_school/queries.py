# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
"""Interrogazioni riutilizzabili dagli altri moduli (per esempio eduwisp-devices)."""

from django.db.models import Q

from .models import SchoolClass, TeachingAssignment


def classes_for_teacher(user, school_year=None):
    """Classi in cui il docente insegna (RF-010).

    Un incarico su una sezione intera vale per tutte le classi della sezione in quell'anno.
    Senza anno indicato si usano gli anni scolastici in corso delle sue organizzazioni.
    """
    assignments = TeachingAssignment.objects.filter(teacher=user)
    if school_year is not None:
        assignments = assignments.filter(school_year=school_year)
    else:
        assignments = assignments.filter(school_year__is_current=True)
    condition = Q(pk__in=[])
    for a in assignments:
        if a.school_class_id:
            condition |= Q(pk=a.school_class_id)
        else:
            condition |= Q(section_id=a.section_id, school_year_id=a.school_year_id)
    return SchoolClass.objects.filter(condition).distinct()
