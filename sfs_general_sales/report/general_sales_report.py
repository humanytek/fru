# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 SF Soluciones.
#    (http://www.sfsoluciones.com)#    
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

from osv import fields, osv
import tools
import openerp.addons.decimal_precision as dp

class general_sales_report(osv.osv):
    _name = "general.sales.report"
    _description = "report on confirmed sale orders"
    _auto = False
    _rec_name = "sale_order_no"
    _columns = {
                'sale_order_no': fields.char('Sale order number', readonly=True, 
                                             size=64),
                'sale_order_date': fields.date('Date sale order', readonly=True),
                'partner_id': fields.many2one('res.partner', 'Customer name', 
                                               readonly=True),
                'amount_total': fields.float('Total Amount', readonly=True, 
                                             digits_compute=dp.get_precision('Account'))
               }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'general_sales_report')
        cr.execute(""" 
                   create or replace view general_sales_report as (
                       select
                           min(so.id) as id,
                           so.name as sale_order_no,
                           so.date_order as sale_order_date,
                           res.id as partner_id,
                           sum(so.amount_total) as amount_total
                        from sale_order as so
                            left join res_partner res on (so.partner_id=res.id)
                        group by
                            so.name,
                            so.date_order,
                            res.id,
                            so.state
                        having
                            so.state NOT IN ('draft', 'sent', 'cancel'))
                   """)

general_sales_report()
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: