from ..crawler import naverblogcrawler

def bloginfo_task(task):
    '''
    URL을 받으면 크롤링하여 BlogPost 객체로 반환
    '''
    blog_post = naverblogcrawler.pasre_blog_post(task._url)
    return [task, blog_post]