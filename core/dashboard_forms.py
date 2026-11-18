from django import forms
from .models import Achievement, Education, Experience, Profile, Project, Resume, Skill


class DashboardModelForm(forms.ModelForm):
    """Shared widgets for the custom content dashboard."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'dashboard-input'
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 5
            if isinstance(field.widget, forms.DateInput):
                field.widget.input_type = 'date'


class ProfileDashboardForm(DashboardModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {'bio': forms.Textarea(attrs={'rows': 7})}


class SkillDashboardForm(DashboardModelForm):
    class Meta:
        model = Skill
        fields = '__all__'


class ExperienceDashboardForm(DashboardModelForm):
    class Meta:
        model = Experience
        fields = '__all__'
        widgets = {'description': forms.Textarea(attrs={'rows': 7})}


class EducationDashboardForm(DashboardModelForm):
    class Meta:
        model = Education
        fields = '__all__'


class AchievementDashboardForm(DashboardModelForm):
    class Meta:
        model = Achievement
        fields = ['category', 'title', 'issuer', 'date', 'description', 'image', 'order']


class ProjectDashboardForm(DashboardModelForm):
    class Meta:
        model = Project
        fields = ['title', 'slug', 'tagline', 'description', 'thumbnail', 'tech_stack', 'live_url', 'github_url', 'is_featured', 'order']


class ResumeDashboardForm(DashboardModelForm):
    class Meta:
        model = Resume
        fields = '__all__'
