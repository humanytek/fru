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
from osv import fields,osv

class stock_movement_report(osv.osv):
    _name = "stock.movement_report"
    _description = "report on stock movements"
    _auto = False
    _rec_name = 'product_name'
    
    def _get_sale_price(self, cr, uid, ids, name, arg, context=None):
       res = {}
       product_pricelist_obj = self.pool.get('product.pricelist')
       pricelist = context.get('pricelist_id',False)
       for obj in self.browse(cr, uid, ids, context=context):
           if pricelist:
               uom_id = obj.uom_id
               product = obj.product_id and obj.product_id.id
               qty = obj.product_qty
               partner_id = obj.partner_id and obj.partner_id.id
               price = product_pricelist_obj.price_get(cr, uid, [pricelist], product, 
                                                       qty or 1.0, partner_id, context={'uom': uom_id}
                                                       )[pricelist]
               res[obj.id] = price
           else:
               res[obj.id] = obj.sale_price
       return res
   
    _columns = {
                'date_move': fields.date('Date Movement', readonly=True),
                'product_reference': fields.char('Product Reference', size=128),
                'product_name': fields.char('Product Name', size=128),
                'product_qty': fields.float('Qtty'),
                'product_id': fields.many2one("product.product", 'PID'),
                'uom_id': fields.integer("uom id"),
                'partner_id': fields.many2one('res.partner', 'Partner'),
                'movement': fields.selection([('In', 'In'),('Out','Out')], "Movement", size=64),
                'sale_price': fields.float('Sale Price'),
                'list_price': fields.function(_get_sale_price, method=True, type='float',
                                              string='Sale Price'),
               }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_movement_report')
        cr.execute("""
                   create or replace view stock_movement_report as (
                       select
                           min(stm.id) as id,
                           to_date(to_char(stm.date, 'YYYY/MM/DD'),'YYYY/MM/DD') as date_move,
                           pr.default_code as product_reference,
                           pt.name as product_name,
                           pu.id as uom_id,
                           pt.id as product_id,
                           sum(stm.product_qty) as product_qty,
                           stm.partner_id as partner_id,
                           sum(pt.list_price) as sale_price,
                        case sl.usage
                           When 'internal' Then 'In'
                           Else 'Out'
                        End as movement
                        from stock_move as stm
                           left join stock_location sl on (sl.id = stm.location_dest_id)
                           left join product_product pr on (pr.id=stm.product_id)
                           left join product_template pt on (pr.product_tmpl_id=pt.id) 
                           LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)                         
                        group by
                           stm.date,
                           pr.default_code,
                           pt.name,
                           stm.partner_id,
                           sl.usage,
                           pt.list_price,
                           stm.product_qty,
                           pt.id,
                           pu.id)
                   """)

stock_movement_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: