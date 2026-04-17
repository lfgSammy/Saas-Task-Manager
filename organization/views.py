from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.db import transaction
from django.contrib.auth import authenticate
from .models import Workspace, Membership
from .serializers import WorkspaceSerializer, MembershipSerializer
from users.models import User


class WorkspaceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = Membership.objects.filter(user= request.user)
        workspaces = [m.workspace for m in memberships]
        serializer = WorkspaceSerializer(workspaces, many= True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = WorkspaceSerializer(data= request.data)
        if serializer.is_valid():
            with transaction.atomic():
                workspace = serializer.save(owner = request.user)
                Membership.objects.create(
                    user = request.user,
                    workspace = workspace,
                    role = 'owner'
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class WorkspaceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, workspace_id, user):
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            membership = Membership.objects.filter(
                user= user, workspace= workspace).first()
            if not membership:
                return None, None
            return workspace, membership
        except workspace.DoesNotExist:
            return None, None
        
    def get(self,request, workspace_id):
        workspace, membership = self.get_object(workspace_id, request.user)
        if not workspace:
            return Response({'error':'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data)
    
    def delete(self,request, workspace_id):
        workspace, membership = self.get_object(workspace_id, request.user)
        if not workspace:
            return Response({'error':'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
        if membership.role != 'owner':
            return Response({'error':'Only owner can delete can delete this workspace'},
                            status=status.HTTP_403_FORBIDDEN)
        workspace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class MemberView(APIView):
    permission_classes = [IsAuthenticated]

    def get_membership(self, workspace_id, user):
        try:
            workspace = Workspace.objects.get(id = workspace_id)
            membership = Membership.objects.filter(
                user = user,
                workspace = workspace
            ).first()
            return workspace, membership
        
        except Workspace.DoesNotExist:
            return None, None
    
    def get(self, request, workspace_id):
        workspace, membership = self.get_membership(workspace_id, request.user)
        if not membership:
            return Response({'error':'Workspace not found'},
                            status=status.HTTP_404_NOT_FOUND)
        members = Membership.objects.filter(workspace= workspace)
        serializer = MembershipSerializer(members, many= True)
        return Response(serializer.data)
    
    def post(self, request, workspace_id):
        workspace, membership = self.get_membership(workspace_id, request.user)
        if not membership:
            return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
        if membership.role not in ['owner', 'admin']:
            return Response({'error': 'Only owners and admins can invite members'},
                            status=status.HTTP_403_FORBIDDEN)
        username = request.data.get('username')
        role = request.data.get('role', 'member')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        if Membership.objects.filter(user=user, workspace=workspace).exists():
            return Response({'error': 'User is already a member'}, status=status.HTTP_400_BAD_REQUEST)
        if membership.role == 'admin' and role == 'owner':
            return Response({'error': 'Admins cannot assign owner role'}, status=status.HTTP_403_FORBIDDEN)
        new_membership = Membership.objects.create(user=user, workspace=workspace, role=role)
        serializer = MembershipSerializer(new_membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request, workspace_id):
        workspace, membership = self.get_membership(workspace_id, request.user)
        if not membership:
            return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
        if membership.role not in ['owner', 'admin']:
            return Response({'error': 'Only owners and admins can remove members'},
                            status=status.HTTP_403_FORBIDDEN)
        username = request.data.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        target_membership = Membership.objects.filter(user=user, workspace=workspace).first()
        if not target_membership:
            return Response({'error': 'User is not a member'}, status=status.HTTP_404_NOT_FOUND)
        if target_membership.role == 'owner':
            return Response({'error': 'Cannot remove the workspace owner'}, status=status.HTTP_403_FORBIDDEN)
        target_membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)