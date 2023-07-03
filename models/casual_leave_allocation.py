from odoo import fields, models, _, api


class CasualLeaveAllocation(models.Model):
    _inherit = 'hr.employee'

    joining_date_cus = fields.Date(string='Date Of Joining')

    @api.onchange('joining_date_cus')
    def joining_date_compute(self):
        allocation = self.env['hr.contract'].search([])

        self.joining_date_cus = self.joining_date

        print('hi', self.joining_date_cus)
        # allocation = self.env['hr.leave.allocation'].create({
        #     'employee_id': self.id
        # })
        # res = super(CasualLeaveAllocation, self).create()
        # return res