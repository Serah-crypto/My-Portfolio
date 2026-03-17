from django.db import models
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Profile  (single-owner portfolio — one row expected)
# ---------------------------------------------------------------------------

class Profile(models.Model):
    name            = models.CharField(max_length=100)
    role            = models.CharField(max_length=100, help_text="e.g. Full Stack Developer")
    tagline_items   = models.CharField(
        max_length=255,
        help_text="Comma-separated typed items, e.g. Designer,Developer,Freelancer",
    )
    bio_short       = models.TextField(help_text="First paragraph of the About bio")
    bio_long        = models.TextField(blank=True, help_text="Second paragraph (optional)")
    avatar          = models.ImageField(upload_to='profile/', blank=True)
    hero_bg         = models.ImageField(upload_to='profile/', blank=True)
    cv_file         = models.FileField(upload_to='cv/', blank=True, null=True)

    # Stats shown on the profile card
    projects_count  = models.PositiveIntegerField(default=0)
    years_experience = models.PositiveIntegerField(default=0)
    awards_count    = models.PositiveIntegerField(default=0)
    rating          = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    # Detail grid
    degree          = models.CharField(max_length=100, blank=True, help_text="e.g. Master of Science")
    location        = models.CharField(max_length=100, blank=True, help_text="e.g. Portland, OR")
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=30, blank=True)
    availability    = models.CharField(max_length=80, default='Open to Work')

    # Social links
    twitter_url     = models.URLField(blank=True)
    facebook_url    = models.URLField(blank=True)
    instagram_url   = models.URLField(blank=True)
    linkedin_url    = models.URLField(blank=True)
    github_url      = models.URLField(blank=True)

    # Footer / contact block (may differ from profile card)
    address         = models.CharField(max_length=200, blank=True)
    contact_email   = models.EmailField(blank=True)
    contact_phone   = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = 'Profile'

    def __str__(self):
        return self.name

    @property
    def typed_items_list(self):
        """Return tagline_items as a Python list for the Typed.js data attribute."""
        return [item.strip() for item in self.tagline_items.split(',') if item.strip()]


# ---------------------------------------------------------------------------
# Skill  (progress-bar skills in the About section)
# ---------------------------------------------------------------------------

class Skill(models.Model):
    name        = models.CharField(max_length=100, help_text="e.g. React & Next.js")
    percentage  = models.PositiveSmallIntegerField(help_text="0–100")
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', '-percentage']
        verbose_name = 'Skill'

    def __str__(self):
        return f'{self.name} ({self.percentage}%)'


# ---------------------------------------------------------------------------
# Experience  (Resume – left column)
# ---------------------------------------------------------------------------

class Experience(models.Model):
    job_title   = models.CharField(max_length=150)
    company     = models.CharField(max_length=150)
    start_year  = models.PositiveSmallIntegerField()
    end_year    = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Leave blank if this is the current role",
    )
    is_current  = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    # Skill tags shown on the featured card (comma-separated)
    skill_tags  = models.CharField(
        max_length=255, blank=True,
        help_text="Comma-separated tags, e.g. Leadership,Strategy,Innovation",
    )

    # Bootstrap icon class for the company logo placeholder
    icon_class  = models.CharField(
        max_length=60, default='bi bi-buildings',
        help_text="Bootstrap icon class, e.g. bi bi-laptop",
    )
    is_featured = models.BooleanField(default=False, help_text="Show as the highlighted 'Current' card")

    class Meta:
        ordering = ['-is_current', '-start_year']
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'

    def __str__(self):
        end = 'Present' if self.is_current else str(self.end_year)
        return f'{self.job_title} @ {self.company} ({self.start_year}–{end})'

    @property
    def duration_label(self):
        end = 'Present' if self.is_current else str(self.end_year)
        return f'{self.start_year} - {end}'

    @property
    def skill_tags_list(self):
        return [t.strip() for t in self.skill_tags.split(',') if t.strip()]


