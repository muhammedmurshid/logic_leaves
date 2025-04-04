from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, time
import requests
from odoo.tools import float_compare, format_date
from pytz import timezone, UTC
from datetime import date, datetime


class LeavesLogicInherit(models.Model):
    _inherit = 'hr.leave'

    attachment_file = fields.Binary(string='Attachment File (150 KB)', attachment=True)
    # sick_leave_already_taken = fields.Boolean('Sick Leave Already Taken')
    # one_more_days_taken_sick_leave = fields.Boolean('One More Days Taken Sick Leave')
    is_it_sick_leave = fields.Boolean('Is It Sick Leave')
    is_it_old_day = fields.Boolean('Is It Old Day')
    reason = fields.Char(string="Reason")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('head_approve', 'Head Approval'),
        # YTI This state seems to be unused. To remove
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', store=True, tracking=True, copy=False, readonly=False,
        help="The status is set to 'To Submit', when a time off request is created." +
             "\nThe status is 'To Approve', when time off request is confirmed by user." +
             "\nThe status is 'Refused', when time off request is refused by manager." +
             "\nThe status is 'Approved', when time off request is approved by manager.")

    note = fields.Text(readonly=1, string='Note',
                       default='Departing without obtaining approval from both HR and the Head will be deemed as Leave Without Pay (LOP), except in cases of emergencies.')
    refuse_reason = fields.Text(string="Refuse Reason")

    # unusual_days_reason = fields.Text(string="Unusual Days Reason")
    # public_holiday_reason = fields.Char(string="Public Holiday Reason", compute='_compute_public_holiday_reason',
    #                                     store=True)

    # @api.depends('date_from')  # You may adjust this dependency based on your use case
    # def _compute_public_holiday_reason(self):
    #     print('work')
    #     for record in self:
    #         if record.holiday_type == 'public_holiday':
    #             print('kkkkkoooi')  # Replace with the condition that fits your requirement
    #             holiday = self.env['resource.calendar.leaves'].search([('holiday_id', '=', record.id)], limit=1)
    #             record.public_holiday_reason = holiday.reason if holiday else 'N/A'
    #         else:
    #             print('oooi')
    #             record.public_holiday_reason = 'N/A'

    # @api.model
    # def get_unusual_days(self, date_from, date_to=None):
    #     # Fetch all public holidays
    #     public_holidays = self.env['resource.calendar.leaves'].search([])
    #     # Concatenate all public holiday names and reasons
    #     unusual_days_reason = ', '.join([f"{ph.name}: {ph.name}" for ph in public_holidays])
    #
    #     # Update the record with unusual_days_reason
    #     if self:
    #         self.ensure_one() # Ensure we're working with a single record
    #         self.write({'unusual_days_reason': unusual_days_reason})
    #         # Call the parent method
    #     return super(LeavesLogicInherit, self).get_unusual_days(date_from, date_to)
    #
    # def name_get(self):
    #     res = []
    #     public_holidays = self.env['resource.calendar.leaves'].search([])
    #
    #     # Concatenate all public holiday names and reasons
    #     unusual_days_reason = ', '.join([f"{ph.name}: {ph.date_from}" for ph in public_holidays])
    #     print(unusual_days_reason, 'unusual_days_reason')
    #     res.append(('unusual_days_info', unusual_days_reason))
    #     for leave in self:
    #         # a = leave.unusual_days_reason
    #         # print(leave, 'a')
    #         if self.env.context.get('short_name'):
    #             unusual_days_info = leave.unusual_days_reason or ''
    #             if leave.leave_type_request_unit == 'hour':
    #                 res.append((leave.id, _("%s : %.2f hours - %s") % (
    #                     leave.name or leave.holiday_status_id.name, leave.number_of_hours_display, unusual_days_info)))
    #             else:
    #                 res.append((leave.id, _("%s : %.2f days - %s") % (
    #                     leave.name or leave.holiday_status_id.name, leave.number_of_days, unusual_days_info)))
    #         else:
    #             if leave.holiday_type == 'company':
    #                 target = leave.mode_company_id.name
    #             elif leave.holiday_type == 'department':
    #                 target = leave.department_id.name
    #             elif leave.holiday_type == 'category':
    #                 target = leave.category_id.name
    #             else:
    #                 target = leave.employee_id.name
    #
    #             display_date = fields.Date.to_string(leave.date_from)
    #             unusual_days_info = leave.unusual_days_reason or ''
    #
    #             if leave.leave_type_request_unit == 'hour':
    #                 res.append((
    #                     leave.id,
    #                     _("%(person)s on %(leave_type)s: %(duration).2f hours on %(date)s - %(unusual_days_info)s") % {
    #                         'person': target,
    #                         'leave_type': leave.holiday_status_id.name,
    #                         'duration': leave.number_of_hours_display,
    #                         'date': display_date,
    #                         # 'unusual_days_info': unusual_days_info,
    #                     }
    #                 ))
    #             else:
    #                 if leave.number_of_days > 1:
    #                     display_date += ' ⇨ %s' % fields.Date.to_string(leave.date_to)
    #                 res.append((
    #                     leave.id,
    #                     _("%(person)s on %(leave_type)s: %(duration).2f days (%(start)s) - %(unusual_days_info)s") % {
    #                         'person': target,
    #                         'leave_type': leave.holiday_status_id.name,
    #                         'duration': leave.number_of_days,
    #                         'start': display_date,
    #                         # 'unusual_days_info': unusual_days_info,
    #                     }
    #                 ))
    #     print(res, 'res')
    #     return res

    @api.onchange('request_date_from')
    def _compute_get_time_of_manager(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('hr_holidays.group_hr_holidays_user'):
            self.is_this_time_off_manager = True
        else:
            self.is_this_time_off_manager = False

    is_this_time_off_manager = fields.Boolean('Is This Time Off Manager', compute='_compute_get_time_of_manager')

    # @api.onchange('request_date_from', 'request_date_to')
    # def _onchange_request_date(self):
    #     today = fields.Date.today()
    #
    #     if self.request_date_from and self.request_date_to:
    #         if not self.is_this_time_off_manager:
    #             request_date = self.request_date_from
    #             # Determine the salary period for the current date
    #             if request_date.month == today.month:
    #                 if request_date.day < 21:
    #                     if today.day <= 21:
    #                         self.is_it_old_day = False
    #                     else:
    #                         self.is_it_old_day = True
    #                 else:
    #                     self.is_it_old_day = False
    #             else:
    #                 before_month = today.month - 1
    #                 if request_date.month == before_month:
    #                     if request_date.day > 20:
    #                         self.is_it_old_day = False
    #                     else:
    #                         self.is_it_old_day = True
    #                 else:
    #                     if request_date.month > today.month:
    #                         self.is_it_old_day = False
    #                     else:
    #                         self.is_it_old_day = True

    @api.model
    def create(self, vals):

        # print(vals.holiday_status_id.leave_validation_type, 'leave validation type')

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
            if not mob.leave_manager_id.employee_id.mobile_phone:
                raise ValidationError(_('Please add mobile number of Head of Department.'))
            else:
                head_number = mob.leave_manager_id.employee_id.mobile_phone
                print(head_number, 'head_number')
                user = 'Manager'
                #
                #     # print(response_json)
                message_applied = "Hi " + user + ", an employee has requested leave in Logic HRMS. For more details login to https://corp.logiceducation.org"
                dlt_applied = '1107168381905841814'
                url = "http://sms.mithraitsolutions.com/httpapi/httpapi?token=adf60dcda3a04ec6d13f827b38349609&sender=LSMKCH&number=" + head_number + "&route=2&type=Text&sms=" + message_applied + "&templateid=" + dlt_applied
                response = requests.get(url)

                # response_json = response.json()
                emp_id = vals['employee_id']
                parent_id = self.env['hr.employee'].search([('id', '=', emp_id)])
                user = self.env['res.users'].search([('id', '=', parent_id.leave_manager_id.id)])
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
            user = self.env['res.users'].search([('id', '=', parent_id.leave_manager_id.id)])
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

    def action_super_reject(self):
        return  {'type': 'ir.actions.act_window',
                 'name': _('Refuse Reason'),
                 'res_model': 'refuse.reason.logic',
                 'target': 'new',
                 'view_mode': 'form',
                 'view_type': 'form',
                 'context': {'default_leave_id': self.id,
                             'default_type': 'super_refuse'}, }

        # self.sudo().write({
        #     'state': 'refuse'
        # })


    def action_confirm(self):
        print('con')
        if self.holiday_status_id.leave_validation_type == 'order_manager_to_hr':
            self.sudo().write({'state': 'head_approve'})
        else:
            self.sudo().write({'state': 'confirm'})
        super(LeavesLogicInherit, self).action_confirm()


    def action_head_approve(self):
        if self.employee_id.leave_manager_id.id == self.env.user.id:
            self.sudo().state = 'confirm'
            self.activity_feedback(['hr_holidays.mail_act_leave_head_approval'])
            hr = self.holiday_status_id.responsible_id
            self.activity_schedule(
                'hr_holidays.mail_act_leave_approval',
                user_id=hr.id, )
            self.activity_update()

        else:
            raise ValidationError(_('Only Head of Department can approve this leave.'))


    def action_head_refuse(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Refuse Reason'),
                'res_model': 'refuse.reason.logic',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_leave_id': self.id,
                            'default_type': 'head_refuse'}, }



    def action_mark_as_draft(self):
        self.state = 'draft'


    @api.onchange('holiday_status_id')
    def _onchange_date(self):
        if self.holiday_status_id.name == 'Sick Leave':
            self.is_it_sick_leave = True

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

    def action_refuse(self):
        super(LeavesLogicInherit, self).action_refuse()
        return {'type': 'ir.actions.act_window',
                'name': _('Refuse Reason'),
                'res_model': 'refuse.reason.logic',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_leave_id': self.id,
                            'default_type': 'refuse'}, }


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


