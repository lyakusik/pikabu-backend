from .models import *
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import *
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework_jwt.serializers import JSONWebTokenSerializer

# Create your views here.

def index(request):
    return HttpResponse('check')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def posts_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializers = PostSerializer(posts, many=True)
        return Response(serializers.data, status=200)
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist as err:
        return JsonResponse({'message': str(err)}, status=400)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)
    if request.method == 'DELETE':
        post.delete()
        return Response({'message': 'delete post ' + str(post)})

    if request.method == 'PUT':
        serializer = PostSerializer(data=request.data, instance=post)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


@api_view(['GET', 'POST'])
def categories_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializers = CategorySerializer(categories, many=True)
        return Response(serializers.data, status=200)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET'])
def posts_list_category(request, category_id):
    try:
        posts = Post.objects.filter(category=category_id)
    except Post.DoesNotExist as err:
        return JsonResponse({'message': str(err)}, status=400)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=200)




class CommentsListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_comments(self, post_id):
        try:
            comments = Comment.objects.filter(post=post_id)
            return comments
        except Comment.DoesNotExist as err:
            return Response({'error': 'Object does not exists'})

    def get(self, request, post_id=None):
        comments = self.get_comments(post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, post_id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)



class CommentDetailAPIView(APIView):
    def get_comment(self, pk):
        try:
            comment = Comment.objects.get(id=pk)
            return comment
        except Comment.DoesNotExist as err:
            return Response({'error': 'Object does not exists'})

    def get(self, request, post_id=None, pk=None):
        comment = self.get_comment(pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=200)

    def put(self, request, post_id=None, pk=None):
        comment = self.get_comment(pk)
        serializer = CommentSerializer(instance=comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, post_id=None, pk=None):
        comment = self.get_comment(pk)
        comment.delete()
        return Response({'message': 'delete comment ' + str(comment)})



class UsersListAPIView(APIView):
    def get(self,request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=200)


class UserDetailAPIView(APIView):
    def get_user(self, pk):
        try:
            user = User.objects.get(id=pk)
            return user
        except User.DoesNotExist as err:
            return Response({'error': 'Object does not exists'})
    def get(self, request, pk=None):
        user = self.get_user(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)



class RegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                return Response({'detail': str(e)}, status=400)

            token_serializer = JSONWebTokenSerializer(data=serializer.data)
            token = token_serializer.validate(request.data).get('token')
            return Response({'token': token})
        return Response(serializer.errors, status=400)
