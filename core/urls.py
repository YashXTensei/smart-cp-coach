from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('problems/', views.problem_list, name='problem_list'),
    path('problems/add/', views.add_problem, name='add_problem'),
    path('problems/edit/<int:pk>/', views.edit_problem, name='edit_problem'),
    path('problems/delete/<int:pk>/', views.delete_problem, name='delete_problem'),
    path("profile/", views.profile_view, name="profile"),
    path('dashboard/ask-coach/', views.ask_coach, name='ask_coach'),
]