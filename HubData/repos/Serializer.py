from dataclasses import field
from rest_framework import serializers
from repos.models import Organization, Repository, Branch, Commit


NAME = 'name'


class CommitSerializer(serializers.Serializer):
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
        foo: str = obj.email.__str__()

        return foo.split('@')[0]

    def get_stats(self, obj: Commit):
        additions = obj.additions
        deletions = obj.deletions
        return {
            'additions' : additions,
            'deletions' : deletions,
            'amount_of_changes' : abs(additions - deletions),
            'total_changes' : additions + deletions,
        }
    
    class Meta:
        model = Commit
        field = [
            'id',
            'sha',
            'repo',
            'branch',
            'user',
            'email',
            'date',
            'stats',
        ]

class BranchSerializer(serializers.ModelSerializer):
    repo = serializers.SerializerMethodField()

    def get_repo(self, obj: Branch):
        repo: str = obj.repo.__str__()

        return repo.split('/')[-1]
    
    class Meta:
        model = Branch
        field = [
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
        field = [
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