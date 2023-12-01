# Generated by Django 4.2.7 on 2023-12-01 13:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True, null=True)),
                ('updated_date', models.DateField(auto_now=True, null=True)),
                ('deleted_date', models.DateField(auto_now=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('phone_number', models.CharField(max_length=255, null=True, unique=True)),
                ('date_of_birth', models.DateTimeField(null=True)),
                ('avatar', models.CharField(max_length=255, null=True)),
                ('cover_avatar', models.CharField(max_length=255, null=True)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AlumniAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True, null=True)),
                ('updated_date', models.DateField(auto_now=True, null=True)),
                ('deleted_date', models.DateField(auto_now=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('alumni_account_code', models.CharField(max_length=255)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='social_media.account')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ConfirmStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True, null=True)),
                ('updated_date', models.DateField(auto_now=True, null=True)),
                ('deleted_date', models.DateField(auto_now=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('confirm_status_value', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GroupAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True, null=True)),
                ('updated_date', models.DateField(auto_now=True, null=True)),
                ('deleted_date', models.DateField(auto_now=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_media.account')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvitationAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(auto_now_add=True, null=True)),
                ('updated_date', models.DateField(auto_now=True, null=True)),
                ('deleted_date', models.DateField(auto_now=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_media.account')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='alumniuser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='groupuser',
            name='invitation_group',
        ),
        migrations.RemoveField(
            model_name='groupuser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='invitationuser',
            name='post_invitation',
        ),
        migrations.RemoveField(
            model_name='invitationuser',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='invitationgroup',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='postimage',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='postinvitation',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='postreaction',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='postsurvey',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='reaction',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='surveyanswer',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='surveyansweroption',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='surveyquestion',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='surveyquestionoption',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='surveyquestiontype',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='surveyresponse',
            options={'ordering': ['-id']},
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='post',
            name='user',
        ),
        migrations.RemoveField(
            model_name='postreaction',
            name='user',
        ),
        migrations.RemoveField(
            model_name='surveyresponse',
            name='user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='account_status',
        ),
        migrations.RemoveField(
            model_name='user',
            name='avatar',
        ),
        migrations.RemoveField(
            model_name='user',
            name='cover_avatar',
        ),
        migrations.RemoveField(
            model_name='user',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
        migrations.AlterField(
            model_name='post',
            name='comment_lock',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='AccountStatus',
        ),
        migrations.DeleteModel(
            name='AlumniUser',
        ),
        migrations.DeleteModel(
            name='GroupUser',
        ),
        migrations.DeleteModel(
            name='InvitationUser',
        ),
        migrations.AddField(
            model_name='invitationaccount',
            name='post_invitation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_media.postinvitation'),
        ),
        migrations.AddField(
            model_name='groupaccount',
            name='invitation_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social_media.invitationgroup'),
        ),
        migrations.AddField(
            model_name='account',
            name='role',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.role'),
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.account'),
        ),
        migrations.AddField(
            model_name='post',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.account'),
        ),
        migrations.AddField(
            model_name='postreaction',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.account'),
        ),
        migrations.AddField(
            model_name='surveyresponse',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.account'),
        ),
        migrations.AddField(
            model_name='user',
            name='confirm_status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='social_media.confirmstatus'),
        ),
    ]