# ---------------------------------------------------------------------------
# Education  (Resume – right column, timeline)
# ---------------------------------------------------------------------------

class Education(models.Model):
    DEGREE_LEVEL_CHOICES = [
        ('Masters',      'Masters'),
        ('Bachelor',     'Bachelor'),
        ('Diploma',      'Diploma'),
        ('Certificate',  'Certificate'),
        ('Other',        'Other'),
    ]

    degree_level    = models.CharField(max_length=20, choices=DEGREE_LEVEL_CHOICES)
    degree_name     = models.CharField(max_length=200, help_text="e.g. Master of Design Innovation")
    institution     = models.CharField(max_length=200)
    start_year      = models.PositiveSmallIntegerField()
    end_year        = models.PositiveSmallIntegerField()
    description     = models.TextField(blank=True)
    achievement     = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. Summa Cum Laude",
    )

    # Bootstrap icon class for the timeline marker
    icon_class      = models.CharField(max_length=60, default='bi bi-mortarboard-fill')

    class Meta:
        ordering = ['-start_year']
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'

    def __str__(self):
        return f'{self.degree_name} – {self.institution}'

    @property
    def year_range(self):
        return f'{self.start_year} - {self.end_year}'


# ---------------------------------------------------------------------------
# Certification  (shown under the Education timeline)
# ---------------------------------------------------------------------------

class Certification(models.Model):
    name    = models.CharField(max_length=200)
    year    = models.PositiveSmallIntegerField()
    issuer  = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-year']
        verbose_name = 'Certification'

    def __str__(self):
        return f'{self.name} ({self.year})'


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class Service(models.Model):
    title       = models.CharField(max_length=150)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    icon_class  = models.CharField(
        max_length=60, default='bi bi-code-slash',
        help_text="Bootstrap icon class, e.g. bi bi-palette",
    )
    is_featured = models.BooleanField(default=False, help_text="Render with the 'Featured' badge")
    order       = models.PositiveSmallIntegerField(default=0)

    # Extended content for the detail page
    detail_body = models.TextField(
        blank=True,
        help_text="Full description shown on the service-details page",
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'Service'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Portfolio Item
# ---------------------------------------------------------------------------

class PortfolioItem(models.Model):
    CATEGORY_CHOICES = [
        ('creative',    'Creative'),
        ('digital',     'Digital'),
        ('strategy',    'Strategy'),
        ('development', 'Development'),
    ]

    title       = models.CharField(max_length=200)
    slug        = models.SlugField(unique=True, blank=True)
    category    = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    category_label = models.CharField(
        max_length=100, blank=True,
        help_text="Display label shown in the overlay, e.g. 'Creative Design'",
    )
    image       = models.ImageField(upload_to='portfolio/')
    year        = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True, help_text="Short teaser shown on the card")
    detail_body = models.TextField(blank=True, help_text="Full description on the detail page")

    # Comma-separated tags shown below the card, e.g. "Branding,Identity"
    tags        = models.CharField(max_length=255, blank=True)

    # External link (optional)
    external_url = models.URLField(blank=True)

    class Meta:
        ordering = ['-year', 'title']
        verbose_name = 'Portfolio Item'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def filter_class(self):
        """Returns the CSS class used by Isotope, e.g. 'filter-creative'."""
        return f'filter-{self.category}'

    @property
    def tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


# ---------------------------------------------------------------------------
# Contact Message  (saved submissions from the contact form)
# ---------------------------------------------------------------------------

class ContactMessage(models.Model):
    name        = models.CharField(max_length=100)
    email       = models.EmailField()
    subject     = models.CharField(max_length=255)
    message     = models.TextField()
    sent_at     = models.DateTimeField(auto_now_add=True)
    is_read     = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Contact Message'

    def __str__(self):
        return f'{self.subject} — {self.name} ({self.sent_at:%Y-%m-%d})'