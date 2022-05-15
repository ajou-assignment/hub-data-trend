from ast import Or
from sre_constants import SUCCESS
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from repos.models import Organization, Repository
from repos.Serializer import OrganizationSerializer


REQUEST_STR = 'request'
GeneralFailureResponse = Response('Failure')

GET = 'get'
CREATE = 'create'

SUCCESS = {
    GET : 200, 
    CREATE : 201
}


class OrgViews(APIView):
    __queryset = Organization.objects.all()

    @property
    def queryset(self):
        return self.__queryset

    def get(self, request: Request, org: str):
        try: queryset = self.queryset.get(name=org)
        except: GeneralFailureResponse
        serializer = OrganizationSerializer(queryset, context={REQUEST_STR:request})
        return Response(serializer.data)

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
