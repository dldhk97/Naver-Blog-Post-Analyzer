from django.http import JsonResponse

# for Forbidden(CSRF cookie not set)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
def get_analyzed_info(request):
    print('Request received from client')
    
    req = request.POST
    name = req['name']
    birth = req['birth']
    
    print('received name : ' + name)
    print('received birth : ' + birth)

    # send data to client 
    return JsonResponse({'world': 'earth', 'status': 'hello'})