# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from eduwisp_school.models import (
    Guardian,
    GuardianKind,
    SchoolClass,
    SchoolLevel,
    Section,
    Site,
    Student,
    StudentEnrollment,
    TeachingAssignment,
)
from eduwisp_school.queries import classes_for_teacher, students_for_guardian

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


def familiare(scuola, persona, studente, **campi):
    g = Guardian(organization=scuola, user=persona, student=studente, **campi)
    g.full_clean()
    g.save()
    return g


def studente_iscritto(scuola, classe_, nome):
    s = Student.objects.create(organization=scuola, display_name=nome)
    StudentEnrollment.objects.create(organization=scuola, student=s, school_class=classe_)
    return s


def test_famiglia_vede_solo_i_propri_figli(scuola, anno, sezione):
    a1 = classe(scuola, anno, sezione("A"), 1)
    figlio, fratello, altro = (studente_iscritto(scuola, a1, n) for n in ("Uno", "Due", "Tre"))
    madre = get_user_model().objects.create_user("madre")
    familiare(scuola, madre, figlio, is_primary=True)
    familiare(scuola, madre, fratello, is_primary=True)
    assert set(students_for_guardian(madre)) == {figlio, fratello}
    assert altro not in students_for_guardian(madre)


def test_un_referente_e_un_secondo_facoltativo(scuola, anno, sezione):
    a1 = classe(scuola, anno, sezione("A"), 1)
    figlio = studente_iscritto(scuola, a1, "Figlio")
    utenti = get_user_model().objects
    madre, padre, terzo = (utenti.create_user(n) for n in ("madre", "padre", "terzo"))
    familiare(scuola, madre, figlio, is_primary=True)
    assert list(students_for_guardian(madre)) == [figlio]
    familiare(scuola, padre, figlio)
    assert list(students_for_guardian(padre)) == [figlio]
    with pytest.raises(ValidationError):
        familiare(scuola, terzo, figlio, kind=GuardianKind.AFFIDATARIO)
    with pytest.raises(ValidationError):
        Guardian(organization=scuola, user=padre, student=figlio, is_primary=True).full_clean()


def test_collegamento_disattivato_non_da_accesso(scuola, anno, sezione):
    a1 = classe(scuola, anno, sezione("A"), 1)
    figlio = studente_iscritto(scuola, a1, "Figlio")
    utenti = get_user_model().objects
    madre, padre, tutore = (utenti.create_user(n) for n in ("madre", "padre", "tutore"))
    familiare(scuola, madre, figlio, is_primary=True)
    g = familiare(scuola, padre, figlio)
    g.is_active = False
    g.full_clean()
    g.save()
    assert list(students_for_guardian(padre)) == []
    familiare(scuola, tutore, figlio, kind=GuardianKind.TUTORE)
    assert list(students_for_guardian(tutore)) == [figlio]


def test_accesso_solo_con_iscrizione_nell_anno_in_corso(scuola, anno, sezione):
    a1 = classe(scuola, anno, sezione("A"), 1)
    figlio = studente_iscritto(scuola, a1, "Figlio")
    madre = get_user_model().objects.create_user("madre")
    familiare(scuola, madre, figlio, is_primary=True)
    anno.is_current = False
    anno.save()
    assert list(students_for_guardian(madre)) == []


def test_familiare_dello_stesso_istituto(scuola, altra_scuola, anno, sezione):
    figlio = Student.objects.create(organization=scuola, display_name="Figlio")
    madre = get_user_model().objects.create_user("madre")
    g = Guardian(organization=altra_scuola, user=madre, student=figlio, is_primary=True)
    with pytest.raises(ValidationError):
        g.full_clean()


def test_familiari_perdono_l_accesso_con_la_maggiore_eta(scuola, anno, sezione):
    from datetime import date

    from eduwisp_school.queries import linked_students

    a3 = classe(scuola, anno, sezione("A"), 3)
    figlio = studente_iscritto(scuola, a3, "Figlio")
    madre = get_user_model().objects.create_user("madre")
    familiare(scuola, madre, figlio, is_primary=True)
    figlio.adult_on = date(2027, 3, 1)
    figlio.save()
    assert list(students_for_guardian(madre, today=date(2027, 2, 28))) == [figlio]
    # Dalla maggiore età: accesso chiuso finché lo studente non sceglie
    assert list(students_for_guardian(madre, today=date(2027, 3, 1))) == []
    assert list(linked_students(madre)) == [figlio]
    figlio.family_access_granted = True
    figlio.save()
    assert list(students_for_guardian(madre, today=date(2027, 3, 1))) == [figlio]
    figlio.family_access_granted = False
    figlio.save()
    assert list(students_for_guardian(madre, today=date(2027, 3, 1))) == []
    assert not figlio.family_access_open(today=date(2027, 3, 1))
    assert figlio.family_access_open(today=date(2027, 2, 1))


def test_la_scuola_non_cambia_la_scelta_dello_studente():
    from django.contrib import admin

    from eduwisp_school.models import Student as S

    ro = admin.site._registry[S].readonly_fields
    assert "family_access_granted" in ro and "family_access_decided_at" in ro