class PublicHolidayView(models.Model):
    _name = 'custom.public.holiday.view'

    name = fields.Char('Reason')
    holiday_status_id = fields.Many2one('hr.leave.type', string="Leave Type")


class PublicHoliday(models.Model):
    _name = 'public.holiday'
    _description = 'Public Holiday'

    name = fields.Char('Holiday Name', required=True)
    date = fields.Date('Date', required=True)


class RefuseReason(models.TransientModel):
    _name = 'refuse.reason.logic'

    reason = fields.Text(string="Reason", required=1)
    leave_id = fields.Many2one('hr.leave')
    type = fields.Selection([('head_refuse', 'Head Refuse'), ('super_refuse', 'Super Refuse'), ('refuse','Refuse')], string="Type")

    def action_super_refuse_reason(self):
        self.leave_id.refuse_reason = self.reason
        self.sudo().leave_id.state = 'refuse'



    def action_head_refuse_reason(self):
        self.leave_id.refuse_reason = self.reason

        if self.leave_id.employee_id.leave_manager_id.id == self.env.user.id:
            self.leave_id.state = 'refuse'
        else:
            raise ValidationError(_('Only Head of Department can reject this leave.'))

    def action_refuse_reason(self):
        self.leave_id.refuse_reason = self.reason
        self.sudo().leave_id.state = 'refuse'
