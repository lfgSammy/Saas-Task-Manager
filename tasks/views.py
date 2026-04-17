from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Project, Task, Comment
from .serializers import ProjectSerializer, TaskSerializer, CommentSerializer
from organization.models import Workspace, Membership


def get_membership(user, workspace_id):
    try:
        workspace = Workspace.objects.get(id=workspace_id)
        membership = Membership.objects.filter(
            user=user, workspace=workspace).first()
        return workspace, membership
    except Workspace.DoesNotExist:
        return None, None


class ProjectListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_id):
        workspace, membership = get_membership(request.user, workspace_id)
        if not membership:
            return Response({'error': 'Workspace not found or access denied'},
                            status=status.HTTP_404_NOT_FOUND)
        projects = Project.objects.filter(workspace=workspace)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, workspace_id):
        workspace, membership = get_membership(request.user, workspace_id)
        if not membership:
            return Response({'error': 'Workspace not found or access denied'},
                            status=status.HTTP_404_NOT_FOUND)
        # only owner or admin can create projects
        if membership.role not in ['owner', 'admin']:
            return Response({'error': 'Only owners and admins can create projects'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(workspace=workspace, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, project_id, user):
        try:
            project = Project.objects.get(id=project_id)
            workspace, membership = get_membership(user, project.workspace.id)
            return project, membership
        except Project.DoesNotExist:
            return None, None

    def get(self, request, project_id):
        project, membership = self.get_object(project_id, request.user)
        if not project:
            return Response({'error': 'Project not found'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def delete(self, request, project_id):
        project, membership = self.get_object(project_id, request.user)
        if not project:
            return Response({'error': 'Project not found'},
                            status=status.HTTP_404_NOT_FOUND)
        if membership.role not in ['owner', 'admin']:
            return Response({'error': 'Only owners and admins can delete projects'},
                            status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'},
                            status=status.HTTP_404_NOT_FOUND)
        workspace, membership = get_membership(request.user, project.workspace.id)
        if not membership:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'},
                            status=status.HTTP_404_NOT_FOUND)
        workspace, membership = get_membership(request.user, project.workspace.id)
        if not membership:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        if membership.role not in ['owner', 'admin']:
            return Response({'error': 'Only owners and admins can create tasks'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, task_id, user):
        try:
            task = Task.objects.get(id=task_id)
            workspace, membership = get_membership(user, task.project.workspace.id)
            return task, membership
        except Task.DoesNotExist:
            return None, None

    def get(self, request, task_id):
        task, membership = self.get_object(task_id, request.user)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def patch(self, request, task_id):
        task, membership = self.get_object(task_id, request.user)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        # members can only update status of tasks assigned to them
        if membership.role == 'member':
            if request.user not in task.assigned_to.all():
                return Response({'error': 'You can only update tasks assigned to you'},
                                status=status.HTTP_403_FORBIDDEN)
            allowed_fields = {'status'}
            if not set(request.data.keys()).issubset(allowed_fields):
                return Response({'error': 'Members can only update task status'},
                                status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task, membership = self.get_object(task_id, request.user)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        if membership.role not in ['owner', 'admin']:
            return Response({'error': 'Only owners and admins can delete tasks'},
                            status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        workspace, membership = get_membership(request.user, task.project.workspace.id)
        if not membership:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        comments = Comment.objects.filter(task=task)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        workspace, membership = get_membership(request.user, task.project.workspace.id)
        if not membership:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)