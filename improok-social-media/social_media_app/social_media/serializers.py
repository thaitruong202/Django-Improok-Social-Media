from rest_framework import serializers

from .models import Role, User, Post, Account, PostImage, InvitationGroup, Comment, ConfirmStatus, AlumniAccount, \
    Reaction, PostReaction, PostInvitation, PostSurvey, SurveyQuestion, SurveyQuestionOption, SurveyAnswer, \
    SurveyResponse


# -Role-
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


# -ConfirmStatus-
class ConfirmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfirmStatus
        fields = '__all__'


# -InvitationGroup-
class AccountSerializerForInvitationGroup(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(source='avatar')
    cover_avatar = serializers.SerializerMethodField(source='cover_avatar')

    def get_avatar(self, account):
        if account.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % account.avatar.name)
        return '/static/%s' % account.avatar.name

    def get_cover_avatar(self, account):
        if account.cover_avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % account.cover_avatar.name)
        return '/static/%s' % account.cover_avatar.name

    class Meta:
        model = Account
        fields = '__all__'


class CreateInvitationGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationGroup
        fields = ['invitation_group_name']


class UpdateInvitationGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationGroup
        fields = ['invitation_group_name']


class InvitationGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitationGroup
        fields = '__all__'


# -User-
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    # Cái này xài bên giao diện admin của django nó không băm :))) để mò thêm
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'first_name', 'last_name', 'email']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}  # Không có cho xem password :)

    # Cái này xài bên giao diện admin của django nó không băm :))) để mò thêm
    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


# -Post-
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_content', 'account']


class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['post_content', 'comment_lock']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


# -Reaction-
class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'


# -PostReaction-
class AccountSerializerForPostReaction(serializers.ModelSerializer):
    role = RoleSerializer()
    user = UserSerializer()

    class Meta:
        model = Account
        fields = ['id', 'phone_number', 'avatar', 'user', 'role']

    # Truy cập trường role_name trong trường Role và username trong User của Account (chỉ để hiển thị cho ĐẸP)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['role'] = representation['role']['role_name']
        representation['user'] = 'id:' + str(representation['user']['id']) + \
                                 '/username:' + representation['user']['username']
        return representation


class CreatePostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['reaction', 'post', 'account']


class UpdatePostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['reaction', 'post']


class PostReactionSerializer(serializers.ModelSerializer):
    account = AccountSerializerForPostReaction()
    reaction = ReactionSerializer()
    post = PostSerializer()

    class Meta:
        model = PostReaction
        fields = '__all__'


# -Account-

# Serializer dùng để tạo riêng
# Vì Cái AccountSerializer kia dùng để hiển thị đã serializer luôn các object bên phía ForeignKey rồi
# Lúc Deserializer lại thì phải trả cho nó cả object (đâu có điên)
# Nên cái CreateAccountSerializer này được ra đời
class CreateAccountSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    date_of_birth = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Account
        fields = ['phone_number', 'date_of_birth', 'avatar', 'cover_avatar', 'account_status', 'user', 'role']


class UpdateAccountSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    date_of_birth = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Account
        fields = ['phone_number', 'date_of_birth', 'avatar', 'cover_avatar', 'account_status', 'role']


class AccountSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField(source='avatar')
    cover_avatar = serializers.SerializerMethodField(source='cover_avatar')
    # Xài cái many=True này tốn tận 2 tới 4 câu query
    # để lấy role, user ra từ cái khóa ngoại
    # Qua bên views xài select_related() ngon hơn (foreign key) vì nó INNER_JOIN (debug toolbar check)
    role = RoleSerializer()
    user = UserSerializer()

    def get_avatar(self, account):
        if account.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % account.avatar.name)
        return '/static/%s' % account.avatar.name

    def get_cover_avatar(self, account):
        if account.cover_avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % account.cover_avatar.name)
        return '/static/%s' % account.cover_avatar.name

    class Meta:
        model = Account
        fields = '__all__'
        # fields = ['invitation_group_account', 'role', 'user', 'avatar', 'cover_avatar']


# Ở CreateAccountSerializer lỡ chỉnh date_of_birth thành Date chứ không phải DateTime nên lỗi :)))
# class AccountSerializer(CreateAccountSerializer):
#     avatar = serializers.SerializerMethodField(source='avatar')
#     cover_avatar = serializers.SerializerMethodField(source='cover_avatar')
#     group_account = InvitationGroupSerializer(many=True)  # Cái này Many To Many
#     # Xài cái many=True này tốn tận 2 tới 4 câu query
#     # để lấy role, user ra từ cái khóa ngoại
#     # Qua bên views xài select_related() ngon hơn (foreign key) vì nó INNER_JOIN (debug toolbar check)
#     role = RoleSerializer()
#     user = UserSerializer()
#
#     def get_avatar(self, account):
#         if account.avatar:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri('/static/%s' % account.avatar.name)
#         return '/static/%s' % account.avatar.name
#
#     def get_cover_avatar(self, account):
#         if account.cover_avatar:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri('/static/%s' % account.cover_avatar.name)
#         return '/static/%s' % account.cover_avatar.name
#
#     class Meta:
#         model = CreateAccountSerializer.Meta.model
#         fields = CreateAccountSerializer.Meta.fields + ['id', 'group_account', 'invitation_account']


