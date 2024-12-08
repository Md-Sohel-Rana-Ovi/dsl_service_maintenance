from odoo import models, fields,api, _


class DSLProductServiceType(models.Model):
    _name = 'dsl.product.service.type'
    _description = 'Service Type'

    name = fields.Char(string='Name', required=True)
    note = fields.Char(string='Note')


class DSLVehicleType(models.Model):
    _name = 'dsl.vehicle.type'
    _description = 'Vehicle Type'

    name = fields.Char(string='Name', required=True)
    note = fields.Char(string='Note')

class DSLGolfDrivers(models.Model):
    _name = 'dsl.golf.driver'
    _description = 'Golf Driver'

    name = fields.Char(string='Name', required=True)
    note = fields.Char(string='Note')

class DSLServiceType(models.Model):
    _name = 'dsl.service.type'
    _description = 'Golf Service Type'

    name = fields.Char(string='Name', required=True)
    note = fields.Char(string='Note')


