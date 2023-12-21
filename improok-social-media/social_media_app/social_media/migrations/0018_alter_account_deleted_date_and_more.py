# Generated by Django 4.2.7 on 2023-12-21 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0017_alter_account_deleted_date_alter_account_role_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alumniaccount',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='confirmstatus',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='invitationgroup',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='postimage',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='postinvitation',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='postreaction',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='postsurvey',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reaction',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='surveyanswer',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='surveyquestion',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='surveyquestionoption',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='surveyquestiontype',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='deleted_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
