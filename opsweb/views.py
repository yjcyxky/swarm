import logging, json
from django.contrib.auth.models import User
from django.http import Http404
from django.template.loader import get_template
from django.http import JsonResponse
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import permissions
from opsweb.serializers import (UserSerializer, PasswordSerializer)
from opsweb.permissions import (IsOwnerOrAdmin, IsOwner)
from opsweb.pagination import CustomPagination
from opsweb.exceptions import CustomException

logger = logging.getLogger(__name__)

class UserList(generics.GenericAPIView):
    """
    List all users, or create a new user.
    """
    pagination_class = CustomPagination
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = User.objects.all().order_by("username")

    def get(self, request, format = None):
        """
        Get all users.
        """
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a user instance.
        """
        serializer = UserSerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            serializer = UserSerializer(user, context = {'request': request})
            return Response({
                "status": "Created Success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Modify account information for the user.
        """
        try:
            username = request.data.get("username")
            if username is None:
                raise CustomException("You need to set username in post.",
                                      status_code = status.HTTP_400_BAD_REQUEST)
            user = self.queryset.get(username = username)
            serializer = UserSerializer(user, data = request.data, context = {'request': request})
            if serializer.is_valid():
                user = serializer.update(user, serializer.validated_data)
                serializer = UserSerializer(user, context = {'request': request})
                return Response({
                    "status": "Updated Success",
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data
               })
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            raise Http404


class UserDetail(APIView):
    """
    Retrieve, update a user instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrAdmin)
    queryset = User.objects
    def get_object(self, pk):
        try:
            return self.queryset.get(pk = pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Retrieve account information for a specified user.
        """
        user = self.get_object(pk)
        # 用于自定义permission的主动检查
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
       })

    def put(self, request, pk):
        """
        Modify password for the user.
        """
        # 普通用户无法access PUT方法
        user = self.get_object(pk)
        self.check_object_permissions(request, user)
        serializer = PasswordSerializer(user, data = request.data, context = {'request': request})
        if serializer.is_valid():
            password = serializer.validated_data.get("password")
            serializer.update(user, password)
            user_info = serializer.data
            user_info.update({
                "username": user.get_username(),
                "last_login": user.last_login,
                "email": user.email,
                "is_active": user.is_active,
                "is_staff": user.is_staff
            })
            return Response({
                "status": "Updated Success",
                "status_code": 200,
                "user_info": user_info
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class APIDetail(APIView):
    """
    Retrieve a specified API instance.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def gen_response_obj(self, request, message = None,
                         collections = None, next = None):
        collections.update({
            "api_uri": request.get_raw_uri() if isinstance(request, Request) else None,
            "next": next
        })
        return {
            "status": message,
            "data": collections,
            "status_code": status.HTTP_200_OK
        }

    def get(self, request, api_name):
        logger.debug('API_NAME: %s' % api_name)
        logger.debug(request.get_raw_uri())
        user = request.user
        if api_name in ('apis', 'navbar', 'sidebar', 'welcome'):
            t = get_template('%s.json.tmpl' % api_name)
            api_prefix = request.get_host()
            api_pool = t.render({"api_prefix": api_prefix, "user": user})
            collections = {
                'apiData': json.loads(api_pool)
            }
            response_obj = self.gen_response_obj(request, message = 'Success.',
                                                 collections = collections)
            return JsonResponse(response_obj, status = 200)
        else:
            raise Http404

def custom404(request):
    return JsonResponse({
        'status_code': 404,
        'details': 'The resource was not found.',
        'status': 'Failed'
    }, status = status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def current_user(request):
        """
        Retrieve account information for current user.
        """
        user = request.user
        serializer = UserSerializer(user, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
       })
