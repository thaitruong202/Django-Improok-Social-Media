from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Count
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.views import Response, APIView
import cloudinary.uploader

from .models import Role, User, Post, Account, PostImage, Comment, ConfirmStatus, AlumniAccount, Reaction, PostReaction, \
    InvitationGroup, PostInvitation, PostSurvey, SurveyQuestion, SurveyQuestionOption, SurveyAnswer, SurveyResponse
from .paginators import PostPagination, MyPageSize
from .permissions import CommentOwner, PostOwner, IsAdmin
from .serializers import UserSerializer, RoleSerializer, PostSerializer, AccountSerializer, PostImageSerializer, \
    CommentSerializer, CreateAccountSerializer, CreateUserSerializer, UpdateUserSerializer, CreatePostSerializer, \
    UpdatePostSerializer, CreatePostImageSerializer, UpdatePostImageSerializer, CreateCommentSerializer, \
    UpdateCommentSerializer, UpdateAccountSerializer, ConfirmStatusSerializer, AlumniAccountSerializer, \
    CreateAlumniAccountSerializer, UpdateAlumniAccountSerializer, ReactionSerializer, PostReactionSerializer, \
    CreatePostReactionSerializer, UpdatePostReactionSerializer, InvitationGroupSerializer, \
    CreateInvitationGroupSerializer, UpdateInvitationGroupSerializer, AccountSerializerForInvitationGroup, \
    PostInvitationSerializer, CreatePostInvitationSerializer, UpdatePostInvitationSerializer, EmailSerializer, \
    PostSurveySerializer, CreatePostSurveySerializer, UpdatePostSurveySerializer, SurveyQuestionSerializer, \
    CreateSurveyQuestionSerializer, UpdateSurveyQuestionSerializer, SurveyQuestionOptionSerializer, \
    CreateSurveyQuestionOptionSerializer, UpdateSurveyQuestionOptionSerializer, SurveyAnswerSerializer, \
    SurveyAnswerSerializerForRelated, SurveyResponseSerializer, CreateSurveyResponseSerializer, \
    CreateSurveyAnswerSerializer, UpdateSurveyAnswerSerializer, TempSerializer, PostReactionSerializerForAccount, \
    CommentSerializerForPost, PostSerializerForList, RetrieveInvitationGroupSerializer
from .swagger_decorators import header_authorization, delete_accounts_from_invitation_group, \
    add_or_update_accounts_from_invitation_group, add_or_update_accounts_from_post_invitation, \
    delete_accounts_from_post_invitation, send_email, warning_api, \
    add_or_update_survey_question_option_to_survey_answer, add_or_update_survey_answer_to_survey_question_option, \
    params_for_post_reaction, params_for_account_reacted_to_the_post, create_alumni_account, create_post_survey, \
    create_post_invitation


# -Role-
class RoleViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


# -ConfirmStatus-
class ConfirmStatusViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = ConfirmStatus.objects.all()
    serializer_class = ConfirmStatusSerializer


# -InvitationGroup-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class InvitationGroupViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                             generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = InvitationGroup.objects.filter(active=True)
    serializer_class = InvitationGroupSerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateInvitationGroupSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateInvitationGroupSerializer
        if self.action == 'retrieve':
            return RetrieveInvitationGroupSerializer
        return self.serializer_class

    # Tính override lại gửi context nhưng mà tự nhiên nó tự có context luôn
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     return Response(RetrieveInvitationGroupSerializer(instance, context={'request': request}).data)

    @action(methods=['GET'], detail=True, url_path='accounts')
    @method_decorator(decorator=header_authorization, name='accounts')
    def get_accounts(self, request, pk):
        accounts = self.get_object().accounts.filter(active=True).all()
        return Response(AccountSerializerForInvitationGroup(accounts, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='add_or_update_accounts')
    @method_decorator(decorator=add_or_update_accounts_from_invitation_group, name='add_or_update_accounts')
    def add_or_update_accounts(self, request, pk):
        try:
            invitation_group = self.get_object()
            list_account_id = request.data.get('list_account_id', [])
            # Truy vấn mấy tài khoản cần thêm này ra
            # Nếu mấy cái mới lấy ra mà không trùng với danh sách cần thêm thì khỏi :)))
            accounts = Account.objects.filter(id__in=list_account_id)
            if len(accounts) != len(list_account_id):
                missing_ids = set(list_account_id) - set(accounts.values_list('id', flat=True))
                raise NotFound(f"Accounts with IDs {missing_ids} do not exist.")

            invitation_group.accounts.add(*accounts)  # Truyền lẻ từng account vào nhanh hơn truyền list accounts vào
            invitation_group.save()

            return Response(InvitationGroupSerializer(invitation_group).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            error_message = str(e)
            return Response({'error kìa: ': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=True, url_path='delete_accounts')
    @method_decorator(decorator=delete_accounts_from_invitation_group, name='delete_account')
    def delete_account(self, request, pk):
        try:
            invitation_group = self.get_object()
            list_account_id = request.data.get('list_account_id', [])
            accounts = invitation_group.accounts.filter(id__in=list_account_id)
            if len(accounts) != len(list_account_id):
                missing_ids = set(list_account_id) - set(accounts.values_list('id', flat=True))
                raise NotFound(f"Accounts with IDs {missing_ids} do not exist.")

            invitation_group.accounts.remove(*accounts)
            invitation_group.save()

            return Response(InvitationGroupSerializer(invitation_group).data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            error_message = str(e)
            return Response({'error: ': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -User-
@method_decorator(decorator=header_authorization, name='list')
# @method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class UserViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView, generics.CreateAPIView,
                  generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPageSize

    # permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ['list', 'update', 'partial_update', 'destroy', 'current_user', 'get_account_by_user_id',
                           'current-user']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    # Override lại để dùng cái Serializer create, update
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateUserSerializer
        return self.serializer_class

    @action(methods=['GET'], detail=False, url_path='current-user')
    @method_decorator(decorator=header_authorization, name='current-user')
    def current_user(self, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
        # if request.user.is_authenticated:
        #     return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
        # else:
        #     return Response({'detail': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['GET'], detail=True, url_path='account')
    @method_decorator(decorator=header_authorization, name='get_account_by_user_id')
    def get_account_by_user_id(self, request, pk):
        try:
            # Lạy chúa thì ra đây là truy vấn ngược của OneToOne :)))
            user = self.get_object()
            account = user.account
            return Response(AccountSerializer(account, context={'request': request}).data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'detail': 'Account not found!!!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error_message = str(e)
            return Response({'error kìa: ': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=False, url_path='create_alumni')
    @method_decorator(decorator=create_alumni_account, name='create_alumni')
    def create_alumni(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        alumni_account_code = request.data.get('alumni_account_code')

        # user = User.objects.create(username=username, email=email, password=password, first_name=first_name,
        #                            last_name=last_name)

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        account = Account.objects.create(user=user)
        alumni = AlumniAccount.objects.create(account=account, alumni_account_code=alumni_account_code)

        return Response(status=status.HTTP_200_OK)


# -Post-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class PostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                  generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Post.objects.filter(active=True).all()
    serializer_class = PostSerializer
    pagination_class = PostPagination

    # permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [PostOwner()]
        if self.action in ['create_post_survey', 'create_post_invitation']:
            return [IsAdmin()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return PostSerializerForList
        if self.action == 'create':
            return CreatePostSerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePostSerializer
        return self.serializer_class

    # detail=True thì kẹp thêm pk (primary key)
    # Cái url_path kia là nó tạo thành enpoint ở cuối
    # post/{post_id}/comments/
    # Nếu xài cái def comments(self, request, pk) luôn thì khỏi url_path
    # Nhức nhức cái đầu ghê :v
    @action(methods=['GET'], detail=True, url_path='comments')
    @method_decorator(decorator=header_authorization, name='get_comments')
    def get_comments(self, request, pk):
        comments = self.get_object().comment_set.filter(active=True).all()

        # Nhớ .data chứ không nó lỗi
        # Thả request dô cho cái CommentSerializer bên kia nó nhận nó gắn static cho image
        return Response(CommentSerializerForPost(comments, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='post-images')
    @method_decorator(decorator=header_authorization, name='get_post_images')
    def get_post_images(self, request, pk):
        post_images = self.get_object().postimage_set.filter(active=True).all()
        return Response(PostImageSerializer(post_images, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='reactions')
    @method_decorator(decorator=params_for_post_reaction, name='get_reactions')
    # @method_decorator([header_authorization, params_for_post_reaction], name='get_reactions')
    def get_reactions(self, request, pk):
        reaction_id = request.query_params.get('reaction_id')
        account_id = request.query_params.get('account_id')
        post_reactions = PostReaction.objects.filter(post_id=pk)

        if reaction_id:
            post_reactions = post_reactions.filter(reaction_id=reaction_id)

        if account_id:
            post_reactions = post_reactions.filter(account_id=account_id)

        return Response(PostReactionSerializer(post_reactions, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='count_all_reactions')
    @method_decorator(decorator=header_authorization, name='count_all_reactions')
    def count_all_reactions(self, request, pk):
        # post_reactions_count = PostReaction.objects.filter(post_id=post.pk).values('id').annotate(count=Count('id'))
        post_reactions_count = PostReaction.objects.filter(post_id=pk).count()
        return Response(post_reactions_count, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='count_type_reactions')
    @method_decorator(decorator=header_authorization, name='count_type_reactions')
    def count_type_reactions(self, request, pk):
        # KIỂU TRUY VẤN NÀY BÁ VÃI :))) (reaction__reaction_name)
        post_reactions_count = PostReaction.objects.filter(post_id=pk).values('reaction__reaction_name') \
            .annotate(Count('id'))

        # Cách này của thầy nè :v hong thích xài
        # post_reactions_count = PostReaction.objects.filter(post_id=pk).annotate(
        #     count=Count('id')).values('reaction__reaction_name', 'count')
        return Response(post_reactions_count, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='count_comments')
    @method_decorator(decorator=header_authorization, name='count_comments')
    def count_comments(self, request, pk):
        comment_count = Comment.objects.filter(post_id=pk).count()
        return Response(comment_count, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='create_post_survey')
    @method_decorator(decorator=create_post_survey, name='create_post_survey')
    def create_post_survey(self, request):
        account_id = request.data.get('account_id')
        post_content = request.data.get('post_content')

        post = Post.objects.create(post_content=post_content, account_id=account_id)

        post_survey_title = request.data.get('post_survey_title')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        post_survey = PostSurvey.objects.create(post=post, post_survey_title=post_survey_title, start_time=start_time,
                                                end_time=end_time)

        survey_question_list = request.data.get('survey_question_list', [])
        for question in survey_question_list:
            survey_question_type_id = question.get('survey_question_type_id')
            question_content = question.get('question_content')
            question_order = question.get('question_order')
            is_required = question.get('is_required')
            survey_question = SurveyQuestion.objects.create(post_survey=post_survey,
                                                            survey_question_type_id=survey_question_type_id,
                                                            question_content=question_content,
                                                            question_order=question_order, is_required=is_required)

            survey_question_option_list = question.get('survey_question_option_list', [])
            for option in survey_question_option_list:
                question_option_value = option.get('question_option_value')
                question_option_order = option.get('question_option_order')
                SurveyQuestionOption.objects.create(survey_question=survey_question,
                                                    question_option_value=question_option_value,
                                                    question_option_order=question_option_order)

        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='create_post_invitation')
    @method_decorator(decorator=create_post_invitation, name='create_post_invitation')
    def create_post_invitation(self, request):
        account_id = request.data.get('account_id')
        post_content = request.data.get('post_content')

        post = Post.objects.create(post_content=post_content, account_id=account_id)

        event_name = request.data.get('event_name')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        PostInvitation.objects.create(post=post,
                                      event_name=event_name,
                                      start_time=start_time,
                                      end_time=end_time)
        return Response(status=status.HTTP_200_OK)


def get_queryset(self):
    queries = self.queryset
    keyword = self.request.query_params.get('keyword')

    if keyword:
        queries = queries.filter(post_content__icontains=keyword)

    account_id = self.request.query_params.get('account_id')
    if account_id:
        queries = queries.filter(account=account_id)

    return queries


# -Reaction-
class ReactionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = Reaction.objects.filter(active=True).all()
    serializer_class = ReactionSerializer
    pagination_class = MyPageSize


# -PostReaction-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class PostReactionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                          generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PostReaction.objects.select_related('account', 'post', 'reaction').filter(active=True).all()
    serializer_class = PostReactionSerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostReactionSerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePostReactionSerializer
        return self.serializer_class


# -Account-
@method_decorator(decorator=header_authorization, name='list')
# @method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class AccountViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Account.objects.select_related('role', 'user').filter(active=True).all()
    serializer_class = AccountSerializer
    pagination_class = MyPageSize
    parser_classes = [MultiPartParser, ]

    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        avatar_file = self.request.data.get('avatar')
        cover_avatar_file = self.request.data.get('cover_avatar')

        if avatar_file and cover_avatar_file:
            upload_avatar = cloudinary.uploader.upload(avatar_file)
            upload_cover_avatar = cloudinary.uploader.upload(cover_avatar_file)
            serializer.save(avatar=upload_avatar['secure_url'], cover_avatar=upload_cover_avatar['secure_url'])

        else:
            if avatar_file:
                upload_data = cloudinary.uploader.upload(avatar_file)
                serializer.save(avatar=upload_data['secure_url'])

            if cover_avatar_file:
                upload_data = cloudinary.uploader.upload(cover_avatar_file)
                serializer.save(cover_avatar=upload_data['secure_url'])

    def perform_update(self, serializer):
        avatar_file = self.request.data.get('avatar')
        cover_avatar_file = self.request.data.get('cover_avatar')

        if avatar_file and cover_avatar_file:
            upload_avatar = cloudinary.uploader.upload(avatar_file)
            upload_cover_avatar = cloudinary.uploader.upload(cover_avatar_file)
            serializer.save(avatar=upload_avatar['secure_url'], cover_avatar=upload_cover_avatar['secure_url'])

        else:
            if avatar_file:
                upload_data = cloudinary.uploader.upload(avatar_file)
                serializer.save(avatar=upload_data['secure_url'])

            if cover_avatar_file:
                upload_data = cloudinary.uploader.upload(cover_avatar_file)
                serializer.save(cover_avatar=upload_data['secure_url'])

    def get_permissions(self):
        if self.action in ['list', 'update', 'partial_update', 'destroy', 'get_posts_by_account']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    # Override lại để dùng cái Serializer create, update
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAccountSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateAccountSerializer
        return self.serializer_class

    @action(methods=['GET'], detail=True, url_path='posts')
    @method_decorator(decorator=header_authorization, name='get_posts_by_account')
    def get_posts_by_account(self, request, pk):
        posts = self.get_object().post_set.filter(active=True).all()
        return Response(PostSerializer(posts, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, url_path='invitation_groups')
    @method_decorator(decorator=header_authorization, name='get_invitation_groups_by_account')
    def get_invitation_groups_by_account(self, request, pk):
        # ManyToMany query ngược
        invitation_groups = self.get_object().invitationgroup_set.filter(active=True).all()
        return Response(InvitationGroupSerializer(invitation_groups, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    # Chỗ này chỉ dùng được method GET thôi, lạy anh Swagger giờ muốn truyền body không được
    # Nó kêu do Serializer lồng dữ quá không tạo được????
    # drf_yasg.errors.SwaggerGenerationError: cannot instantiate nested serializer as Parameter
    @action(methods=['GET'], detail=True, url_path='reacted_to_the_post')
    @method_decorator(decorator=params_for_account_reacted_to_the_post, name='reacted_to_the_post')
    def reacted_to_the_post(self, request, pk):
        post_id = request.query_params.get('post_id')
        post_reactions = PostReaction.objects.filter(account_id=pk)

        if post_id:
            post_reactions = post_reactions.filter(post_id=post_id)

        post_reaction_serializer = PostReactionSerializerForAccount(post_reactions, many=True,
                                                                    context={'request': request}).data

        reaction = False
        if post_reaction_serializer:
            reaction = True

        return Response({
            'reacted': reaction,
            'data': post_reaction_serializer
        }, status=status.HTTP_200_OK)

    # @action(methods=['POST'], detail=True, url_path='reacted_to_the_post')
    # def reacted_to_the_post(self, request, pk):
    #     list_post_id = request.data.get('list_post_id', [])
    #     list_post_id = [14, 5, 8]
    #     post_reactions_of_account = PostReaction.objects.filter(account_id=pk, post_id__in=list_post_id)
    #
    #     return Response(TempSerializer(post_reactions_of_account, many=True, context={'request': request}).data,
    #                     status=status.HTTP_200_OK)


# -AlumniAccount-
@method_decorator(decorator=header_authorization, name='list')
# @method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class AlumniAccountViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                           generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = AlumniAccount.objects.all()
    serializer_class = AlumniAccountSerializer

    # permission_classes = [permissions.IsAuthenticated]
    def get_permissions(self):
        if self.action in ['list', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]

    # Override lại để dùng cái Serializer create, update
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateAlumniAccountSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateAlumniAccountSerializer
        return self.serializer_class


# -PostImage-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class PostImageViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                       generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PostImage.objects.filter(active=True).all()
    serializer_class = PostImageSerializer
    pagination_class = MyPageSize
    parser_classes = [MultiPartParser, ]
    permission_classes = [permissions.IsAuthenticated]

    # def create(self, request, *args, **kwargs):
    #     response = super().create(request, *args, **kwargs)
    #     # image_file = self.request.data.get('post_image_url')
    #     # upload_data = cloudinary.uploader.upload(image_file)
    #     # # Thì ra đây là cách gán giá trị cho response NHƯNG không lưu db
    #     # response.data['post_image_url'] = upload_data['secure_url']
    #     data = {
    #         'response': response.data,
    #         # 'upload_cloudinary': upload_data['secure_url']
    #     }
    #
    #     return Response(data, status=status.HTTP_200_OK)

    # hàm này là override lại quá trình diễn ra trong lúc create
    def perform_create(self, serializer):
        image_file = self.request.data.get('post_image_url')
        if image_file:
            upload_data = cloudinary.uploader.upload(image_file)
            serializer.save(post_image_url=upload_data['secure_url'])

    def perform_update(self, serializer):
        image_file = self.request.data.get('post_image_url')
        if image_file:
            upload_data = cloudinary.uploader.upload(image_file)
            serializer.save(post_image_url=upload_data['secure_url'])

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostImageSerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePostImageSerializer
        return self.serializer_class


# -Comment-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class CommentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.filter(active=True).all()
    serializer_class = CommentSerializer
    pagination_class = MyPageSize
    parser_classes = [MultiPartParser, ]

    def perform_create(self, serializer):
        image_file = self.request.data.get('comment_image_url')
        if image_file:
            upload_data = cloudinary.uploader.upload(image_file)
            serializer.save(comment_image_url=upload_data['secure_url'])

    def perform_update(self, serializer):
        image_file = self.request.data.get('comment_image_url')
        if image_file:
            upload_data = cloudinary.uploader.upload(image_file)
            serializer.save(comment_image_url=upload_data['secure_url'])

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [CommentOwner()]
        elif self.action == 'destroy':
            return [CommentOwner()]
        else:
            return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCommentSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateCommentSerializer
        return self.serializer_class


# -PostInvitation-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class PostInvitationViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                            generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PostInvitation.objects.filter(active=True).all()
    serializer_class = PostInvitationSerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostInvitationSerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePostInvitationSerializer
        return self.serializer_class

    @action(methods=['GET'], detail=True, url_path='accounts')
    @method_decorator(decorator=header_authorization, name='accounts')
    def get_accounts(self, request, pk):
        accounts = self.get_object().accounts.filter(active=True).all()
        return Response(AccountSerializerForInvitationGroup(accounts, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='add_or_update_accounts')
    @method_decorator(decorator=add_or_update_accounts_from_post_invitation, name='add_or_update_accounts')
    def add_or_update_accounts(self, request, pk):
        try:
            post_invitation = self.get_object()
            list_account_id = request.data.get('list_account_id', [])
            accounts = Account.objects.filter(id__in=list_account_id)
            if len(accounts) != len(list_account_id):
                missing_ids = set(list_account_id) - set(accounts.values_list('id', flat=True))
                raise NotFound(f'Accounts with IDs {missing_ids} do not exist.')

            post_invitation.accounts.add(*accounts)
            post_invitation.save()

            return Response(PostInvitationSerializer(post_invitation).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            error_message = str(e)
            return Response({'error kìa: ': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['POST'], detail=True, url_path='delete_accounts')
    @method_decorator(decorator=delete_accounts_from_post_invitation, name='delete_account')
    def delete_account(self, request, pk):
        try:
            post_invitation = self.get_object()
            list_account_id = request.data.get('list_account_id', [])
            accounts = post_invitation.accounts.filter(id__in=list_account_id)
            if len(accounts) != len(list_account_id):
                missing_ids = set(list_account_id) - set(accounts.values_list('id', flat=True))
                raise NotFound(f'Accounts with IDs {missing_ids} do not exist.')

            post_invitation.accounts.remove(*accounts)
            post_invitation.save()

            return Response(PostInvitationSerializer(post_invitation).data, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            error_message = str(e)
            return Response({'error: ': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -PostSurvey-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class PostSurveyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                        generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PostSurvey.objects.filter(active=True).all()
    serializer_class = PostSurveySerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePostSurveySerializer
        if self.action in ['update', 'partial_update']:
            return UpdatePostSurveySerializer
        return self.serializer_class

    @action(methods=['GET'], detail=True, url_path='survey_question')
    @method_decorator(decorator=header_authorization, name='get_survey_questions')
    def get_survey_questions(self, request, pk):
        survey_questions = self.get_object().surveyquestion_set.filter(active=True).all()
        return Response(SurveyQuestionSerializer(survey_questions, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)

    # ERROR
    @action(methods=['POST'], detail=True, url_path='create_survey_questions')
    @method_decorator(decorator=warning_api, name='create_survey_questions')
    def create_survey_questions(self, request, pk):
        post_survey = self.get_object()

        # {
        #   "question_content": "What is your favorite color?",
        #   "is_required": true,
        #   "survey_question_type": "1"
        # }
        # Cannot assign "1": "SurveyQuestion.survey_question_type" must be a "SurveyQuestionType" instance
        # Thằng SurveyQuestion này không chịu cái id của survey_question_type
        # Do nó cần gửi cả 1 instance của object :)))
        # Thôi tách ra Srializer riêng cho ròi :)

        survey_questions = SurveyQuestion(question_content=request.data['question_content'],
                                          post_survey=post_survey,
                                          is_required=request.data['is_required'],
                                          survey_question_type=request.data['survey_question_type']
                                          )
        return Response(SurveyQuestionSerializer(survey_questions, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# -SurveyQuestion-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class SurveyQuestionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                            generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = SurveyQuestion.objects.filter(active=True).all()
    serializer_class = SurveyQuestionSerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSurveyQuestionSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateSurveyQuestionSerializer
        return self.serializer_class


# -SurveyQuestionOption-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class SurveyQuestionOptionViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView,
                                  generics.CreateAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = SurveyQuestionOption.objects.filter(active=True).all()
    serializer_class = SurveyQuestionOptionSerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSurveyQuestionOptionSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateSurveyQuestionOptionSerializer
        return self.serializer_class

    @action(methods=['GET'], detail=True, url_path='survey_answer')
    @method_decorator(decorator=header_authorization, name='get_survey_answer')
    def get_survey_answer(self, request, pk):
        survey_answers = self.get_object().survey_answers \
            .select_related('survey_question', 'survey_response') \
            .filter(active=True).all()

        return Response(
            SurveyAnswerSerializerForRelated(survey_answers, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK)

    # ManyToMany nhưng chiều này hơi cấn
    @action(methods=['POST'], detail=True, url_path='add_or_update_survey_answers')
    @method_decorator(decorator=add_or_update_survey_answer_to_survey_question_option,
                      name='add_or_update_survey_answers')
    @method_decorator(decorator=warning_api)
    def add_or_update_survey_answers(self, request, pk):
        try:
            survey_question_option = self.get_object()
            list_survey_answer_id = request.data.get('list_survey_answer_id', [])
            survey_answers = SurveyAnswer.objects.filter(id__in=list_survey_answer_id)
            if len(survey_answers) != len(list_survey_answer_id):
                missing_ids = set(list_survey_answer_id) - set(survey_answers.values_list('id', flat=True))
                raise NotFound(f"Survey Answer with IDs {missing_ids} do not exist.")

            survey_question_option.survey_answers.add(*survey_answers)
            survey_question_option.save()

            return Response(SurveyQuestionOptionSerializer(survey_question_option).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            error_message = str(e)
            return Response({'error kìa: ': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -SurveyResponse-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='destroy')
class SurveyResponseViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                            generics.DestroyAPIView):
    queryset = SurveyResponse.objects.filter(active=True).all()
    serializer_class = SurveyResponseSerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSurveyResponseSerializer
        return self.serializer_class


# -SurveyAnswer-
@method_decorator(decorator=header_authorization, name='list')
@method_decorator(decorator=header_authorization, name='create')
@method_decorator(decorator=header_authorization, name='retrieve')
@method_decorator(decorator=header_authorization, name='update')
@method_decorator(decorator=header_authorization, name='partial_update')
@method_decorator(decorator=header_authorization, name='destroy')
class SurveyAnswerViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView, generics.CreateAPIView,
                          generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = SurveyAnswer.objects.filter(active=True).all()
    serializer_class = SurveyAnswerSerializer
    pagination_class = MyPageSize
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSurveyAnswerSerializer
        if self.action in ['update', 'partial_update']:
            return UpdateSurveyAnswerSerializer
        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='add_or_update_survey_question_options')
    @method_decorator(decorator=add_or_update_survey_question_option_to_survey_answer,
                      name='add_or_update_survey_question_options')
    def add_or_update_survey_question_options(self, request, pk):
        try:
            survey_answer = self.get_object()
            list_survey_question_option_id = request.data.get('list_survey_question_option_id', [])
            survey_question_options = SurveyQuestionOption.objects.filter(id__in=list_survey_question_option_id)
            if len(survey_question_options) != len(list_survey_question_option_id):
                missing_ids = set(list_survey_question_option_id) - set(
                    survey_question_options.values_list('id', flat=True))
                raise NotFound(f"Survey Answer with IDs {missing_ids} do not exist.")

            survey_answer.surveyquestionoption_set.add(*survey_question_options)
            survey_answer.save()

            return Response(SurveyAnswerSerializer(survey_answer).data,
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            error_message = str(e)
            return Response({'error kìa: ': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -other views-

# -Email-
# Tại sao tách decor ra nó lại bị lỗi AttributeError: 'SendEmailView' object has no attribute 'data'
# Nhưng gắn @swagger_auto_schema trực tiếp thì không bị?
# Bí ẩn zậy!
# @method_decorator(decorator=send_email, name='post')
class SendEmailView(APIView):
    @staticmethod
    @swagger_auto_schema(
        request_body=EmailSerializer
    )
    def post(request, format=None):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']
            recipient_list = serializer.validated_data['recipient_list']

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

            return Response({'message': 'Email sent successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -Cloudinary-
class UploadView(APIView):
    parser_classes = (
        MultiPartParser,
        JSONParser,
    )

    @staticmethod
    def post(request):
        file = request.data.get('picture')

        upload_data = cloudinary.uploader.upload(file)
        return Response({
            'status': 'success',
            'data': upload_data,
        }, status=201)
