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
from osv import osv, fields

class stock_warehouse_analysis(osv.osv):
    _name = "stock.warehouse.qty.analysis"
    _description = "Stock by warehouse analysis"
    _auto = False
    _rec_name = 'product_id'
    _columns = {
                'product_ref': fields.char('Code', size=128),
                'product_id': fields.many2one('product.product', 'Description'),
                'product_categ_id': fields.many2one('product.category', 'Category'),
                'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse'),
                'sale_price': fields.float('Product Cost'),
                'product_qty': fields.float('Real Stock'),
                'total_value': fields.float('Total Value')
                }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'stock_warehouse_qty_analysis')
        cr.execute("""
            create or replace view stock_warehouse_qty_analysis as (
                select max(id) as id,
                        product_ref,
                        product_id,
                        warehouse_id,
                        product_categ_id,
                        sum(sale_price) as sale_price,
                        sum(qty) as product_qty,
                        case when sum(qty) < 0.00 then 0.00 else sum(sale_price) * sum(qty) end as total_value
                from (
                    select -max(sm.id) as id,
                        pp.default_code as product_ref,
                        sm.product_id,
                        sw.id as warehouse_id,
                        pt.categ_id as product_categ_id,
                        sum(pt.list_price) as sale_price,
                        -sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_location sl
                        on (sl.id = sm.location_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    left join stock_warehouse sw
                        on (sw.lot_stock_id = sm.location_id)
                    left join product_product pp
                        on(pp.id = sm.product_id)
                    left join product_template pt
                        on (pt.id = pp.product_tmpl_id)
                    where sm.state = 'done'
                    group by sm.product_id, sm.product_uom, sw.id, pp.default_code, pt.categ_id
                    union all
                    select max(sm.id) as id,
                        pp.default_code as product_ref,
                        sm.product_id,
                        sw.id as warehouse_id,
                        pt.categ_id as product_categ_id,
                        sum(pt.list_price) as sale_price,
                        sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_location sl
                        on (sl.id = sm.location_dest_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    left join stock_warehouse sw
                        on (sw.lot_stock_id = sm.location_dest_id)
                    left join product_product pp
                        on(pp.id = sm.product_id)
                    left join product_template pt
                        on (pt.id = pp.product_tmpl_id)
                    where sm.state = 'done'
                    group by sm.product_id, sm.product_uom, sw.id, pp.default_code, pt.categ_id
                ) as report
        where warehouse_id is not null
        group by product_ref, product_id, warehouse_id, product_categ_id)""")

stock_warehouse_analysis()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
