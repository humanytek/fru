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

import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp

class sales_by_product_report(osv.osv):
    _name = "sales.analysis_report"
    _description = "report on confirmed sale orders by product"
    _auto = False
    _rec_name = 'product_name'
    _columns = {
                'sale_order_date': fields.date('Date', readonly=True) ,
                'product_reference': fields.char('Product Reference', size=128) ,
                'product_name': fields.char('Product Name', size=128) ,
                'product_qty': fields.float('Total Quantity') ,
                'price_unit': fields.float('Unit Price') ,
                'amount_total': fields.float('Total Amount', digits_compute = dp.get_precision('Account')) ,
                'partner_id': fields.many2one('res.partner', 'Customer') ,
               }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sales_analysis_report')
        cr.execute(""" 
                   create or replace view sales_analysis_report as (
                       select
                           min(l.id) as id ,
                           s.date_order as sale_order_date ,
                           p.default_code as product_reference ,
                           l.name as product_name ,
                           sum(l.product_uom_qty) as product_qty ,
                           l.price_unit as price_unit ,
                           res.id as partner_id ,
                           sum(l.product_uom_qty * l.price_unit) as amount_total
                        from sale_order_line as l
                            left join sale_order s on (l.order_id=s.id)
                            left join res_partner res on (s.partner_id=res.id)
                            left join product_product p on (l.product_id=p.id)
                        group by
                            s.date_order ,
                            p.default_code ,
                            l.name ,
                            l.price_unit ,
                            res.id ,
                            s.state
                        having
                            s.state NOT IN ('draft', 'sent', 'cancel'))
                   """)


sales_by_product_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: