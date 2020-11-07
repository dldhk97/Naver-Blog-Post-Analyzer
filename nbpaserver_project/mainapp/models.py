from django.db import models

class BlogInfo(models.Model):
    blog_info_id = models.AutoField(primary_key=True)
    blog_id = models.CharField(max_length=45)
    log_no = models.CharField(max_length=45)
    
    url = models.TextField()
    title = models.TextField()
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.blog_info_id) + ', ' + self.blog_id + ', ' + self.log_no + ', ' + self.url + ', ' + self.title


class AnalyzedInfo(models.Model):
    analyzed_info_id = models.AutoField(primary_key=True)
    blog_info = models.ForeignKey(BlogInfo, on_delete=models.CASCADE)
    
    lorem_percentage = models.FloatField()
    tag_similarity = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.analyzed_info_id) + ', ' + self.blog_info.blog_id + ', ' + self.blog_info.log_no + ', ' + self.blog_info.title + ', ' + self.blog_info.url + ', ' + str(self.lorem_percentage) + ', ' + str(self.tag_similarity)

class MultimediaRatio(models.Model):
    multimedia_ratio_id = models.AutoField(primary_key=True)
    ratio_type = models.ForeignKey('RatioType', on_delete=models.PROTECT)
    analyzed_info = models.ForeignKey(AnalyzedInfo, on_delete=models.CASCADE)
    
    ratio = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.multimedia_ratio_id) + ', ' + str(self.ratio_type.name) + ', ' + str(self.analyzed_info.analyzed_info_id) + ', ' + str(self.ratio)

class Dictionary(models.Model):
    dictionary_id = models.AutoField(primary_key=True)
    blog_info = models.ForeignKey(BlogInfo, on_delete=models.CASCADE)

    dictionary_type = models.ForeignKey('DictionaryType', on_delete=models.PROTECT)
    word = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.dictionary_id) + ', ' + str(self.blog_info.blog_info_id) + ', ' + self.dictionary_type.name + ', ' + self.word

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    blog_info = models.ForeignKey(BlogInfo, on_delete=models.CASCADE)
    
    ip = models.CharField(max_length=45)
    feedback_type = models.ForeignKey('FeedbackType', on_delete=models.PROTECT)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.feedback_id) + ', ' + str(self.blog_info.blog_info_id) + ', ' + self.ip + ', ' + str(self.feedback_type.name) + ', ' + self.message

class BannedUser(models.Model):
    banned_user_id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=45)
    
    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.banned_user_id) + ', ' + self.ip + ', ' + self.reason + ', '  + str(self.created_at)

class RatioType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return str(self.id) + ', ' + self.name

class DictionaryType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return str(self.id) + ', ' + self.name

class FeedbackType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)

    def __str__(self):
        return str(self.id) + ', ' + self.name