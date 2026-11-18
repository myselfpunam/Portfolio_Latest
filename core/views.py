from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.utils.http import url_has_allowed_host_and_scheme
from itertools import groupby
from .models import Profile, Skill, Experience, Education, Achievement, Project, Resume, ContactMessage
from .dashboard_forms import (
    AchievementDashboardForm, EducationDashboardForm, ExperienceDashboardForm,
    ProfileDashboardForm, ProjectDashboardForm, ResumeDashboardForm, SkillDashboardForm,
)


DASHBOARD_SECTIONS = [
    {'key': 'profile', 'label': 'Profile', 'model': Profile, 'form': ProfileDashboardForm, 'columns': [('Name', 'name'), ('Role', 'title'), ('Email', 'email')]},
    {'key': 'skills', 'label': 'Skills', 'model': Skill, 'form': SkillDashboardForm, 'columns': [('Skill', 'name'), ('Category', 'get_category_display'), ('Level', 'proficiency')]},
    {'key': 'experience', 'label': 'Experience', 'model': Experience, 'form': ExperienceDashboardForm, 'columns': [('Role', 'role'), ('Company', 'company'), ('Period', 'duration_label')]},
    {'key': 'education', 'label': 'Education', 'model': Education, 'form': EducationDashboardForm, 'columns': [('Degree', 'degree'), ('Institution', 'institution'), ('Period', 'year_label')]},
    {'key': 'achievements', 'label': 'Achievements & Certifications', 'model': Achievement, 'form': AchievementDashboardForm, 'columns': [('Title', 'title'), ('Type', 'get_category_display'), ('Issuer', 'issuer'), ('Date', 'date')]},
    {'key': 'projects', 'label': 'Projects', 'model': Project, 'form': ProjectDashboardForm, 'columns': [('Project', 'title'), ('Featured', 'is_featured'), ('Slug', 'slug')]},
    {'key': 'resume', 'label': 'Resume / CV', 'model': Resume, 'form': ResumeDashboardForm, 'columns': [('Label', 'label'), ('File', 'file'), ('Updated', 'updated_at')]},
    {'key': 'messages', 'label': 'Messages', 'model': ContactMessage, 'form': None, 'columns': [('From', 'name'), ('Email', 'email'), ('Subject', 'subject'), ('Received', 'sent_at'), ('Read', 'is_read')]},
]


def _dashboard_section(key):
    return next((section for section in DASHBOARD_SECTIONS if section['key'] == key), None)


def _dashboard_brand_name(user=None):
    profile = Profile.objects.first()
    if profile and profile.name:
        return profile.name
    return user.get_username() if user and user.is_authenticated else 'Portfolio'


def dashboard_login(request):
    next_url = request.GET.get('next') or request.POST.get('next', '')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user.is_staff and user.is_active:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('dashboard')
        form.add_error(None, 'This account does not have dashboard access.')
    return render(request, 'dashboard/login.html', {'form': form, 'next': next_url, 'brand_name': _dashboard_brand_name(request.user)})


