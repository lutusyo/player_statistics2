from django.contrib import admin
from apps.medical_data.models import (MedicalVisit,MedicalAttachment,MedicalFollowUp,)

class MedicalAttachmentInline(admin.TabularInline):
    model = MedicalAttachment
    extra = 1

class MedicalFollowUpInline(admin.TabularInline):
    model = MedicalFollowUp
    extra = 1

@admin.register(MedicalVisit)
class MedicalVisitAdmin(admin.ModelAdmin):

    date_hierarchy = "date"
    list_display = ("date","player","team","visit_type","main_complaint","availability_status","training_session_status","attachment_count","follow_up_count",)
    list_filter = ("team","visit_type","main_complaint","availability_status","training_session_status","injury_status",)
    search_fields = ("player__name","player__name","working_diagnosis","therapy",)
    autocomplete_fields = ("player",)
    readonly_fields = ("created_at","updated_at",)
    inlines = [MedicalAttachmentInline,MedicalFollowUpInline,]

    def attachment_count(self, obj):

        return obj.attachments.count()

    attachment_count.short_description = "Files"

    def follow_up_count(self, obj):

        return obj.follow_ups.count()

    follow_up_count.short_description = "Follow-ups"


@admin.register(MedicalAttachment)
class MedicalAttachmentAdmin(admin.ModelAdmin):

    list_display = ("visit","description","uploaded_at",)
    search_fields = ("description",)

@admin.register(MedicalFollowUp)
class MedicalFollowUpAdmin(admin.ModelAdmin):

    list_display = ("visit","review_date","status",)
    list_filter = ("status",)
    date_hierarchy = "review_date"