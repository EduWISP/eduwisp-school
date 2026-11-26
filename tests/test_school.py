# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from eduwisp_school.models import (
    SchoolClass,
    SchoolLevel,
    Section,
    Site,
    Student,
    StudentEnrollment,
    TeachingAssignment,
)
from eduwisp_school.queries import classes_for_teacher

pytestmark = pytest.mark.django_db


def classe(scuola, anno, sezione, numero):
    c = SchoolClass(organization=scuola, school_year=anno, section=sezione, year_number=numero)
    c.full_clean()
    c.save()
    return c


def test_media_ha_tre_anni(scuola, anno, sezione):
    a = sezione("A")
    for n in (1, 2, 3):
        classe(scuola, anno, a, n)
    with pytest.raises(ValidationError):
        classe(scuola, anno, a, 4)


def test_superiori_hanno_cinque_anni(scuola, anno):
    liceo = Site.objects.create(organization=scuola, name="Sede", level=SchoolLevel.SECONDARIA_2)
    a = Section.objects.create(organization=scuola, site=liceo, name="A")
    assert str(classe(scuola, anno, a, 5)) == "5ª A (2026/2027)"
    with pytest.raises(ValidationError):
        classe(scuola, anno, a, 6)


def test_infanzia_senza_anni(scuola, anno):
    infanzia = Site.objects.create(organization=scuola, name="Infanzia", level=SchoolLevel.INFANZIA)
    girasoli = Section.objects.create(organization=scuola, site=infanzia, name="Girasoli")
    classe(scuola, anno, girasoli, None)
    with pytest.raises(ValidationError):
        classe(scuola, anno, girasoli, 1)


def test_sezioni_libere_per_istituto(scuola, sezione):
    # Ogni istituto sceglie nomi e numero delle sezioni.
    for nome in ("A", "B", "F", "Sperimentale"):
        sezione(nome)
    assert Section.objects.count() == 4


def test_docente_su_sezione_intera_e_su_singola_classe(scuola, anno, sezione):
    a, b = sezione("A"), sezione("B")
    a1, a2, a3 = (classe(scuola, anno, a, n) for n in (1, 2, 3))
    b1 = classe(scuola, anno, b, 1)
    classe(scuola, anno, b, 2)
    docente = get_user_model().objects.create_user("prof.matematica", password="x")
    # Tutto il corso A, più la sola 1ª B.
    TeachingAssignment.objects.create(
        organization=scuola, teacher=docente, school_year=anno, section=a, subject="Matematica"
    )
    TeachingAssignment.objects.create(
        organization=scuola,
        teacher=docente,
        school_year=anno,
        section=b,
        school_class=b1,
        subject="Matematica",
    )
    assert set(classes_for_teacher(docente)) == {a1, a2, a3, b1}


def test_una_classe_piu_docenti(scuola, anno, sezione):
    a = sezione("A")
    a1 = classe(scuola, anno, a, 1)
    utenti = get_user_model().objects
    for nome in ("prof.italiano", "prof.inglese"):
        TeachingAssignment.objects.create(
            organization=scuola, teacher=utenti.create_user(nome), school_year=anno, section=a
        )
    for nome in ("prof.italiano", "prof.inglese"):
        assert a1 in classes_for_teacher(utenti.get(username=nome))


def test_studente_in_una_sola_classe_per_anno(scuola, anno, sezione):
    a = sezione("A")
    a1, a2 = classe(scuola, anno, a, 1), classe(scuola, anno, a, 2)
    studente = Student.objects.create(organization=scuola, display_name="Studente Fittizio")
    StudentEnrollment.objects.create(organization=scuola, student=studente, school_class=a1)
    doppia = StudentEnrollment(organization=scuola, student=studente, school_class=a2)
    with pytest.raises(ValidationError):
        doppia.full_clean()


def test_niente_collegamenti_tra_istituti_diversi(scuola, altra_scuola, anno, sezione):
    a = sezione("A")
    c = SchoolClass(organization=altra_scuola, school_year=anno, section=a, year_number=1)
    with pytest.raises(ValidationError) as exc:
        c.full_clean()
    assert "section" in exc.value.message_dict


def test_classe_dell_incarico_coerente_con_la_sezione(scuola, anno, sezione):
    a, b = sezione("A"), sezione("B")
    b1 = classe(scuola, anno, b, 1)
    docente = get_user_model().objects.create_user("prof")
    incarico = TeachingAssignment(
        organization=scuola, teacher=docente, school_year=anno, section=a, school_class=b1
    )
    with pytest.raises(ValidationError):
        incarico.full_clean()
