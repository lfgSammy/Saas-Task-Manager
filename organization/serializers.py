from rest_framework import serializers
from .models import Workspace, Membership
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email', 'created_at']

class WorkspaceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only= True)
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'description', 'owner','created_at', 'updated_at']
        read_only_fields = ['owner']


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only= True)
    workspace = WorkspaceSerializer(read_only = True)
    class Meta:
        model = Membership
        fields = ['id', 'user', 'workspace', 'role', 'joined_at']
    
