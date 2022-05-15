from ast import Or
from sre_constants import SUCCESS
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from repos.models import Organization, Repository, Branch
from repos.Serializer import OrganizationSerializer, RepositorySerializer, BranchSerializer


REQUEST_STR = 'request'
GeneralFailureResponse = Response('Failure')

GET = 'get'
CREATE = 'create'

SUCCESS = {
    GET : 200, 
    CREATE : 201
}


class RepoViews(APIView):
    __queryset = Repository.objects.all()

    @property
    def queryset(self):
        return self.__queryset
    
    def get(self, request: Request, org: str, repo: str):
        try: 
            _org = Organization.objects.get(name=org)
            _repo = Repository.objects.filter(org=_org, name=repo)[0]
        except: GeneralFailureResponse

        queryset = self.queryset.get(org=_org, repo=_repo)
        serializer = RepositorySerializer(queryset, context={REQUEST_STR:request})
        return Response(serializer.data, status=SUCCESS[GET])
    
    def post(self, request: Request, org: str, repo: str):
        try: _org = Organization.objects.get(name=org)
        except: GeneralFailureResponse

class ReposViews(APIView):
    __queryset = Repository.objects.all()

    @property
    def queryset(self):
        return self.__queryset

    def get(self, request: Request, org: str):
        try: _org = Organization.objects.get(name=org)
        except: GeneralFailureResponse

        queryset = self.queryset.filter(org=_org)
        serializer = RepositorySerializer(queryset, context={REQUEST_STR:request}, many=True)
        return Response(serializer.data, status=SUCCESS[GET])
    
    def post(self, request: Request, org: str):
        try: _org = Organization.objects.get(name=org)
        except: GeneralFailureResponse
        
        serializer = RepositorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(org=_org)
        return Response(serializer.data, status=SUCCESS[CREATE])

class OrgsViews(APIView):
    __queryset = Organization.objects.all()

    @property
    def queryset(self):
        return self.__queryset

    def get(self, request: Request):
        serializer = OrganizationSerializer(self.queryset, context={REQUEST_STR:request}, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=SUCCESS[CREATE])
