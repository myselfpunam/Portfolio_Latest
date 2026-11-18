from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/', views.dashboard_home, name='dashboard'),
    path('dashboard/<slug:section_key>/', views.dashboard_section, name='dashboard_section'),
    path('dashboard/<slug:section_key>/add/', views.dashboard_edit, name='dashboard_add'),
    path('dashboard/<slug:section_key>/<int:pk>/edit/', views.dashboard_edit, name='dashboard_edit'),
    path('dashboard/<slug:section_key>/<int:pk>/delete/', views.dashboard_delete, name='dashboard_delete'),
    path('dashboard/messages/<int:pk>/read/', views.dashboard_mark_read, name='dashboard_mark_read'),
    path('resume/cv.pdf', views.resume_pdf, name='resume_pdf'),
    path('chat/ask/', views.portfolio_chat, name='portfolio_chat'),
    path('about/', views.section_page, {'page': 'about'}, name='about'),
    path('work/', views.section_page, {'page': 'work'}, name='work'),
    path('achievements/', views.section_page, {'page': 'achievements'}, name='achievements'),
    path('contact/', views.section_page, {'page': 'contact'}, name='contact'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
]
