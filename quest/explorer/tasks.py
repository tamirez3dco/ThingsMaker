from celery.task import task
from explorer.helper.server_manager import ServerManager
from explorer.explore.controller import Base as Controller
from explorer.explore.renderer import Renderer

#exploration renderer tasks
@task()
def request_images(params):
    renderer = Renderer()
    renderer.request_images(params)

@task()
def get_ready_images():
    renderer = Renderer()
    renderer.get_ready_images()

#exploration controller tasks
@task()
def send_deep(children, r1, r2):
    controller = Controller(r1, r2)
    controller._send_deep(children)

@task()
def send_jobs(definition, uuids, root, params, material, explore_type, text, base_models=None, param_index=None):
    #return True
    controller = Controller(material, explore_type)
    controller._send_jobs(definition, uuids, root, params, text, base_models=base_models,param_index=param_index)

@task()
def send_missing_jobs(items):
    controller = Controller()
    controller._send_missing_jobs(items)
    
@task()
def send_deep_jobs(items):
    controller = Controller()
    controller._send_deep_jobs(items)
    
#server management tasks
@task()
def wakeup_servers(manual):
    manager = ServerManager()
    manager.wake_up(manual)

@task()
def manage_servers():
    manager = ServerManager()
    manager.manage()

@task()
def send_background_items():
    controller = Controller()  
    controller.send_background_items()
    
@task()
def check_3dm(definitions):
    for definition in definitions:
        definition.check_3dm()