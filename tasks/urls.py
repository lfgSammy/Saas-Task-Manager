from django.urls import path
from . import views

urlpatterns = [
    path('workspaces/<int:workspace_id>/projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/<int:project_id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:project_id>/tasks/', views.TaskListView.as_view(), name='task-list'),
    path('tasks/<int:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', views.CommentListView.as_view(), name='comment-list'),
]
