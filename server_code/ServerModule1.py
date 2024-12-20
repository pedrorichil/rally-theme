import anvil.email
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.pdf
from datetime import datetime

@anvil.server.callable(require_user=True)
def get_user_expenses(status=None):
  d = {}
  if anvil.users.get_user()['role'] != 'admin':
    d['submitted_by'] = anvil.users.get_user()
  if status != None:
    d['status'] = status
  return app_tables.expenses.search(tables.order_by('created', ascending=False), **d)

@anvil.server.callable(require_user=True)
def add_expense(expense_dict):
  app_tables.expenses.add_row(created=datetime.now(), status="pending", submitted_by=anvil.users.get_user(), **expense_dict)

def is_admin(user):
  return user['role'] == 'admin'

@anvil.server.background_task
def send_email(user, message):
  anvil.email.send(to=user, from_name="Expenses App", subject="Your expense has been updated", html=message)

@anvil.server.callable(require_user=is_admin)
def change_status(row, status):
  old_status = row['status']
  user = row['submitted_by']['email']
  message = f"<p>Hi, {user},</p><p>The status of your expense ('{row['description']}') changed from <b>{old_status}</b> to <b>{status}</b>.</p><p>Visit the <a href={anvil.server.get_app_origin()}>app</a> to learn more details.</p>"
  row.update(status=status)
  anvil.server.launch_background_task('send_email', user=user, message=message)

@anvil.server.callable(require_user=is_admin)
def reject(row, message):
  change_status(row, 'rejected')
  row.update(reject_message=message)

@anvil.server.callable(require_user=is_admin)
def get_status_data():
  status_data = [x['status'] for x in app_tables.expenses.search()]
  labels = list(set(status_data))
  values = []
  for l in labels:
    values.append(status_data.count(l))
  return labels, values

@anvil.server.callable(require_user=is_admin)
def get_status_amount_data():
  data = app_tables.expenses.search(status=q.not_("pending", "rejected"))
  status_data = [x['status'] for x in data]
  amount_data = [x['amount'] for x in data]
  return status_data, amount_data
  
@anvil.server.callable(require_user=is_admin)
def get_dates_data():
  dates = [x['created'].date() for x in app_tables.expenses.search()]
  unique_dates = sorted(set(dates))
  qts = []
  for d in unique_dates:
    qts.append(dates.count(d))
  return unique_dates, qts

@anvil.server.callable(require_user=is_admin)
def create_summary_pdf():
  return anvil.pdf.render_form('SummaryPlots')

  
