from odoo import api, fields, models, _
import requests
from odoo.exceptions import UserError

class LeaveAllocationInheritance(models.Model):
    _inherit = 'hr.leave.allocation'

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('head_approve', 'Head Approval'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, tracking=True, copy=False, default='confirm',
        help="The status is set to 'To Submit', when an allocation request is created." +
             "\nThe status is 'To Approve', when an allocation request is confirmed by user." +
             "\nThe status is 'Refused', when an allocation request is refused by manager." +
             "\nThe status is 'Approved', when an allocation request is approved by manager.")

    @api.model
    def create(self, values):
        print('leave allocation testing')
        head_number = self.env['hr.employee'].sudo().search([('id','=',values.get('employee_id'))])
        print(head_number.parent_id.mobile_phone, 'head number')
        mobile = str(head_number.parent_id.mobile_phone)
        user = "Manager"
        type = "Leave Allocation"
        message_approved = "Hi " + user + ", an employee has requested " + type + " in Logic HRMS. For more details login to https://corp.logiceducation.org"
        dlt_approved = '1107168689563797302'

        url = "http://sms.mithraitsolutions.com/httpapi/httpapi?token=adf60dcda3a04ec6d13f827b38349609&sender=LSMKCH&number=" + str(
            mobile) + "&route=2&type=Text&sms=" + message_approved + "&templateid=" + dlt_approved

        # A GET request to the API
        response = requests.get(url)
        response_json = response.json()
        print(self.state, 'state')
        values['state'] = 'head_approve'
        return super(LeaveAllocationInheritance, self).create(values)

    def action_head_approval(self):
        print(self.employee_id.parent_id.user_id.id, 'yes')
        print(self.env.user.id, 'user')
        if self.env.user.id != self.employee_id.parent_id.user_id.id:
            raise UserError(_('Only Manager can approve this leave.'))
        else:
            self.state = 'confirm'

        # self.state = 'confirm'

    def action_head_reject(self):
        if self.env.user.id != self.employee_id.parent_id.user_id.id:
            raise UserError(_('Only Manager can approve this leave.'))
        else:
            self.state = 'refuse'


    def action_mark_as_draft_head(self):

        self.state = 'draft'

