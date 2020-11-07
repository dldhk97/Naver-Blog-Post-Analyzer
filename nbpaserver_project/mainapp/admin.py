from django.contrib import admin
from .models import BlogInfo, AnalyzedInfo, MultimediaRatio, Dictionary, Feedback, BannedUser, RatioType, FeedbackType, DictionaryType

# Register your models here.
admin.site.register(BlogInfo)
admin.site.register(AnalyzedInfo)
admin.site.register(MultimediaRatio)
admin.site.register(Dictionary)
admin.site.register(Feedback)
admin.site.register(BannedUser)
admin.site.register(RatioType)
admin.site.register(FeedbackType)
admin.site.register(DictionaryType)