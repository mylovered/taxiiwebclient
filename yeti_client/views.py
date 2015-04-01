from multiprocessing import Process

from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.template import RequestContext

from forms import ConfigForm, PushStixIPForm, PushStixEmailForm, PushFileForm
from models import Config, ReceivedFile, Event, RECEIVED_FILES_DIR
from utils import check_request_file, parse_status_response


poll_timestamp = ''

@login_required
def index(request, file_form=None, stix_ip_form=None, stix_email_form=None):
    if request.is_ajax():
        template = "index_poll_ajax.html"
    else:
        template = "index.html"

    config = Config.objects.get()

    try:
        received_files = ReceivedFile.objects.all()
    except ObjectDoesNotExist:
        received_files = []

    return render(request, template,
        {
            'file_form': file_form or PushFileForm(),
            'stix_ip_form': stix_ip_form or PushStixIPForm(),
            'stix_email_form': stix_email_form or PushStixEmailForm(),
            'polling': config.polling,
            'poll_rate': config.pollRate * 1000,
            'received_files': received_files,
            'received_files_dir': RECEIVED_FILES_DIR,
            'poll_timestamp': config.poll_req_tstamp
        }, context_instance=RequestContext(request))

@login_required
def history(request):
    event_history = Event.objects.all()
    return render(request, 'history.html', {'event_history': event_history})

@login_required
def alerts(request):
    return render(request, 'alerts.html')

@login_required
@permission_required('user.is_superuser', raise_exception=True)
def settings(request):
    if request.method == 'POST':
        config = Config.objects.get()
        request.FILES['privFile'] = check_request_file('privFile', request, config.privFile)
        request.FILES['pubFile'] = check_request_file('pubFile', request, config.pubFile)
            
        config_form = ConfigForm(request.POST, request.FILES)
        
        if config_form.is_valid():
            config_form.save()
            config_form = ConfigForm(instance=Config.objects.get())
            messages.info(request, 'Settings saved')
        else:
            messages.info(request, 'Invalid form')
    else:
        config_form = ConfigForm(instance=Config.objects.get())

    return render(request, 'settings.html', {'config_form': config_form})

@login_required
def push_file(request):
    if request.method == 'POST':
        push_file_form = PushFileForm(request.POST, request.FILES)
        if push_file_form.is_valid():
            f = request.FILES['content_file']
            cb = push_file_form.get_content_block(f)

            config = Config.objects.get()
            resp = config.call_inbox(cb)
            config.push_event(request.user.username, resp.status_type, 'File: ' + f.name)
            messages.info(request, parse_status_response(resp))
        else:
            messages.info(request, 'Invalid form')
            return index(request, push_file_form=push_file_form)
    # end if

    return redirect('index')

@login_required
def push_stix_ip(request):
    if request.method == 'POST':
        stix_form = PushStixIPForm(request.POST)
        if stix_form.is_valid():
            cb = stix_form.get_content_block()
            config = Config.objects.get()
            resp = config.call_inbox(cb)
            config.push_event(request.user.username, resp.status_type,
                              '[STIX] IP List:\n' + request.POST['ip_list'] + '\nDescription:\n' + request.POST['desc'])
            messages.info(request, parse_status_response(resp))
        else:
            messages.info(request, 'Invalid form')
            return index(request, stix_ip_form=stix_form)
    # end if

    return redirect('index')

@login_required
def push_stix_email(request):
    if request.method == 'POST':
        stix_form = PushStixEmailForm(request.POST)
        if stix_form.is_valid():
            cb = stix_form.get_content_block()
            config = Config.objects.get()
            resp = config.call_inbox(cb)
            config.push_event(request.user.username, resp.status_type,
                              '[STIX] E-mail List:\n' + request.POST['email_list'] + '\nDescription:\n' + request.POST['desc'])
            messages.info(request, parse_status_response(resp))
        else:
            messages.info(request, 'Invalid form')
            return index(request, stix_email_form=stix_form)
    # end if

    return redirect('index')


polling_process = None

@login_required
def pull(request):
    global polling_process

    if request.method == 'POST':
        config = Config.objects.get()

        if not config.polling:
            polling_process = Process(target=config.poll_request)
            polling_process.start()
            config.polling = True
            config.save()
            messages.info(request, 'Polling started')
        else:
            polling_process.terminate()
            config.polling = False
            config.save()
            messages.info(request, 'Polling stopped')
    # end if

    return redirect('index')
