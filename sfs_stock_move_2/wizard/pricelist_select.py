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
###############################################################################

from osv import fields, osv

class pricelist_select(osv.osv_memory):
    
    _name = "pricelist.select"
    _description = """ A table to enter the Price list required """
    _columns = {
                "pricelist_id": fields.many2one("product.pricelist", "Pricelist")
               }
    
pricelist_select()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: