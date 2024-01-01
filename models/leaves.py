from odoo import models, fields, api, _


class LeavesLogicInherit(models.Model):
    _inherit = 'hr.leave'

    attachment_file = fields.Binary(string='Attachment File', attachment=True)
    # sick_leave_already_taken = fields.Boolean('Sick Leave Already Taken')
    # one_more_days_taken_sick_leave = fields.Boolean('One More Days Taken Sick Leave')
    is_it_sick_leave = fields.Boolean('Is It Sick Leave')

    def add_attachment_file(self):
        print('hello')

    @api.onchange('holiday_status_id')
    def _onchange_date(self):

        # print('hello')
        # records = self.env['hr.leave'].sudo().search([('holiday_status_id.name', '=', 'Sick Leave')])
        # for rec in records:
        #     if self.holiday_status_id.name == 'Sick Leave':
        #         if self.request_date_from and self.request_date_to:
        #             print('sick leave')
        #             if self.env.user.id == rec.create_uid.id:
        #                 if self.request_date_from.month == rec.request_date_to.month or self.request_date_to.month == rec.request_date_to.month:
        #                     print(self.env.user.name, 'create uid')
        #                     self.sick_leave_already_taken = True
        #                     print(rec.request_date_from.month, 'from month')
        #
        #                 else:
        #                     print('one')
        #                     self.sick_leave_already_taken = False
        #         # if self.number_of_days > 1:
        #         #     self.sick_leave_already_taken = True
        #         # else:
        #
        #         # else:
        #         #     print('two')
        #         #     self.sick_leave_already_taken = False
        #     else:
        #         print('three')
        #         self.sick_leave_already_taken = False

        # rec.is_same_month = record.date_field.month == current_month.month

        # print(rec.request_date_from.month, 'from month')
        # print(rec.request_date_to.month, 'to month')
        if self.holiday_status_id.name == 'Sick Leave':
            self.is_it_sick_leave = True
            # if self.number_of_days > 1:
            #     self.one_more_days_taken_sick_leave = True
            # else:
            #     self.one_more_days_taken_sick_leave = False
        else:
            self.is_it_sick_leave = False
