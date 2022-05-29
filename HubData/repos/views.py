from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from repos.models import Organization, Repository, Branch, Commit, User
from repos.Serializer import OrganizationSerializer, RepositorySerializer, BranchSerializer, CommitSerializer, UserSerializer


REQUEST_STR = 'request'
GeneralFailureResponse = Response('Failure')

GET = 'get'
CREATE = 'create'

SUCCESS = {
    GET : 200, 
    CREATE : 201
}


class CommitsViews(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    __queryset = Commit.objects.all()

    @property
    def queryset(self):
        return self.__queryset
    
    def get(self, request: Request, org: str, repo: str, sha: str):
        try: 
            _org = Organization.objects.get(name=org)
            _repo = Repository.objects.filter(org=_org, name=repo)[0]
            _branch = Branch.objects.filter(repo=_repo, name=sha)[0]
        except: GeneralFailureResponse

        since = request.query_params.get('since', False)
        until = request.query_params.get('until', False)

        if since and until:
            queryset = self.queryset.filter(repo=_repo, branch=_branch, date__range=[since, until])
        else:
            queryset = self.queryset.filter(repo=_repo, branch=_branch)
        serializer = CommitSerializer(queryset, context={REQUEST_STR:request}, many=True)
        return Response(serializer.data, status=SUCCESS[GET])

    def post(self, request: Request, org: str, repo: str, sha: str):
        try: 
            _org = Organization.objects.get(name=org)
            _repo = Repository.objects.filter(org=_org, name=repo)[0]
            _branch = Branch.objects.filter(repo=_repo, name=sha)[0]
        except: GeneralFailureResponse
        try:
            userdata = {
                'name': request.data['name'],
                'email': request.data['email']
            } 
            _user = User.objects.filter(name=userdata['name'], email=userdata['email'])[0]
        except: 
            userserializer = UserSerializer(data=userdata)
            if userserializer.is_valid(): userserializer.save()
            
            _user = User.objects.get(email=userdata['email'])
            
        serializer = CommitSerializer(data=request.data)
        if serializer.is_valid(): 
            serializer.save(
                repo=_repo, 
                branch=_branch,
                user=_user,
                additions=request.data['additions'],
                deletions=request.data['deletions'],
                )
        return Response(serializer.data, status=SUCCESS[CREATE])

class RepoViews(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    __queryset = Repository.objects.all()

    @property
    def queryset(self):
        return self.__queryset
    
    def get(self, request: Request, org: str, repo: str):
        try: 
            _org = Organization.objects.get(name=org)
        except: GeneralFailureResponse

        queryset = self.queryset.get(org=_org, name=repo)
        serializer = RepositorySerializer(queryset, context={REQUEST_STR:request})
        return Response(serializer.data, status=SUCCESS[GET])
    
    def post(self, request: Request, org: str, repo: str):
        try: 
            _org = Organization.objects.get(name=org)
            _repo = Repository.objects.get(name=repo)
        except: GeneralFailureResponse

        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid(): serializer.save(repo=_repo)
        return Response(serializer.data, status=SUCCESS[CREATE])

class ReposViews(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
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
        try: 
            _org = Organization.objects.get(name=org)
            _repo = self.queryset.filter(name=request.data['name'])
        except: GeneralFailureResponse
        if len(_repo) > 1: return GeneralFailureResponse
        
        serializer = RepositorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(org=_org)
        return Response(serializer.data, status=SUCCESS[CREATE])

class OrgsViews(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
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
