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
from opsweb.serializers import (UserSerializer)
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
                          # permissions.DjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = User.objects.all().order_by("username")
    lookup_field = 'id'

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('user_id', 'username', 'email'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("UserList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("UserList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except User.DoesNotExist:
                return False

    def get(self, request, format = None):
        """
        Get all users.
        """
        query_params = request.query_params
        if query_params and (query_params.get('user_id') or \
                             query_params.get('username') or \
                             query_params.get('email')):
            if not self.exist_object(**query_params):
                return Response({
                    "status": "Not Found.",
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "data": []
                })
            else:
                return Response({
                    "status": "Success.",
                    "status_code": status.HTTP_200_OK,
                    "data": []
                })
        else:
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
            serializer = UserSerializer(user, data = request.data,
                                        context = {'request': request},
                                        partial = True)
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
            raise CustomException("Not Found the User.", status_code = status.HTTP_200_OK)


class UserDetail(APIView):
    """
    Retrieve, update a user instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrAdmin)
    queryset = User.objects
    lookup_field = 'id'

    def get_object(self, pk):
        try:
            return self.queryset.get(pk = pk)
        except User.DoesNotExist:
            raise CustomException("Not Found the User.", status_code = status.HTTP_200_OK)

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
        serializer = UserSerializer(user, data = request.data,
                                    context = {'request': request},
                                    partial = True)
        if serializer.is_valid():
            query_params = request.query_params
            if query_params.get("resetPassword"):
                password = user.username
                logger.debug("UserDetail@put@password@%s" % password)
            else:
                password = None

            user = serializer.update(user, serializer.validated_data,
                                     password = password)
            serializer = UserSerializer(user, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": 200,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete the user.
        """
        try:
            user = self.get_object(pk)
            self.check_object_permissions(request, user)
            user.delete()
            return Response({
                "status_code": status.HTTP_204_NO_CONTENT,
                "status": "No Content.",
                "data": []
            })
        except:
            return Response({
                "status": "Not Found.",
                "status_code": status.HTTP_404_NOT_FOUND,
                "data": []
            })

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
            return Response({
                "status": "Not Found.",
                "status_code": status.HTTP_404_NOT_FOUND,
                "data": []
            })

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
