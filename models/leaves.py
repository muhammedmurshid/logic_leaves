from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import requests
from pytz import timezone, UTC


class LeavesLogicInherit(models.Model):
    _inherit = 'hr.leave'

    attachment_file = fields.Binary(string='Attachment File (150 KB)', attachment=True)
    # sick_leave_already_taken = fields.Boolean('Sick Leave Already Taken')
    # one_more_days_taken_sick_leave = fields.Boolean('One More Days Taken Sick Leave')
    is_it_sick_leave = fields.Boolean('Is It Sick Leave')
    is_it_old_day = fields.Boolean('Is It Old Day')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('head_approve', 'Head Approval'),
        # YTI This state seems to be unused. To remove
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False,
        help="The status is set to 'To Submit', when a time off request is created." +
             "\nThe status is 'To Approve', when time off request is confirmed by user." +
             "\nThe status is 'Refused', when time off request is refused by manager." +
             "\nThe status is 'Approved', when time off request is approved by manager.")

    note = fields.Text(readonly=1, string='Note',
                       default='Departing without obtaining approval from both HR and the Head will be deemed as Leave Without Pay (LOP), except in cases of emergencies.')

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
        yesterday = today - timedelta(days=1)
        if self.request_date_from and self.request_date_to:
            if self.is_this_time_off_manager == False:
                print('tru value')
                if yesterday == self.request_date_from or yesterday == self.request_date_to or self.request_date_from >= today or self.request_date_to >= today:
                    self.is_it_old_day = False
                else:
                    if self.request_date_from and self.request_date_to:
                        if self.request_date_from < today or self.request_date_to < today:
                            self.is_it_old_day = True
                        else:
                            self.is_it_old_day = False
        else:
            print('false value')

    @api.model
    def create(self, vals):
        print(vals.get('is_it_old_day'), 'vals')
        # print(vals.holiday_status_id.leave_validation_type, 'leave validation type')
        print(vals['holiday_status_id'], 'self')
        print(vals['employee_id'], 'values')
        # return super(LeavesLogicInherit, self).create(vals)
        if vals.get('is_it_old_day'):
            if vals.get('is_it_old_day') == True:
                print('is old day')
                raise ValidationError(_('This date is invalid for leave request due to being in the past.'))
            else:
                print('not old day')
        leaves_type = self.env['hr.leave.type'].search([('id', '=', vals.get('holiday_status_id'))])
        if leaves_type.leave_validation_type == 'order_manager_to_hr':
            mob = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])
            print(mob.parent_id.mobile_phone, 'mobile')
            if not mob.parent_id.mobile_phone:
                raise ValidationError(_('Please add mobile number of Head of Department.'))
            else:
                head_number = mob.parent_id.mobile_phone
                print(head_number, 'head_number')
                user = 'Manager'
                #
                #     # print(response_json)
                message_applied = "Hi " + user + ", an employee has requested leave in Logic HRMS. For more details login to https://corp.logiceducation.org"
                dlt_applied = '1107168381905841814'
                url = "http://sms.mithraitsolutions.com/httpapi/httpapi?token=adf60dcda3a04ec6d13f827b38349609&sender=LSMKCH&number=" + head_number + "&route=2&type=Text&sms=" + message_applied + "&templateid=" + dlt_applied
                response = requests.get(url)

                response_json = response.json()
                emp_id = vals['employee_id']
                parent_id = self.env['hr.employee'].search([('id', '=', emp_id)])
                user = self.env['res.users'].search([('id', '=', parent_id.parent_id.user_id.id)])
                self.activity_schedule(
                    'hr_holidays.mail_act_leave_head_approval',
                    user_id=user.id, )
                print(user.name, 'manager name')
                self.activity_update()
            vals['state'] = 'head_approve'

        return super(LeavesLogicInherit, self).create(vals)

    def activity_update(self):
        to_clean, to_do = self.env['hr.leave'], self.env['hr.leave']
        for holiday in self:
            start = UTC.localize(holiday.date_from).astimezone(timezone(holiday.employee_id.tz or 'UTC'))
            end = UTC.localize(holiday.date_to).astimezone(timezone(holiday.employee_id.tz or 'UTC'))
            note = _(
                'New %(leave_type)s Request created by %(user)s from %(start)s to %(end)s',
                leave_type=holiday.holiday_status_id.name,
                user=holiday.create_uid.name,
                start=start,
                end=end
            )
            emp_id = self.employee_id.id
            parent_id = self.env['hr.employee'].search([('id', '=', emp_id)])
            user = self.env['res.users'].search([('id', '=', parent_id.parent_id.user_id.id)])
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'head_approve':
                holiday.activity_schedule(
                    'hr_holidays.mail_act_leave_head_approval',
                    note=note,
                    user_id=user.id or self.env.user.id)
        super(LeavesLogicInherit, self).activity_update()

    def add_attachment_file(self):
        print('hello')

    def action_super_approve(self):
        self.state = 'validate'

    def action_confirm(self):
        print('con')
        if self.holiday_status_id.leave_validation_type == 'order_manager_to_hr':
            self.sudo().write({'state': 'head_approve'})
        else:
            self.sudo().write({'state': 'confirm'})
        super(LeavesLogicInherit, self).action_confirm()

    def action_head_approve(self):
        if self.employee_id.parent_id.user_id.id == self.env.user.id:
            self.state = 'confirm'
            self.activity_feedback(['hr_holidays.mail_act_leave_head_approval'])
            hr = self.holiday_status_id.responsible_id
            self.activity_schedule(
                'hr_holidays.mail_act_leave_approval',
                user_id=hr.id, )
            self.activity_update()

        else:
            raise ValidationError(_('Only Head of Department can approve this leave.'))

    def action_head_refuse(self):
        if self.employee_id.parent_id.user_id.id == self.env.user.id:
            self.state = 'refuse'
        else:
            raise ValidationError(_('Only Head of Department can reject this leave.'))

    def action_mark_as_draft(self):
        self.state = 'draft'

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

    def action_approve(self):
        user = self.env.ref('hr_holidays.group_hr_holidays_user').users
        hr = []
        for j in user:
            hr.append(j.id)
            print(j.id, 'hello approve')
            print(self.env.user.id, 'env user')
        if self.env.user.id not in hr:
            raise ValidationError(_('Only HR Manager can approve this leave.'))
        else:
            super(LeavesLogicInherit, self).action_approve()

    def action_get_global_time_off(self):
        leave = self.env['resource.calendar'].sudo().search([])
        for i in leave.global_leave_ids:
            print(i.name, 'name')
            print('date', i.date_from, i.date_to)


class InheritEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    current_leave_state = fields.Selection(compute='_compute_leave_status', string="Current Time Off Status",
                                           selection=[
                                               ('draft', 'New'),
                                               ('confirm', 'Waiting Approval'),
                                               ('head_approve', 'Waiting Head Approval'),
                                               ('refuse', 'Refused'),
                                               ('validate1', 'Waiting Second Approval'),
                                               ('validate', 'Approved'),
                                               ('cancel', 'Cancelled')
                                           ])
