from odoo import api, fields, models


class AddNewLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    leave_validation_type = fields.Selection([
        ('no_validation', 'No Validation'),
        ('hr', 'By Time Off Officer'),
        ('manager', "By Employee's Manager"),
        ('both', "By Employee's Manager and Time Off Officer"),
        ('order_manager_to_hr', "Order Manager To HR")], default='hr', string='Leave Validation')
    # @api.onchange('leave_validation_type')
    # def onchange_leave_validation_type(self):
    #     if self.leave_validation_type == 'order_manger_to_hr':
    #         return {
    #             'req'
    #         }
