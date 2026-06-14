from rest_framework import serializers
from .models import Group, GroupMember


class GroupMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupMember
        fields = [
            'id',
            'group',
            'user',
            'joined_at',
            'left_at',
            'is_active'
        ]


class GroupSerializer(serializers.ModelSerializer):
    members = GroupMemberSerializer(
        source='groupmember_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'members'
        ]
