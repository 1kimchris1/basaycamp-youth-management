from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('participants/', views.participants_view, name='participants'),
    path('participants/add/', views.add_participant_view, name='add_participant'),
    path('participants/edit/<int:participant_id>/', views.edit_participant_view, name='edit_participant'),
    path('participants/delete/<int:participant_id>/', views.delete_participant_view, name='delete_participant'),
    path('churches/', views.churches_view, name='churches'),
    path('churches/add/', views.add_church_view, name='add_church'),
    path('churches/<int:church_id>/members/', views.church_members_view, name='church_members'),
    path('activities/', views.activities_view, name='activities'),
    path('finances/', views.finances_view, name='finances'),
    path('finances/edit/<int:finance_id>/', views.edit_finance_view, name='edit_finance'),
    path('finances/delete/<int:finance_id>/', views.delete_finance_view, name='delete_finance'),
    path('api/participants/', views.participants_api_view, name='participants_api'),
    path('admin-scoring/', views.admin_scoring_view, name='admin_scoring'),
    path('demerit-details/<int:survival_result_id>/', views.demerit_details_view, name='demerit_details'),
    path('merit-details/<int:survival_result_id>/', views.merit_details_view, name='merit_details'),
    
    # Game Result Edit and Delete URLs
    path('activities/edit-vs-game/<int:game_id>/', views.edit_vs_game_view, name='edit_vs_game'),
    path('activities/delete-vs-game/<int:game_id>/', views.delete_vs_game_view, name='delete_vs_game'),
    path('activities/edit-survival-game/<int:result_id>/', views.edit_survival_game_view, name='edit_survival_game'),
    path('activities/delete-survival-game/<int:result_id>/', views.delete_survival_game_view, name='delete_survival_game'),
    
    # Staff Management URLs
    path('staff/', views.staff_management_view, name='staff_management'),
    path('staff/add/', views.add_staff_view, name='add_staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff_view, name='delete_staff'),
    
    # Default redirect to dashboard
    path('', views.dashboard_view, name='home'),
]
