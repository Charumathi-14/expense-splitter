from rest_framework import viewsets

from .models import Group, GroupMember
from .serializers import GroupSerializer, GroupMemberSerializer


class GroupViewSet(viewsets.ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class GroupMemberViewSet(viewsets.ModelViewSet):

    queryset = GroupMember.objects.all()
    serializer_class = GroupMemberSerializer