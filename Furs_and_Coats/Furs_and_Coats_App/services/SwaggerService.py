from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response


# class UserList(APIView):
#     @swagger_auto_schema(
#         operation_description="Get list of users",
#         responses={200: UserSerializer(many=True)}
#     )
#     def get(self, request):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)
