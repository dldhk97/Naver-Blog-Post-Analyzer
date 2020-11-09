from .analyzer.lorem_analyzer import load_module as analyzer_load_module

def load_module():
    print('[SYSTEM][model_task] Start loading module.')

    response = {}
    response['task_type'] = 'load_module'
    
    try:
        analyzer_load_module()
        print('[SYSTEM][model_task] Load module successful.')
        
        response['success'] = 'True'
        response['message'] = 'Load module successful.'

    except Exception as e:
        print('[SYSTEM][model_task] Failed to load module.', e)
        response['success'] = 'False'
        response['message'] = 'Failed to load module.'

    return response