from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
import logging
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class DSLFuelRequisition(models.Model):
    _name = 'dsl.fuel.requisition'
    _description = 'Fuel Requisition'

    name = fields.Char(
        string="Note",
        required=True,
        default=lambda self: _("New"),
        tracking=True,
    )    
    code = fields.Char(string="Serial No", default=lambda self: _("New"), readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                default=lambda self: self.env.user.employee_id.id)
    department_id = fields.Many2one("hr.department", string="Department",
                                    default=lambda self: self.env.user.employee_id.department_id.id)
    fuel_config_id = fields.Many2one('dsl.fuel.config', string="Fuel Configuration")
    source_location_id = fields.Many2one('stock.location', string="Requested Location", domain=[('usage', '=', 'internal')])
    destination_location_id = fields.Many2one('stock.location', string="Requesting Location", domain=[('usage', '=', 'internal')], default=lambda self: self.env.user.employee_id.destination_location_id.id)

    product_id = fields.Many2one('product.product', string="Product")
    product_service_type_id = fields.Many2one('dsl.product.service.type', string='Product Service Type')
    
    quantity = fields.Float(string="Quantity")
    quantity_done = fields.Float(string="Quantity Done", readonly=True)
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure", related="product_id.uom_id", readonly=True)
    
    qty_available = fields.Float(
        string="Available Quantity", 
        compute="_compute_qty_available", 
        store=True,
        readonly=True
    )
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Dynamically set source location based on selected product"""
        if self.product_id:
            # Retrieve the locations associated with the selected product through stock.quant
            quants = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id.usage', '=', 'internal')
            ])
            
            # Get the unique locations from the quants
            locations = quants.mapped('location_id')
            
            # Update the source_location_id domain with filtered locations
            self.source_location_id = False  # Reset the selected location
            return {
                'domain': {
                    'source_location_id': [('id', 'in', locations.ids)]
                }
            }
        else:
            # Reset source_location_id domain if no product is selected
            return {
                'domain': {
                    'source_location_id': [('usage', '=', 'internal')]
                }
            }
            
    @api.depends('source_location_id', 'product_id')
    def _compute_qty_available(self):
        for record in self:
            if record.source_location_id and record.product_id:
                # Find the stock.quant record for the given location and product
                quant = self.env['stock.quant'].search([
                    ('location_id', '=', record.source_location_id.id),
                    ('product_id', '=', record.product_id.id)
                ], limit=1)
                
                # Assign the available quantity from the quant record
                if quant:
                    record.qty_available = quant.quantity
                else:
                    record.qty_available = 0.0
            else:
                record.qty_available = 0.0
                
    service_id = fields.Many2one('dsl.product.service.type', string='Service Type')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

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
    
    @api.constrains('date')
    def _check_date(self):
        """Ensure the date is not in the future."""
        for record in self:
            if record.date > fields.Date.today():
                raise ValidationError("The date cannot be in the future. Please select a valid date.")
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Requested'),
        ('confirm', 'Confirmed'),
        ('approve', 'Approved'),
        ('transfer', 'Transferred'),
        ('received', 'Received'),
        ('reject', 'Rejected')],
        default='draft', string="Status", tracking=True
    )
    approved_by = fields.Many2one("res.users", string="Approved by")
    approved_date = fields.Date("Approved On")
    confirmed_by = fields.Many2one("res.users", string="Confirmed by")
    confirmed_date = fields.Date("Confirmed On")
    transfered_by = fields.Many2one("res.users", string="Transferred by")
    transfered_date = fields.Date("Transferred On")
    rejected_by = fields.Many2one("res.users", string="Rejected by")
    rejected_date = fields.Date("Rejected On")
    
    ### COMPUTE METHODS ###
    @api.model
    def _get_products_for_location(self):
        """Filter products available at the source location from the fuel config."""
        if self.source_location_id:
            location = self.source_location_id
            return [('location_id', '=', location.id)]
        return []

    ### ACTIONS ###
    def action_request(self):
        self.state = "request"

    def action_confirm(self):
        self.state = "confirm"
        self.confirmed_by = self.env.user.id
        self.confirmed_date = date.today()

    def action_approve(self):
        self.state = "approve"
        self.approved_by = self.env.user.id
        self.approved_date = date.today()

    def action_transfer(self):
        self.transfered_by = self.env.user.id
        self.transfered_date = date.today()

        # Get the source and destination locations
        source_location = self.source_location_id.id  # Source location
        destination_location = self.destination_location_id.id  # Destination location

        # Ensure that the source location is valid
        if not source_location:
            raise UserError(_('Source location is not defined. Please select a valid source location.'))

        # Ensure that the destination location is valid
        if not destination_location:
            raise UserError(_('Destination location is not defined. Please select a valid destination location.'))

        # Ensure we have a valid warehouse associated with the company
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
        if not warehouse_id:
            raise UserError(_('Warehouse is not defined for this company. Please configure it in warehouse settings.'))

        # Get the internal transfer picking type
        picking_type_id = self.env['stock.picking.type'].search([
            ('warehouse_id', '=', warehouse_id.id),
            ('code', '=', 'internal')  # Internal Transfer type
        ], limit=1)
        
        if not picking_type_id:
            raise UserError(_('Internal transfer picking type is not defined for this warehouse.'))

        # Create the stock picking record for the transfer
        picking_id = self.env['stock.picking'].create({
            'partner_id': self.employee_id.user_id.partner_id.id,
            'origin': self.code,
            'location_id': source_location,
            'location_dest_id': destination_location,
            'picking_type_id': picking_type_id.id,  # Picking type for internal transfer
            'store_requisition_id': self.id,  # Link back to the requisition
        })

        # Create a stock move for the requisition (since no One2many lines are used)
        quantity_inprogress = self.quantity  # Transfer the full quantity requested

        if quantity_inprogress > self.qty_available:
            quantity_inprogress = self.qty_available  # Transfer only available quantity

        move_id = self.env['stock.move'].create({
            'name': self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': quantity_inprogress,  # Transfer the available quantity
            'reserved_availability': quantity_inprogress,  # Reserve the stock for transfer
            'product_uom': self.uom_id.id,
            'picking_id': picking_id.id,
            'location_id': source_location,
            'location_dest_id': destination_location,
        })

        # Update the quantity_done (if applicable)
        self.quantity_done = quantity_inprogress

        # Update the requisition state to 'transfer'
        self.state = "transfer"

        # -- Manual confirmation of the picking (replicating action_confirm) --
        # Move the picking to 'confirmed' state
        picking_id.write({'state': 'confirmed'})
        
        # -- Manual stock assignment (replicating action_assign) --
        # Assign the stock moves (reserve stock)
        moves = picking_id.move_ids.filtered(lambda move: move.state not in ('done', 'cancel'))
        if moves:
            moves._action_assign()  # Reserve the stock in the system

        # -- Manual validation (replicating button_validate) --
        # Mark the picking as 'done', which will also update stock.quant records
        picking_id.write({'state': 'done'})
        
        # Adjust the inventory in stock.quant for the source and destination locations
        self._adjust_stock_quant(picking_id)

        # Record the transfer details
        self.transfered_by = self.env.user.id
        self.transfered_date = date.today()

        return True

    def _adjust_stock_quant(self, picking_id):
        """ Adjust the stock.quants based on the transfer for source and destination locations """
        # Get the stock move(s) from the picking
        for move in picking_id.move_ids:
            # if move.state == 'done':
                # Decrease stock in source location
                self.env['stock.quant'].create({
                    'location_id': move.location_id.id,
                    'product_id': move.product_id.id,
                    'quantity': -move.product_uom_qty,  # Deduct the quantity
                    'in_date': date.today(),
                })

                # Increase stock in destination location
                self.env['stock.quant'].create({
                    'location_id': move.location_dest_id.id,
                    'product_id': move.product_id.id,
                    'quantity': move.product_uom_qty,  # Add the quantity
                    'in_date': date.today(),
                })

    def action_receive(self):
        self.state = "received"

    def action_reject(self):
        self.state = "reject"
        self.rejected_by = self.env.user.id
        self.rejected_date = date.today()

    def action_reset_draft(self):
        self.state = "draft"

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('dsl.fuel.requisition')
        return super(DSLFuelRequisition, self).create(vals)

    def unlink(self):
        if self.filtered(lambda r: r.state != 'draft'):
            raise UserError(_('Only requests in draft state can be deleted.'))
        return super(DSLFuelRequisition, self).unlink()

class StockPicking(models.Model):
    _inherit = "stock.picking"

    store_requisition_id = fields.Many2one('dsl.fuel.requisition', string="Fuel Requisition")


class DSLFuelConfig(models.Model):
    _name = 'dsl.fuel.config'
    _description = 'Fuel Transfer Configuration'

    name = fields.Char(string='Name', default='Global Configuration')
    source_location_id = fields.Many2one('stock.location', string="Source Location")
    destination_location_id = fields.Many2one('stock.location', string="Destination Location")
