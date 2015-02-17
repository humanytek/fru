# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Move Analysis',
    'version': '1.3',
    'category': 'Stock Management',
    'description': """ 
        Module to generate A stock Movement Analysis Report
    """,
    'author': 'SF Soluciones',
    'website': 'sfsoluciones.com',
    'depends': ['stock'],
    'init_xml': [],
    'update_xml': [
                   'report/stock_movement_report.xml',
                   'wizard/pricelist_select_wizard_view.xml',
                   'security/ir.model.access.csv',
                  ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: