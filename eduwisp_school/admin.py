# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Michele Salerno e i contributori di EduWISP
from django.contrib import admin
from eduwisp_users.models import Role
from eduwisp_users.tenancy import OrganizationScopedAdminMixin

from . import models

MANAGERS = [Role.SCHOOL_ADMIN, Role.IT_ADMIN]


class ScopedAdmin(OrganizationScopedAdminMixin, admin.ModelAdmin):
    organization_roles = MANAGERS


class TeachingAssignmentInline(OrganizationScopedAdminMixin, admin.TabularInline):
    model = models.TeachingAssignment
    organization_roles = MANAGERS
    fk_name = "section"
    extra = 0
    fields = ["organization", "teacher", "school_year", "school_class", "subject", "kind"]


@admin.register(models.Site)
class SiteAdmin(ScopedAdmin):
    list_display = ["name", "level", "code", "organization"]
    list_filter = ["level"]


@admin.register(models.Track)
class TrackAdmin(ScopedAdmin):
    list_display = ["name", "site", "organization"]


@admin.register(models.Section)
class SectionAdmin(ScopedAdmin):
    list_display = ["name", "site", "track", "organization"]
    list_filter = ["site"]
    inlines = [TeachingAssignmentInline]


@admin.register(models.SchoolYear)
class SchoolYearAdmin(ScopedAdmin):
    list_display = ["label", "start_date", "end_date", "is_current", "organization"]


class StudentEnrollmentInline(OrganizationScopedAdminMixin, admin.TabularInline):
    model = models.StudentEnrollment
    organization_roles = MANAGERS
    extra = 0


@admin.register(models.SchoolClass)
class SchoolClassAdmin(ScopedAdmin):
    list_display = ["__str__", "section", "school_year", "organization"]
    list_filter = ["school_year", "section__site"]
    inlines = [StudentEnrollmentInline]


@admin.register(models.Student)
class StudentAdmin(ScopedAdmin):
    list_display = ["display_name", "internal_code", "organization"]
    search_fields = ["display_name", "internal_code"]
    inlines = [StudentEnrollmentInline]


@admin.register(models.TeachingAssignment)
class TeachingAssignmentAdmin(ScopedAdmin):
    list_display = ["teacher", "section", "school_class", "subject", "kind", "school_year"]
    list_filter = ["school_year", "kind"]