# -AlumniAccount-
class CreateAlumniAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniAccount
        fields = ['alumni_account_code', 'account']


class UpdateAlumniAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniAccount
        fields = ['alumni_account_code']


class AlumniAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniAccount
        fields = '__all__'


# -PostImage-
class CreatePostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['post_image_url', 'post']


class UpdatePostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['post_image_url']  # Cái này lỏ rồi


class PostImageSerializer(serializers.ModelSerializer):
    post_image_url = serializers.SerializerMethodField(source='post_image_url')

    def get_post_image_url(self, post_image):
        if post_image.post_image_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % post_image.post_image_url.name)
        return '/static/%s' % post_image.post_image_url.name

    class Meta:
        model = PostImage
        fields = '__all__'


# -Comment-
class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_content', 'comment_image_url', 'account', 'post']


class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_content', 'comment_image_url']


class CommentSerializer(serializers.ModelSerializer):
    comment_image_url = serializers.SerializerMethodField(source='comment_image_url')

    def get_comment_image_url(self, comment):
        if comment.comment_image_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri('/static/%s' % comment.comment_image_url.name)
        return '/static/%s' % comment.comment_image_url.name

    class Meta:
        model = Comment
        fields = '__all__'


# -PostInvitation-
class CreatePostInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostInvitation
        fields = ['event_name', 'start_time', 'end_time', 'post']


class UpdatePostInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostInvitation
        fields = ['event_name', 'start_time', 'end_time']


class PostInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostInvitation
        fields = '__all__'


# -PostSurvey-
class CreatePostSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostSurvey
        fields = ['post_survey_title', 'start_time', 'end_time', 'post']


class UpdatePostSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostSurvey
        fields = ['post_survey_title', 'start_time', 'end_time', 'is_closed']


class PostSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostSurvey
        fields = '__all__'


# -SurveyQuestion-

class CreateSurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = ['is_required', 'question_content', 'question_order', 'post_survey', 'survey_question_type']


class UpdateSurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        # survey_question_type có nên cho đổi sau khi đăng bài không ta?
        # Vì nếu đổi từ dạng multi choice về input text thì phải hủy hết các lựa chọn (SurveyQuestionOption)
        fields = ['is_required', 'question_content', 'question_order', 'survey_question_type']


class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = '__all__'


# -SurveyQuestionOption-
class CreateSurveyQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestionOption
        fields = ['question_option_value', 'question_option_order', 'survey_question']


class UpdateSurveyQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestionOption
        fields = ['question_option_value', 'question_option_order']


class SurveyQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestionOption
        fields = '__all__'


# -SurveyResponse-

class CreateSurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = ['account', 'post_survey']


class SurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyResponse
        fields = '__all__'


# -SurveyAnswer-

class CreateSurveyAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyAnswer
        fields = ['question_option_value', 'survey_question', 'survey_response']


class UpdateSurveyAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyAnswer
        fields = ['question_option_value']


# Serializer zậy cho client fetch nhìn đỡ bị lú relationship db
# cái này nằm trong cái dưới
class PostSurveySerializerForSurveyQuestion(serializers.ModelSerializer):
    class Meta:
        model = PostSurvey
        fields = ['id', 'post_survey_title']


# Rồi cái này cũng nằm trong cái dưới
class SurveyQuestionSerializerSerializerForSurveyAnswer(serializers.ModelSerializer):
    post_survey = PostSurveySerializerForSurveyQuestion()  # nó nè

    class Meta:
        model = SurveyQuestion
        fields = ['question_content', 'post_survey', 'survey_question_type']


class SurveyAnswerSerializerForRelated(serializers.ModelSerializer):
    survey_question = SurveyQuestionSerializerSerializerForSurveyAnswer()  # Nó nè

    class Meta:
        model = SurveyAnswer
        fields = '__all__'


class SurveyAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyAnswer
        fields = '__all__'


# -other serializer-
# -Email-
class EmailSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    subject = serializers.CharField(max_length=100)
    message = serializers.CharField()
    recipient_list = serializers.ListField(child=serializers.EmailField())
