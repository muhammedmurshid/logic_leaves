{
    'name': "Logic Leaves Allocation",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'hr', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/leave_allocation_casual.xml',
        'views/leaves_reporting.xml',
        'views/leaves.xml',
        'data/activity.xml',
        'views/leave_type.xml',
        'views/refuse_reason.xml',

    ],


    'demo': [],
    'summary': "logic_leaves_allocation",
    'description': "leave_allocation",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': False
}