@login_required(login_url='dashboard_login')
def dashboard_logout(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    logout(request)
    return redirect('dashboard_login')


@staff_member_required(login_url='dashboard_login')
def dashboard_home(request):
    counts = [
        {'label': section['label'], 'count': section['model'].objects.count(), 'key': section['key']}
        for section in DASHBOARD_SECTIONS if section['key'] != 'messages'
    ]
    return render(request, 'dashboard/home.html', {
        'sections': DASHBOARD_SECTIONS,
        'counts': counts,
        'unread_count': ContactMessage.objects.filter(is_read=False).count(),
        'recent_messages': ContactMessage.objects.all()[:5],
        'brand_name': _dashboard_brand_name(request.user),
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_section(request, section_key):
    section = _dashboard_section(section_key)
    if not section:
        from django.http import Http404
        raise Http404
    records = section['model'].objects.all()
    rows = []
    for record in records:
        cells = []
        for label, attr in section['columns']:
            value = getattr(record, attr, '')
            if callable(value):
                value = value()
            if attr == 'file' and value:
                value = value.name.rsplit('/', 1)[-1]
            elif hasattr(value, 'strftime'):
                value = value.strftime('%d %b %Y')
            elif isinstance(value, bool):
                value = 'Yes' if value else 'No'
            cells.append(value or '—')
        rows.append({'record': record, 'cells': cells})
    return render(request, 'dashboard/list.html', {
        'sections': DASHBOARD_SECTIONS, 'section': section, 'rows': rows,
        'can_manage': section['form'] is not None,
        'brand_name': _dashboard_brand_name(request.user),
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_edit(request, section_key, pk=None):
    section = _dashboard_section(section_key)
    if not section or section['form'] is None:
        from django.http import Http404
        raise Http404
    instance = get_object_or_404(section['model'], pk=pk) if pk else None
    if section_key == 'profile' and instance is None:
        instance = section['model'].objects.first()
    form = section['form'](request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"{section['label']} saved successfully.")
        return redirect('dashboard_section', section_key=section_key)
    return render(request, 'dashboard/form.html', {
        'sections': DASHBOARD_SECTIONS, 'section': section, 'form': form,
        'is_edit': instance is not None,
        'brand_name': _dashboard_brand_name(request.user),
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_delete(request, section_key, pk):
    section = _dashboard_section(section_key)
    if not section or section['form'] is None:
        from django.http import Http404
        raise Http404
    record = get_object_or_404(section['model'], pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, f"{section['label']} item deleted.")
        return redirect('dashboard_section', section_key=section_key)
    return render(request, 'dashboard/delete.html', {'sections': DASHBOARD_SECTIONS, 'section': section, 'record': record, 'brand_name': _dashboard_brand_name(request.user)})


@staff_member_required(login_url='dashboard_login')
def dashboard_mark_read(request, pk):
    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = True
    message.save(update_fields=['is_read'])
    messages.success(request, 'Message marked as read.')
    return redirect('dashboard_section', section_key='messages')


def index(request):
    profile = Profile.objects.first()
    skills_qs = Skill.objects.all()

    # Group skills by category
    skills_by_category = {}
    for skill in skills_qs:
        cat = skill.get_category_display()
        skills_by_category.setdefault(cat, []).append(skill)

    experiences = Experience.objects.all()
    education = Education.objects.all()
    achievements = Achievement.objects.all()
    projects = Project.objects.all()
    featured_projects = projects.filter(is_featured=True)
    resume = Resume.objects.first()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()
        if name and email and message_body:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message_body
            )
            messages.success(request, "Your message has been sent! I'll get back to you soon.")
            return redirect('index')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'index.html', {
        'profile': profile,
        'skills_by_category': skills_by_category,
        'experiences': experiences,
        'education': education,
        'achievements': achievements,
        'projects': projects,
        'featured_projects': featured_projects,
        'resume': resume,
    })


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    other_projects = Project.objects.exclude(pk=project.pk)[:3]
    return render(request, 'project_detail.html', {
        'project': project,
        'other_projects': other_projects,
        'profile': Profile.objects.first(),
        'resume': Resume.objects.first(),
    })


def section_page(request, page):
    profile = Profile.objects.first()
    context = {'profile': profile, 'resume': Resume.objects.first()}
    if page == 'about':
        context.update({
            'skills_by_category': {},
            'experiences': Experience.objects.all(),
            'education': Education.objects.all(),
        })
        for skill in Skill.objects.all():
            context['skills_by_category'].setdefault(skill.get_category_display(), []).append(skill)
        return render(request, 'about.html', context)
    if page == 'work':
        context['projects'] = Project.objects.all()
        return render(request, 'work.html', context)
    if page == 'achievements':
        context['achievements'] = Achievement.objects.all()
        return render(request, 'achievements.html', context)
    if page == 'contact':
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            subject = request.POST.get('subject', '').strip()
            message_body = request.POST.get('message', '').strip()
            if name and email and message_body:
                ContactMessage.objects.create(name=name, email=email, subject=subject, message=message_body)
                messages.success(request, "Your message has been sent! I'll get back to you soon.")
                return redirect('contact')
            messages.error(request, 'Please fill in all required fields.')
        return render(request, 'contact.html', context)
