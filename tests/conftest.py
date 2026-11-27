# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
from datetime import date

import pytest
from eduwisp_users.models import Organization

from eduwisp_school.models import SchoolLevel, SchoolYear, Section, Site


@pytest.fixture
def scuola(db):
    return Organization.objects.create(name="Istituto Comprensivo Fittizio", slug="ic-fittizio")


@pytest.fixture
def altra_scuola(db):
    return Organization.objects.create(name="Liceo Fittizio", slug="liceo-fittizio")


@pytest.fixture
def anno(scuola):
    return SchoolYear.objects.create(
        organization=scuola,
        label="2026/2027",
        start_date=date(2026, 9, 1),
        end_date=date(2027, 8, 31),
        is_current=True,
    )


@pytest.fixture
def media(scuola):
    return Site.objects.create(
        organization=scuola, name="Plesso Centro", level=SchoolLevel.SECONDARIA_1
    )


@pytest.fixture
def sezione(scuola, media):
    def _sezione(nome):
        return Section.objects.create(organization=scuola, site=media, name=nome)

    return _sezione
