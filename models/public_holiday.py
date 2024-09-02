from odoo import models, fields, _, api


class AddPublicHolidayToLeaves(models.Model):
    _inherit = 'resource.calendar'

    def write(self, vals):
        # print('kooi', vals)
        holiday = self.env['hr.leave.type'].sudo().search([('name', '=', 'Public Holiday')])
        company_id = self.env['res.users'].sudo().search([]).company_id.id
        for leave in vals['global_leave_ids']:
            if leave[0] == 0:
                leave_data = leave[2]  # This contains the dictionary with the new data
                name = leave_data.get('name')  # Get the 'name' field
                date_from = leave_data.get('date_from')
                date_to = leave_data.get('date_to')
                print(name, 'name', 'date :', date_from, 'date to:', date_to)
                leaves = self.env['hr.leave'].sudo().create({
                    'holiday_status_id': holiday.id,
                    'request_date_from': date_from,
                    'request_date_to': date_to,
                    'name': name,
                    'mode_company_id': company_id,
                    'holiday_type': 'company',
                    'state': 'draft'

                })

        # for i in vals.global_leave_ids:
        #     print(i.name)
        return super(AddPublicHolidayToLeaves, self).write(vals)

    def action_create_public_holiday(self):
        holiday = self.env['hr.leave.type'].sudo().search([('name', '=', 'Public Holiday')])
        print('holiday', holiday)
        company_id = self.env['res.users'].sudo().search([]).company_id.id
        print(company_id)
        date_from = '2024-09-23'
        date_to = '2024-09-24'
        print(date_to, date_from)
        name ='ppoo'
        leaves = self.env['hr.leave'].sudo().create({
            'holiday_status_id': holiday.id,
            'request_date_from': date_from,
            'request_date_to': date_to,
            'name': name,
            'mode_company_id': company_id,
            'holiday_type': 'company',
            'state': 'draft'

        })
