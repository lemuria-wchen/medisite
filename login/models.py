from django.db import models
import django.utils.timezone as timezone


# Create your models here.
class User(models.Model):
    id = models.AutoField(verbose_name='用户序号', unique=True, primary_key=True)
    name = models.CharField(verbose_name='用户名', max_length=128)
    password = models.CharField(verbose_name='用户密码', max_length=256)
    start = models.IntegerField(verbose_name='开始序号')
    end = models.IntegerField(verbose_name='结束序号')

    def __str__(self):
        return self.name


class RawText(models.Model):
    unique_id = models.CharField(verbose_name='样本句子序号', max_length=20, unique=True, primary_key=True)
    example_id = models.IntegerField(verbose_name='样本序号')
    sentence_id = models.IntegerField(verbose_name='句子序号')
    speaker = models.TextField(verbose_name='对话人')
    sentence = models.TextField(verbose_name='对话文本', null=True)
    label = models.CharField(verbose_name='预设标签', max_length=300, null=True)
    normalized = models.CharField(verbose_name='归一化症状标签', max_length=128, null=True)
    type = models.CharField(verbose_name='症状判断', max_length=128, null=True)
    drug_word = models.CharField(verbose_name='药品判断', max_length=128, null=True)
    drug_pos = models.CharField(verbose_name='药品位置', max_length=128, null=True)
    check_word = models.CharField(verbose_name='检查判断', max_length=128, null=True)
    check_pos = models.CharField(verbose_name='检查位置', max_length=128, null=True)

    def __str__(self):
        return self.sentence


class SelfReport(models.Model):
    example_id = models.IntegerField(verbose_name='样本序号', unique=True, primary_key=True)
    question = models.TextField(verbose_name='咨询问题')
    diagnose = models.TextField(verbose_name='诊断结果')

    def __str__(self):
        return self.diagnose


class TagText(models.Model):
    id = models.AutoField(verbose_name='记录序号', unique=True, primary_key=True)
    example_id = models.IntegerField(verbose_name='样本序号')
    unique_id = models.CharField(verbose_name='样本句子序号', max_length=128)
    sentence_id = models.IntegerField(verbose_name='句子序号')
    speaker = models.TextField(verbose_name='对话人')
    sentence = models.TextField(verbose_name='对话文本', null=True)
    label = models.CharField(verbose_name='标签', max_length=300, null=True)
    normalized = models.CharField(verbose_name='所有归一化标签', max_length=128, null=True)
    type = models.CharField(verbose_name='所有归一化标签特征', max_length=128, null=True)
    dialogue_act = models.CharField(verbose_name='话语行为', max_length=128, default='其他', null=True)
    report = models.TextField(verbose_name='诊断报告', null=True)
    reviewer = models.IntegerField(verbose_name='用户id')
    savedate = models.DateTimeField('保存日期', default=timezone.now)

    def __str__(self):
        return self.label


class LabelClass(models.Model):
    labelid = models.IntegerField(verbose_name='BIO类别')
    labelmeaning = models.TextField(verbose_name='BIO含义')

    def __str__(self):
        return self.labelid


class ActClass(models.Model):
    aid = models.TextField(verbose_name='ACT类别')
    actid = models.TextField(verbose_name='话语行为类别')

    def __str__(self):
        return self.actid
