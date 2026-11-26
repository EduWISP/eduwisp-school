# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
from django.apps import AppConfig


class EduwispSchoolConfig(AppConfig):
    name = "eduwisp_school"
    verbose_name = "EduWISP — gestione scolastica"
    default_auto_field = "django.db.models.BigAutoField"
