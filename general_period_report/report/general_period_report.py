# -*- encoding: utf-8 -*
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
import openerp.addons.decimal_precision as dp
from osv import fields,osv

class general_period_report(osv.osv):
    
    _name = "general.period.report"
    _description = "report on account invoices"
    _auto = False
    _rec_name = 'date_invoice'
    _columns = {
                'company_id': fields.many2one('res.company','Company', readonly=True),
                'date_invoice': fields.date('Date', readonly=True),
                'amount_total1': fields.float('Customer Invoices'),
                'amount_total2': fields.float('Customer Refunds'),
                'amount_total3': fields.float('Supplier Invoices'),
                'amount_total4': fields.float('Supplier Refunds'),
                'profit_amount': fields.float(' Profit Amount'),
                'profit_percent': fields.float('Profit Percent', digits_compute=dp.get_precision('Account')),
               }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'general_period_report')
        cr.execute("""
                   create or replace view general_period_report as (
                       select
                           max(id) as id,
                           date_invoice,
                           company_id,
                           sum(amount_total1) as amount_total1,
                           sum(amount_total2) as amount_total2,
                           sum(amount_total3) as amount_total3,
                           sum(amount_total4) as amount_total4,
                           sum((amount_total1-amount_total2)-(amount_total3-amount_total4)) as profit_amount,
                           case sum(amount_total1)
                           When 0.00 Then 100.00
                           else 
                           sum((amount_total1-amount_total2)-(amount_total3-amount_total4))/sum(amount_total1) 
                           End as profit_percent
                       from(
                           select
                           max(acc_inv.id) as id,    
                           acc_inv.company_id as company_id,
                           to_date(to_char(acc_inv.date_invoice, 'YYYY/MM/DD'),'YYYY/MM/DD') as date_invoice,
                           case acc_inv.type
                           When 'out_invoice' Then acc_inv.amount_total
                           else 0.00
                           End as amount_total1,
                           case acc_inv.type
                           When 'out_refund' Then acc_inv.amount_total
                           else 0.00
                           End as amount_total2,
                           case acc_inv.type
                           When 'in_invoice' Then acc_inv.amount_total
                           else 0.00
                           End as amount_total3,
                           case acc_inv.type
                           When 'in_refund' Then acc_inv.amount_total
                           else 0.00
                           End as amount_total4
                        from account_invoice as acc_inv
                        group by
                           acc_inv.date_invoice,
                           acc_inv.company_id,
                           acc_inv.type,
                           acc_inv.amount_total
                           ) as report
                    group by date_invoice, 
                        company_id
                    )
                   """)

general_period_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:-
