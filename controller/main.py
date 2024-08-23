from odoo import http
from odoo.http import request

class MyDashboard(http.Controller):

    @http.route('/my_dashboard', type='http', auth='user')
    def my_dashboard(self, **kw):
        holidays = request.env['hr.leave'].get_public_holidays()
        return request.render('logic_leaves.my_dashboard_template', {
            'holidays': holidays,
        })