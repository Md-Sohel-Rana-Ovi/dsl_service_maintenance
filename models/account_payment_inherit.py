from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'account.payment'
    
    product_service_type_id = fields.Many2one('dsl.service.type', string='Service Type')
