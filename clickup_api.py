import os
from pyclickup import ClickUp
from dotenv import load_dotenv
from datetime import datetime, timezone
import time

load_dotenv()

def pretty_print(task):
    start_date = task.start_date.date() if task.start_date else 'no start date'
    due_date = task.due_date.date() if task.due_date else 'no due date'
    text = f'''
❇️ **{task.name}** | 📅 {start_date} - {due_date} | ✍️ {task.status.status.capitalize()}'''
    return text

def sort_date(dt):
    return 1e10 if not dt.start_date else datetime.timestamp(dt.start_date)

class MyClickUp:
    def __init__(self, token):
        self.token = token 
        self.clickup = ClickUp(self.token)
        self.tasks = self.clickup.teams[0].spaces[-1].\
            projects[0].lists[0].get_all_tasks(include_closed=False)

    def sync(self):
        self.tasks = self.clickup.teams[0].spaces[-1].\
            projects[0].lists[0].get_all_tasks(include_closed=False)

    def get_tasks_by_date(self, date):
        self.sync()
        res = []
        for task in self.tasks:
            if task.start_date and task.due_date:
                if date.date() >= task.start_date.date() \
                    and date.date() <= task.due_date.date():
                    res.append(task)
        return [pretty_print(t) for t in sorted(res, key=sort_date)]
    
    def get_tasks_by_person(self, name):
        self.sync()
        res = []
        for task in self.tasks:
            if task.status.status == name:
                res.append(task)
        return [pretty_print(t) for t in sorted(res, key=sort_date)]
    
    def get_tasks_in_future(self, date):
        self.sync()
        res = []
        for task in self.tasks:
            if task.start_date and task.due_date:
                if date.date() < task.start_date.date():
                    res.append(task)
        return [pretty_print(t) for t in sorted(res, key=sort_date)]

if __name__ == '__main__':
    CLICKUP_TOKEN = os.getenv('CLICKUP_TOKEN')
    m = MyClickUp(CLICKUP_TOKEN)
    # res = m.get_tasks_by_date(datetime.now(timezone.utc))
    res = m.get_tasks_in_future(datetime.now(timezone.utc))
    print(res)

