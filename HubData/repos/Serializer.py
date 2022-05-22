from rest_framework import serializers
from repos.models import Organization, Repository, Branch, Commit, User


NAME = 'name'


class CommitSerializer(serializers.ModelSerializer):
    repo = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    def get_repo(self, obj: Commit):
        foo: str = obj.repo.__str__()

        return foo.split('/')[-1]
    
    def get_branch(self, obj: Commit):
        foo: str = obj.branch.__str__()

        return foo.split('/')[-1]

    def get_user(self, obj: Commit):
        return {
            'name': obj.user.name,
            'email': obj.user.email,
        }

    def get_stats(self, obj: Commit):
        additions = obj.additions
        deletions = obj.deletions
        return {
            'additions' : additions,
            'deletions' : deletions,
            'amount_of_changes' : additions - deletions,
            'total_changes' : additions + deletions,
        }
    
    class Meta:
        model = Commit
        fields = [
            'id',
            'sha',
            'repo',
            'branch',
            'user',
            'date',
            'stats',
        ]
"""
{
    "sha": "asdfasdfasdfasdfasdfsdf",
    "name": "testname2",
    "email": "test2@email.com",
    "date": "2022-05-22T16:28",
    "additions": 3,
    "deletions": 3
}
"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class BranchSerializer(serializers.ModelSerializer):
    repo = serializers.SerializerMethodField()

    def get_repo(self, obj: Branch):
        repo: str = obj.repo.__str__()

        return repo.split('/')[-1]
    
    class Meta:
        model = Branch
        fields = [
            'id',
            'name',
            'repo',
            'create_at',
        ]


class RepositorySerializer(serializers.ModelSerializer):
    org = serializers.SerializerMethodField()
    branches = serializers.SerializerMethodField()

    def get_org(self, obj: Repository):
        return obj.org.__str__()

    def get_branches(self, obj: Repository):
        return [branch[0] for branch in Branch.objects.filter(repo=obj.id).values_list(NAME)]
    
    class Meta:
        model = Repository
        fields = [
            'id',
            'name',
            'org',
            'branches',
        ]

class OrganizationSerializer(serializers.ModelSerializer):
    repos = serializers.SerializerMethodField()

    def get_repos(self, obj: Organization):
        return [repo[0] for repo in Repository.objects.filter(org=obj.id).values_list(NAME)]

    class Meta:
        model = Organization
        fields = [
            'id',
            'name',
            'repos',
        ]