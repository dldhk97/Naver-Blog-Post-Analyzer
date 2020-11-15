from ... import models

# 크롤러에서 사용하는 BlogPost 객체를 BlogInfo, BlogInfo배열, Dictionary배열로 분리하여 반환
def blog_post_to_django_model(blog_post):
    hyperlink_dict = []
    tag_dict = []

    try:
        blog_info = models.BlogInfo()
        blog_info.blog_id = blog_post._blog_id
        blog_info.log_no = blog_post._log_no
        blog_info.url = blog_post._url
        blog_info.title = blog_post._title
        blog_info.body = blog_post._body

        for l in blog_post._hyperlinks:
            hyperlink = models.Dictionary()
            hyperlink.blog_info = blog_info
            hyperlink.dictionary_type = models.DictionaryType.objects.filter(name='hyperlink')[0]
            hyperlink.word = l
            hyperlink_dict.append(hyperlink)

        for t in blog_post._tags:
            tag = models.Dictionary()
            tag.blog_info = blog_info
            tag.dictionary_type = models.DictionaryType.objects.filter(name='hashtag')[0]
            tag.word = t
            tag_dict.append(tag)

        return blog_info, hyperlink_dict, tag_dict
    except Exception as e:
        print('[SYSTEM][model_converter] Failed to convert blog_post to blog_info, dictionarys\n' + blog_info.title + ', ' + blog_info.url, e)
        if 'list index out of range' in e.args[0]:
            print('[CRITICAL_ERROR][DB] Is dictionaryType table empty? Check the type tables.')
        
    return None, None, None

def dictionary_to_django_model(blog_info, word, dictionary_type):
    dictionary = models.Dictionary()
    dictionary.blog_info = blog_info
    dictionary.dictionary_type = dictionary_type
    dictionary.word = word

    return dictionary

def analyzed_info_to_django_model(blog_info, lorem_percentage, tag_similarity):
    analyzed_info = models.AnalyzedInfo()
    analyzed_info.blog_info = blog_info
    analyzed_info.lorem_percentage = lorem_percentage
    analyzed_info.tag_similarity = tag_similarity

    return analyzed_info

def multimedia_ratio_to_django_model(blog_info, ratio, ratio_type):
    multimedia_ratio = models.MultimediaRatio()
    multimedia_ratio.blog_info = blog_info
    multimedia_ratio.ratio = ratio
    multimedia_ratio.ratio_type = ratio_type
    
    return multimedia_ratio