from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Profile,
    Skill,
    Experience,
    Education,
    Certification,
    Service,
    PortfolioItem,
    ContactMessage,
)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identity', {
            'fields': ('name', 'role', 'tagline_items', 'avatar', 'hero_bg', 'cv_file'),
        }),
        ('Bio', {
            'fields': ('bio_short', 'bio_long'),
        }),
        ('Stats', {
            'fields': ('projects_count', 'years_experience', 'awards_count', 'rating'),
        }),
        ('Detail Grid', {
            'fields': ('degree', 'location', 'email', 'phone', 'availability'),
        }),
        ('Social Links', {
            'fields': ('twitter_url', 'facebook_url', 'instagram_url', 'linkedin_url', 'github_url'),
            'classes': ('collapse',),
        }),
        ('Footer / Contact Block', {
            'fields': ('address', 'contact_email', 'contact_phone'),
            'classes': ('collapse',),
        }),
    )

    list_display  = ('name', 'role', 'email', 'availability', 'avatar_preview')
    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:50%;" />',
                obj.avatar.url,
            )
        return '—'
    avatar_preview.short_description = 'Avatar'


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display  = ('name', 'percentage', 'order', 'progress_bar')
    list_editable = ('percentage', 'order')
    ordering      = ('order', '-percentage')

    def progress_bar(self, obj):
        color = '#4e73df' if obj.percentage >= 80 else '#f6c23e' if obj.percentage >= 50 else '#e74a3b'
        return format_html(
            '<div style="width:150px;background:#eee;border-radius:4px;">'
            '<div style="width:{pct}%;background:{color};height:10px;border-radius:4px;"></div>'
            '</div> {pct}%',
            pct=obj.percentage,
            color=color,
        )
    progress_bar.short_description = 'Level'


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display  = ('job_title', 'company', 'duration_label', 'is_current', 'is_featured')
    list_filter   = ('is_current', 'is_featured')
    list_editable = ('is_current', 'is_featured')
    search_fields = ('job_title', 'company')
    ordering      = ('-is_current', '-start_year')

    fieldsets = (
        (None, {
            'fields': (
                'job_title', 'company',
                'start_year', 'end_year',
                'is_current', 'is_featured',
            ),
        }),
        ('Details', {
            'fields': ('description', 'skill_tags', 'icon_class'),
        }),
    )

    def duration_label(self, obj):
        return obj.duration_label
    duration_label.short_description = 'Period'


# ---------------------------------------------------------------------------
# Education + Certification (inline on Education list)
# ---------------------------------------------------------------------------

class CertificationInline(admin.TabularInline):
    model  = Certification
    extra  = 1
    fields = ('name', 'year', 'issuer')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display  = ('degree_name', 'institution', 'degree_level', 'year_range', 'achievement')
    list_filter   = ('degree_level',)
    search_fields = ('degree_name', 'institution')
    ordering      = ('-start_year',)

    fieldsets = (
        (None, {
            'fields': ('degree_level', 'degree_name', 'institution', 'start_year', 'end_year'),
        }),
        ('Details', {
            'fields': ('description', 'achievement', 'icon_class'),
        }),
    )

    def year_range(self, obj):
        return obj.year_range
    year_range.short_description = 'Period'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display  = ('name', 'year', 'issuer')
    list_editable = ('year', 'issuer')
    ordering      = ('-year',)
    search_fields = ('name', 'issuer')


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ('title', 'slug', 'icon_preview', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')
    list_filter   = ('is_featured',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    ordering      = ('order',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'icon_class', 'is_featured', 'order'),
        }),
        ('Content', {
            'fields': ('description', 'detail_body'),
        }),
    )

    def icon_preview(self, obj):
        return format_html('<i class="{}" style="font-size:1.2rem;"></i>', obj.icon_class)
    icon_preview.short_description = 'Icon'


# ---------------------------------------------------------------------------
# Portfolio Item
# ---------------------------------------------------------------------------

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'year', 'tags', 'thumbnail_preview')
    list_filter   = ('category', 'year')
    search_fields = ('title', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    ordering      = ('-year', 'title')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'category_label', 'year'),
        }),
        ('Media', {
            'fields': ('image', 'thumbnail_preview'),
        }),
        ('Content', {
            'fields': ('description', 'detail_body', 'tags', 'external_url'),
        }),
    )

    readonly_fields = ('thumbnail_preview',)

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:80px;width:120px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return '—'
    thumbnail_preview.short_description = 'Preview'


# ---------------------------------------------------------------------------
# Contact Message
# ---------------------------------------------------------------------------

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('subject', 'name', 'email', 'sent_at', 'is_read', 'read_badge')
    list_filter   = ('is_read',)
    list_editable = ('is_read',)
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('name', 'email', 'subject', 'message', 'sent_at')
    ordering      = ('-sent_at',)

    # Prevent accidental edits to submitted messages
    def has_add_permission(self, request):
        return False

    def read_badge(self, obj):
        if obj.is_read:
            return format_html('<span style="color:#28a745;font-weight:600;">✓ Read</span>')
        return format_html('<span style="color:#dc3545;font-weight:600;">● New</span>')
    read_badge.short_description = 'Status'

    def get_fields(self, request, obj=None):
        return ('name', 'email', 'subject', 'message', 'sent_at', 'is_read')