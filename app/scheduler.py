
from config import db_url
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.slack.actions import send_INFO_message_to_slack_channel
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_EXECUTED

scheduler = BackgroundScheduler(executors={'default': {'type': 'threadpool', 'max_workers': 50}})
scheduler.add_jobstore('sqlalchemy', url= db_url)
logs_channel_id = "C06FTS38JRX"

if scheduler.state != 1:
    print('-----Scheduler started-----')
    scheduler.start()
    

def job_executed(event): 
    job_id = str(event.job_id).capitalize()
    print(f'\n{job_id} was executed successfully at {event.scheduled_run_time}, response: {event.retval}')
    
def job_error(event):
    job_id = str(event.job_id).capitalize()
    message = f'An error occured in {job_id}, response: {event.retval}'
    send_INFO_message_to_slack_channel(channel_id=logs_channel_id, 
                                       title_message="Error executing AI Alpha Bots", 
                                       sub_title="Response", 
                                       message=message)
    print(message)
   
def job_max_instances_reached(event): 
    job_id = str(event.job_id).capitalize()
    message = f'Maximum number of running instances reached, *Upgrade* the time interval for {job_id}'
    send_INFO_message_to_slack_channel(channel_id=logs_channel_id, 
                                       title_message="Error executing AI Alpha Bots", 
                                       sub_title="Response", 
                                       message=message)
    print(message)
  

   
scheduler.add_listener(job_error, EVENT_JOB_ERROR)
scheduler.add_listener(job_max_instances_reached, EVENT_JOB_MAX_INSTANCES)
scheduler.add_listener(job_executed, EVENT_JOB_EXECUTED)