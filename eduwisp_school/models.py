# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
"""Struttura delle scuole italiane: vedi la pagina «Gestione scolastica» della documentazione.

Nessuna durata o sezione è fissata nel codice oltre alla durata legale degli ordini di scuola:
sezioni, indirizzi e plessi li definisce ogni istituto (RF-005, RF-006).
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from eduwisp_users.models import OrganizationOwned


class SchoolLevel(models.TextChoices):
    INFANZIA = "infanzia", "scuola dell'infanzia"
    PRIMARIA = "primaria", "scuola primaria"
    SECONDARIA_1 = "secondaria_1", "secondaria di primo grado"
    SECONDARIA_2 = "secondaria_2", "secondaria di secondo grado"


#: Numero di anni di ciascun ordine di scuola. L'infanzia è organizzata per sezioni, senza anni.
LEVEL_YEARS = {
    SchoolLevel.INFANZIA: None,
    SchoolLevel.PRIMARIA: 5,
    SchoolLevel.SECONDARIA_1: 3,
    SchoolLevel.SECONDARIA_2: 5,
}


class Site(OrganizationOwned):
    """Plesso o sede, con il proprio ordine di scuola."""

    name = models.CharField("nome", max_length=200)
    level = models.CharField("ordine di scuola", max_length=20, choices=SchoolLevel.choices)
    code = models.CharField("codice meccanografico", max_length=20, blank=True)

    class Meta:
        verbose_name = "plesso"
        verbose_name_plural = "plessi"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    @property
    def years(self) -> int | None:
        return LEVEL_YEARS[self.level]


class Track(OrganizationOwned):
    """Indirizzo di studio (per esempio liceo scientifico), soprattutto nelle superiori."""

    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="plesso")
    name = models.CharField("nome", max_length=200)
    same_organization_fields = ("site",)

    class Meta:
        verbose_name = "indirizzo"
        verbose_name_plural = "indirizzi"
        constraints = [models.UniqueConstraint(fields=["site", "name"], name="indirizzo_unico")]

    def __str__(self):
        return self.name


class Section(OrganizationOwned):
    """Sezione (A, B, …) definita da ciascun istituto per ciascun plesso."""

    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="plesso")
    name = models.CharField("nome", max_length=20)
    track = models.ForeignKey(
        Track, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="indirizzo"
    )
    same_organization_fields = ("site", "track")

    class Meta:
        verbose_name = "sezione"
        verbose_name_plural = "sezioni"
        ordering = ["site", "name"]
        constraints = [models.UniqueConstraint(fields=["site", "name"], name="sezione_unica")]

    def __str__(self):
        return f"Sezione {self.name} — {self.site.name}"

    def clean(self):
        super().clean()
        if self.track_id and self.track.site_id != self.site_id:
            raise ValidationError({"track": "L'indirizzo deve appartenere allo stesso plesso."})


class SchoolYear(OrganizationOwned):
    """Anno scolastico (di norma dal 1° settembre al 31 agosto)."""

    label = models.CharField("anno scolastico", max_length=9, help_text="per esempio 2026/2027")
    start_date = models.DateField("inizio")
    end_date = models.DateField("fine")
    is_current = models.BooleanField("in corso", default=False)

    class Meta:
        verbose_name = "anno scolastico"
        verbose_name_plural = "anni scolastici"
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(fields=["organization", "label"], name="anno_unico"),
            models.UniqueConstraint(
                fields=["organization"],
                condition=models.Q(is_current=True),
                name="un_solo_anno_in_corso",
            ),
        ]

    def __str__(self):
        return self.label

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "La fine deve essere successiva all'inizio."})


class SchoolClass(OrganizationOwned):
    """Classe = anno + sezione, in un anno scolastico (per esempio 2ª B 2026/2027)."""

    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.PROTECT, verbose_name="anno scolastico"
    )
    section = models.ForeignKey(Section, on_delete=models.PROTECT, verbose_name="sezione")
    year_number = models.PositiveSmallIntegerField(
        "anno di corso", null=True, blank=True, help_text="vuoto per la scuola dell'infanzia"
    )
    same_organization_fields = ("school_year", "section")

    class Meta:
        verbose_name = "classe"
        verbose_name_plural = "classi"
        ordering = ["school_year", "section__site", "year_number", "section__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "section", "year_number"], name="classe_unica"
            )
        ]

    def __str__(self):
        if self.year_number is None:
            return f"Sezione {self.section.name} ({self.school_year})"
        return f"{self.year_number}ª {self.section.name} ({self.school_year})"

    def clean(self):
        super().clean()
        if not self.section_id:
            return
        years = self.section.site.years
        if years is None and self.year_number is not None:
            raise ValidationError(
                {"year_number": "L'infanzia è organizzata per sezioni, senza anni."}
            )
        if years is not None and not (self.year_number and 1 <= self.year_number <= years):
            raise ValidationError(
                {"year_number": f"Per questo ordine di scuola l'anno va da 1 a {years}."}
            )


class Student(OrganizationOwned):
    """Studente. Solo i dati necessari alla gestione dei dispositivi (RC-002)."""

    display_name = models.CharField("nome", max_length=150)
    internal_code = models.CharField(
        "codice interno della scuola", max_length=50, blank=True, help_text="facoltativo"
    )
    adult_on = models.DateField(
        "maggiorenne dal",
        null=True,
        blank=True,
        help_text="solo la data della maggiore età, non la data di nascita (ADR-0018)",
    )
    family_access_granted = models.BooleanField(
        "accesso dei familiari consentito dallo studente",
        null=True,
        blank=True,
        help_text="scelta dello studente maggiorenne dal tablet; vuoto = non ancora scelto",
    )
    family_access_decided_at = models.DateTimeField("scelta fatta il", null=True, blank=True)

    class Meta:
        verbose_name = "studente"
        verbose_name_plural = "studenti"
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name

    def is_adult(self, today=None):
        today = today or timezone.localdate()
        return self.adult_on is not None and self.adult_on <= today

    def family_access_open(self, today=None):
        """I familiari vedono i dati se lo studente è minorenne o se l'ha consentito."""
        return not self.is_adult(today) or self.family_access_granted is True


