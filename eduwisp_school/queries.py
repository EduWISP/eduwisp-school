# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
"""Interrogazioni riutilizzabili dagli altri moduli (per esempio eduwisp-devices)."""

from django.db.models import Q
from django.utils import timezone

from .models import ADULT_AGE, SchoolClass, Student, TeachingAssignment, born_by


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


def linked_students(user):
    """Studenti a cui la persona è collegata, iscritti nell'anno in corso (ADR-0018).

    Comprende i maggiorenni che non hanno consentito l'accesso: serve solo per dire ai
    familiari che lo studente è maggiorenne, mai per mostrarne i dati.
    """
    return Student.objects.filter(
        guardians__user=user,
        guardians__is_active=True,
        enrollments__school_class__school_year__is_current=True,
    ).distinct()


def adult_without_consent(today=None):
    today = today or timezone.localdate()
    return Q(birth_date__lte=born_by(today, ADULT_AGE)) & ~Q(family_access_granted=True)


def students_for_guardian(user, today=None):
    """Figli di cui la persona può vedere i dati (ADR-0018).

    Solo collegamenti attivi e studenti iscritti nell'anno in corso: quando lo studente
    lascia l'istituto l'accesso termina. Dalla maggiore età l'accesso è chiuso, salvo
    consenso dello studente dal proprio tablet.
    """
    return linked_students(user).exclude(adult_without_consent(today))
