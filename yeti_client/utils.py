import logging


logger = logging.getLogger(__name__)

def check_request_file(name, request, cur_file):
    if request.FILES.get(name):
        logger.debug("Got a new " + name)
        return request.FILES.get(name)
    else:
        if request.POST.get(name + '-clear'):
            logger.debug("Clearing file " + name)
            return None
        elif cur_file:
            logger.debug("Using existing " + name)
            return cur_file

def parse_status_response(resp):
    return "ID: " + resp.message_id + ", Status Type: " + resp.status_type + ", Message: " + str(resp.message)
