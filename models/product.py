from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_parts = fields.Boolean(string="Is Parts", help="Indicates if this product is a part.")
    product_service_type_id = fields.Many2one('dsl.product.service.type', string='Product Service Type')
    fuel_type = fields.Selection([
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('full_hybrid', 'Full Hybrid'),
        ('plug_in_hybrid_diesel', 'Plug-in Hybrid Diesel'),
        ('plug_in_hybrid_gasoline', 'Plug-in Hybrid Gasoline'),
        ('cng', 'CNG'),
        ('lpg', 'LPG'),
        ('hydrogen', 'Hydrogen'),
        ('electric', 'Electric'),
    ], string='Fuel Type')