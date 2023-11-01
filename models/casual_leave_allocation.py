from odoo import fields, models, _, api


class CasualLeaveAllocation(models.Model):
    _inherit = 'hr.employee'

    joining_date_cus = fields.Date(string='Date Of Joining')
    