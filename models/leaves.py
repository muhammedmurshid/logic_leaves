from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta


class LeavesLogicInherit(models.Model):
    _inherit = 'hr.leave'

    attachment_file = fields.Binary(string='Attachment File (150 KB)', attachment=True)
    # sick_leave_already_taken = fields.Boolean('Sick Leave Already Taken')
    # one_more_days_taken_sick_leave = fields.Boolean('One More Days Taken Sick Leave')
    is_it_sick_leave = fields.Boolean('Is It Sick Leave')
    is_it_old_day = fields.Boolean('Is It Old Day')
    note = fields.Text(readonly=1, string='Note', default='Departing without obtaining approval from both HR and the Head will be deemed as Leave Without Pay (LOP), except in cases of emergencies.')

    @api.onchange('request_date_from')
    def _compute_get_time_of_manager(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('hr_holidays.group_hr_holidays_user'):
            self.is_this_time_off_manager = True
        else:
            self.is_this_time_off_manager = False

    is_this_time_off_manager = fields.Boolean('Is This Time Off Manager', compute='_compute_get_time_of_manager')

    @api.onchange('request_date_from', 'request_date_to')
    def _onchange_request_date(self):
        today = fields.Date.today()
        yesterday = self.request_date_to + timedelta(days=1)
        print(today, 'today')
        print(yesterday, 'yesterday')
        print(self.request_date_from, 'from')
        print(self.request_date_to, 'to')
        if self.is_this_time_off_manager == False:
            if yesterday == today or self.request_date_from >= today or self.request_date_to >= today:
                self.is_it_old_day = False
            else:
                if self.request_date_from and self.request_date_to:
                    if self.request_date_from < today or self.request_date_to < today:
                        self.is_it_old_day = True
                    else:
                        self.is_it_old_day = False


    @api.model
    def create(self, vals):
        print(vals.get('is_it_old_day'), 'vals')
        print(self,'self')
        # return super(LeavesLogicInherit, self).create(vals)
        if vals.get('is_it_old_day'):
            if vals.get('is_it_old_day') == True:
                print('is old day')
                raise ValidationError(_('This date is invalid for leave request due to being in the past.'))
            else:
                print('not old day')
        return super(LeavesLogicInherit, self).create(vals)

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
