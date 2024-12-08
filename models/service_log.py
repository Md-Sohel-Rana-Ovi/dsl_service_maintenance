import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class DSLFuelLog(models.Model):
    _name = 'dsl.service.log'
    _description = 'Service Log'
    _rec_name="employee_id"

    description = fields.Html(string='Description')
    code = fields.Char(string="Serial No", default=lambda self: _("New"), tracking=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    driver_id = fields.Many2one('res.partner', string='Driver')
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
    date = fields.Date(string='Date', default=fields.Date.today)
    product_service_type_id = fields.Many2one('dsl.product.service.type', string='Service Type')
    cost= fields.Float(string="Cost")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Canceled')],
        default='draft',
        string="Status",
        tracking=True,
    )
    def action_approve(self):
        for rec in self:
            rec.write({'state': 'approved'})

    def action_cancel(self):
        for rec in self:
            rec.write({'state': 'cancel'})

    def action_reset_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('dsl.service.log')
        result = super(DSLFuelLog, self).create(vals)
        return result


