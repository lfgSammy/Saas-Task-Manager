from django.urls import path
from . import views

urlpatterns = [
    path('workspaces/', views.WorkspaceListView.as_view(), name='workspace-list'),
    path('workspaces/<int:workspace_id>/', views.WorkspaceDetailView.as_view(), name='workspace-detail'),
    path('workspaces/<int:workspace_id>/members/', views.MemberView.as_view(), name='members'),
]