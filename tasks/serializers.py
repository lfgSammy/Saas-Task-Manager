from rest_framework import serializers
from .models import Project, Task, Comment
from organization.serializers import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only= True)
    class Meta:
        model = Project
        fields = ['id','name','description','status','created_by','created_at','updated_at']
        read_only_fields = ['created_by']

class TaskSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only= True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset= Project.objects.all(), source= 'project', write_only = True
    )
    assigned_to = UserSerializer(many= True, read_only= True)
    created_at = UserSerializer(read_only= True)
    
    class Meta:
        model = Task
        fields = ['id','title','project','project_id', 'description',
                  'status','priority','assigned_at',
                  'created_by', 'due_date','updated_at','created_at'
                  ]
        related_fields = ['created_by']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only= True)
    task = TaskSerializer(read_only=  True)

    class Meta:
        model = Comment
        fields = [
            'id','task','author','content','created_at','updated_at'
        ]
        read_only_fields = ['author', 'task']
