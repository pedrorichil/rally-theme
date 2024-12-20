from ._anvil_designer import MainTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import State
from ..ExpenseDashboard import ExpenseDashboard
from ..SummaryPlots import SummaryPlots

class Main(MainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    self.switch_to_dashboard(None)
    if State.user['role'] == 'admin':
      self.separator_label_2.visible = True
      self.summary_btn.visible = True
      self.summary_btn.enabled = True

  def log_out_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    open_form('Login')

  def switch_to_dashboard(self, status):
    self.content_panel.clear()
    self.content_panel.add_component(ExpenseDashboard(status=status))
  
  def pendingappr_btn_click(self, **event_args):
    self.switch_to_dashboard('pending')

  def pendingreimb_btn_click(self, **event_args):
    self.switch_to_dashboard('approved')

  def pastexp_btn_click(self, **event_args):
    self.switch_to_dashboard(q.not_("pending", "approved"))

  def allexp_btn_click(self, **event_args):
    self.switch_to_dashboard(None)

  def summary_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(SummaryPlots())
  














