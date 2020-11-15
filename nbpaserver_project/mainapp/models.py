from django.db import models

class BlogInfo(models.Model):
    id = models.AutoField(primary_key=True)
    blog_id = models.CharField(max_length=45)
    log_no = models.CharField(max_length=45)
    
    url = models.TextField()
    title = models.TextField()
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        id_str = str(self.id if self.id else '')
        return id_str + ', ' + self.blog_id + ', ' + self.log_no + ', ' + self.url + ', ' + self.title


class AnalyzedInfo(models.Model):
    id = models.AutoField(primary_key=True)
    blog_info = models.ForeignKey(BlogInfo, on_delete=models.CASCADE)
    
    lorem_percentage = models.FloatField(default=-1)
    tag_similarity = models.FloatField(default=-1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        id_str = str(self.id if self.id else '')
        return id_str + ', ' + self.blog_info.blog_id + ', ' + self.blog_info.log_no + ', ' + self.blog_info.title + ', ' + self.blog_info.url + ', ' + str(self.lorem_percentage) + ', ' + str(self.tag_similarity)

class MultimediaRatio(models.Model):
    id = models.AutoField(primary_key=True)
    ratio_type = models.ForeignKey('RatioType', on_delete=models.PROTECT)
    blog_info = models.ForeignKey(BlogInfo, on_delete=models.CASCADE)
    
    ratio = models.FloatField(default=-1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        id_str = str(self.id if self.id else '')
        return id_str + ', ' + str(self.ratio_type.name) + ', ' + str(self.blog_info.blog_id) + ', ' + str(self.ratio)

class Dictionary(models.Model):
    id = models.AutoField(primary_key=True)
    blog_info = models.ForeignKey(BlogInfo, on_delete=models.CASCADE)

    dictionary_type = models.ForeignKey('DictionaryType', on_delete=models.PROTECT)
    word = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        id_str = str(self.id if self.id else '')
        blog_info_id_str = str(self.blog_info.id if self.blog_info.id else '')
        return id_str + ', ' + blog_info_id_str + ', ' + self.dictionary_type.name + ', ' + self.word

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    blog_info = models.ForeignKey(BlogInfo, on_delete=models.CASCADE)
    
    ip = models.CharField(max_length=45)
    feedback_type = models.ForeignKey('FeedbackType', on_delete=models.PROTECT)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        id_str = str(self.id if self.id else '')
        blog_info_id_str = str(self.blog_info.id if self.blog_info.id else '')
        return id_str + ', ' + blog_info_id_str + ', ' + self.ip + ', ' + str(self.feedback_type.name) + ', ' + self.message

class BannedUser(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=45)
    
    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        id_str = str(self.id if self.id else '')
        return id_str + ', ' + self.ip + ', ' + self.reason + ', '  + str(self.created_at)

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