class StudentEnrollment(OrganizationOwned):
    """Iscrizione di uno studente a una classe in un anno scolastico."""

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="enrollments", verbose_name="studente"
    )
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.CASCADE, related_name="enrollments", verbose_name="classe"
    )
    same_organization_fields = ("student", "school_class")

    class Meta:
        verbose_name = "iscrizione"
        verbose_name_plural = "iscrizioni"
        constraints = [
            models.UniqueConstraint(fields=["student", "school_class"], name="iscrizione_unica")
        ]

    def __str__(self):
        return f"{self.student} — {self.school_class}"

    def clean(self):
        super().clean()
        if not (self.student_id and self.school_class_id):
            return
        doppia = StudentEnrollment.objects.filter(
            student=self.student, school_class__school_year=self.school_class.school_year
        ).exclude(pk=self.pk)
        if doppia.exists():
            raise ValidationError("Lo studente è già iscritto a una classe in questo anno.")


class AssignmentKind(models.TextChoices):
    CURRICOLARE = "curricolare", "curricolare"
    COORDINATORE = "coordinatore", "coordinatore di classe"
    SOSTEGNO = "sostegno", "sostegno"


class TeachingAssignment(OrganizationOwned):
    """Incarico di insegnamento (RF-009).

    Si assegna un docente a una **sezione intera** (tutte le sue classi nell'anno) oppure
    a una **singola classe**. Per il sostegno non si registra l'abbinamento al singolo
    studente (RC-013).
    """

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teaching_assignments",
        verbose_name="docente",
    )
    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.PROTECT, verbose_name="anno scolastico"
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name="sezione")
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="classe",
        help_text="vuoto = tutte le classi della sezione",
    )
    subject = models.CharField("disciplina", max_length=100, blank=True)
    kind = models.CharField(
        "tipo", max_length=20, choices=AssignmentKind.choices, default=AssignmentKind.CURRICOLARE
    )
    same_organization_fields = ("school_year", "section", "school_class")

    class Meta:
        verbose_name = "incarico di insegnamento"
        verbose_name_plural = "incarichi di insegnamento"

    def __str__(self):
        target = self.school_class or self.section
        return f"{self.teacher} — {target} {self.subject}".strip()

    def clean(self):
        super().clean()
        if self.school_class_id:
            if self.school_class.section_id != self.section_id:
                raise ValidationError({"school_class": "La classe deve essere della sezione."})
            if self.school_class.school_year_id != self.school_year_id:
                raise ValidationError({"school_class": "La classe deve essere dello stesso anno."})


class GuardianKind(models.TextChoices):
    GENITORE = "genitore", "genitore"
    TUTORE = "tutore", "tutore"
    AFFIDATARIO = "affidatario", "affidatario"


MAX_ACTIVE_GUARDIANS = 2


class Guardian(OrganizationOwned):
    """Collegamento tra una persona con responsabilità e uno studente (ADR-0018).

    Per ogni studente: almeno un collegamento (il referente) e al massimo due attivi,
    con gli stessi diritti di consultazione. «Referente» indica solo chi riceve per primo
    le comunicazioni. Un collegamento disattivato (per esempio per un provvedimento del
    giudice) non dà accesso; il motivo non si registra.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guardianships",
        verbose_name="persona",
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="guardians", verbose_name="studente"
    )
    kind = models.CharField(
        "relazione", max_length=20, choices=GuardianKind.choices, default=GuardianKind.GENITORE
    )
    is_primary = models.BooleanField(
        "referente", default=False, help_text="riceve per primo le comunicazioni"
    )
    is_active = models.BooleanField("accesso attivo", default=True)
    verified_at = models.DateTimeField(
        "relazione verificata il", null=True, blank=True, help_text="RF-020"
    )
    same_organization_fields = ("student",)

    class Meta:
        verbose_name = "familiare"
        verbose_name_plural = "familiari"
        constraints = [
            models.UniqueConstraint(fields=["user", "student"], name="familiare_unico"),
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(is_primary=True),
                name="un_solo_referente",
            ),
        ]

    def __str__(self):
        return f"{self.user} — {self.student} ({self.get_kind_display()})"

    def clean(self):
        super().clean()
        if not self.student_id:
            return
        if self.is_primary and not self.is_active:
            raise ValidationError({"is_active": "Il referente deve avere l'accesso attivo."})
        if self.is_active:
            attivi = Guardian.objects.filter(student=self.student, is_active=True).exclude(
                pk=self.pk
            )
            if attivi.count() >= MAX_ACTIVE_GUARDIANS:
                raise ValidationError(
                    f"Lo studente ha già {MAX_ACTIVE_GUARDIANS} familiari con accesso attivo."
                )
