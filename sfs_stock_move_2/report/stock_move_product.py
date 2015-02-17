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
############################################################################

import tools
import time 
from osv import fields,osv

class stock_movement_product_report(osv.osv):
    _name = "stock.move_product"
    _description = "report on stock movements"
    _auto = False
    _order = 'date_move'
    _rec_name = 'product_name'
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        res = super(stock_movement_product_report, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,
            context=context, count=count)
        return res
    
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
                'movement': fields.selection([('In','In'), ('Out','Out')], "Movement", size=64),
                'stock': fields.float("Real Stock"),
                'list_price': fields.function(_get_sale_price, method=True, type='float',
                                              string='Sale Price'),
                'product_qty': fields.float('Qtty'),
                'sale_price': fields.float('Sale Price'),
                'product_id': fields.many2one("product.product", 'PID'),
                'partner_id': fields.many2one('res.partner', 'Partner'),
                'uom_id': fields.integer("uom id")
               }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_move_product')
        cr.execute("""
                   drop function if exists get_qty_onhand(product_id integer);
                   CREATE OR REPLACE FUNCTION get_qty_onhand
                   (x_product_id integer)
                   RETURNS TABLE(qty float) AS
                   $BODY$
                   BEGIN
                   return query
                   select sum(x.product_qty) 
                   from((SELECT
                        coalesce(sum(-m.product_qty * pu.factor / pu2.factor)::float, 0.0) as product_qty
                   FROM
                    stock_move m
                        LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)
                        LEFT JOIN stock_location l ON (m.location_id=l.id)
                        where m.product_id = x_product_id and l.usage = 'internal'  
                   GROUP BY
                        m.id, m.product_id, m.product_uom, pt.categ_id, m.location_id,  m.location_dest_id,
                        m.prodlot_id, m.date, m.state, l.usage, m.company_id, pt.uom_id) 
                   UNION ALL (
                   SELECT
                   coalesce(sum(m.product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty
                   FROM
                    stock_move m
                        LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                        LEFT JOIN product_product pp ON (m.product_id=pp.id)
                        LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
                        LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
                        LEFT JOIN product_uom u ON (m.product_uom=u.id)
                        LEFT JOIN stock_location l ON (m.location_dest_id=l.id)
                        where m.product_id = x_product_id and l.usage='internal'
                   GROUP BY
                        m.id, m.product_id, m.product_uom, pt.categ_id, m.location_id, m.location_dest_id,
                        m.prodlot_id, m.date, m.state, l.usage, m.company_id, pt.uom_id
                    ))x;
                   END
                   $BODY$
                   LANGUAGE 'plpgsql';
                
                   create or replace view stock_move_product as (
                       select
                           min(stm.id) as id,
                           to_date(to_char(stm.date, 'YYYY/MM/DD'),'YYYY/MM/DD') as date_move,
                           pr.default_code as product_reference,
                           pt.id as product_id,
                           pu.id as uom_id,
                           stm.partner_id as partner_id,
                           pt.name as product_name,
                           sum(stm.product_qty) as product_qty ,
                           sum(pt.list_price) as sale_price ,
                           (select get_qty_onhand(pr.id)) as stock, 
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
                           pr.id,
                           stm.date,
                           pr.default_code,
                           pt.name,
                           sl.usage,
                           stm.product_id,
                           stm.product_qty,
                           pt.list_price,
                           pt.id,
                           pu.id,
                           stm.partner_id);
                   """)


stock_movement_product_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: