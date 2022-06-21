# login/admin.py
from django.contrib import admin
from .models import *
#admin.site.register([models.User,models.RawText,models.SelfReport,models.TagText,models.LabelClass,models.ActClass])

@admin.register(RawText)
class RawTextAdmin(admin.ModelAdmin):
    list_display = ['unique_id','example_id','sentence_id','speaker',
                    'sentence','label','normalized','type','drug_word',
                    'drug_pos','check_word','check_pos']
    search_fields = ['example_id']
    list_per_page = 20
    # list_filter = ['example_id']

@admin.register(SelfReport)
class SelfReportAdmin(admin.ModelAdmin):
    list_display = ['example_id','question','diagnose']
    search_fields = ['example_id']
    list_filter = ['diagnose']
    list_per_page = 20

@admin.register(LabelClass)
class LabelClassAdmin(admin.ModelAdmin):
    list_display = ['labelid','labelmeaning']

@admin.register(ActClass)
class ActClassAdmin(admin.ModelAdmin):
    list_display = ['id','aid','actid']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','name','password','start','end']
    search_fields = ['name']
    list_per_page = 20

@admin.register(TagText)
class TagTextAdmin(admin.ModelAdmin):
    list_display = ['id','example_id','unique_id','sentence_id','speaker',
                    'sentence','label','normalized','dialogue_act','report','reviewer','savedate']
    search_fields = ['reviewer']
    list_per_page = 40
