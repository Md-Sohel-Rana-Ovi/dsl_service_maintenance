# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date
from datetime import datetime


class DSLReportWizard(models.TransientModel):
    _name = 'dsl.report.wizard'

    from_date = fields.Date(string='From Date', default=lambda self: fields.Datetime.now())
    to_date = fields.Date(string='To Date')
    product_service_type_id = fields.Many2one('dsl.product.service.type', string='Product Service Type')
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    requested_by = fields.Many2one('res.users', string='Requested By')



    def generate_report(self):
        from_date = str(self.from_date) if self.from_date else None
        to_date = str(self.to_date) if self.to_date else None

        all_data = {
            'company_name': self.company_id.name,
            'company_logo': self.company_id.logo,
            'company_country': self.company_id.country_id.name,
            'from_date': from_date if from_date else "Not specified",
            'to_date': to_date if to_date else from_date if from_date else "Not specified",
        }

        # Build the domain dynamically based on the provided filters
        domain = []
        if from_date:
            domain.append(('date', '>=', from_date))
        if to_date:
            domain.append(('date', '<=', to_date))
        if self.product_service_type_id:
            domain.append(('product_service_type_id', '=', self.product_service_type_id.id))

        # Fetch data based on the dynamic domain
        requisitions = self.env['dsl.fuel.requisition'].search(domain)

        data_list = []
        for req in requisitions:
            data_list.append({
                'name': req.name,
                'code': req.code,
                'employee': req.employee_id.name,
                'product_service_type_id': req.product_service_type_id.name,
                'quantity': req.quantity,
                'fuel_type': req.fuel_type,
                'status': req.state,
            })

        all_data['data_list'] = data_list

        return self.env.ref('dsl_service_maintenance.dsl_fuel_requisition_report').report_action([], data=all_data)

    def generate_report_for_service_log(self):
        domain = []
        if self.from_date:
            domain.append(('date', '>=', self.from_date))
        if self.to_date:
            domain.append(('date', '<=', self.to_date))
        if self.product_service_type_id:
            domain.append(('product_service_type_id', '=', self.product_service_type_id.id))

        logs = self.env['dsl.service.log'].search(domain)

        data_list = []
        for log in logs:
            data_list.append({
                'employee': log.employee_id.name,
                'vendor': log.vendor_id.name,
                'product_service_type_id': log.product_service_type_id.name,
                'cost': log.cost,
                'state': log.state,
            })

        data = {
            'company_name': self.company_id.name,
            'company_logo': self.company_id.logo,
            'from_date': self.from_date or "Not specified",
            'to_date': self.to_date or "Not specified",
            'data_list': data_list,
        }

        return self.env.ref('dsl_service_maintenance.dsl_fuel_log_report').report_action([], data=data)
    
    
    
    def generate_purchase_request_report(self):
        # Handle dates properly (as datetime objects for correct comparison)
        from_date = self.from_date if self.from_date else None
        to_date = self.to_date if self.to_date else None

        all_data = {
            'company_name': self.env.company.name,  # Fetch the company name
            'company_logo': self.env.company.logo,  # Fetch the company logo (Base64 encoded)
            'company_country': self.company_id.country_id.name,
            'from_date': from_date.strftime('%d %B, %Y') if from_date else "Not specified",
            'to_date': to_date.strftime('%d %B, %Y') if to_date else "Not specified",
        }

        # Build the domain dynamically based on the provided filters
        domain = []
        if from_date:
            domain.append(('date_start', '>=', from_date))
        if to_date:
            domain.append(('date_start', '<=', to_date))
        if self.requested_by:
            domain.append(('requested_by', '=', self.requested_by.id))

        # Fetch data based on the dynamic domain
        requests = self.env['purchase.request.order'].search(domain)
        
        data_list = []
        for req in requests:
            data_list.append({
                'name': req.name,
                'requested_by': req.requested_by.name,
                'assigned_to': req.assigned_to.name if req.assigned_to else 'N/A',
                'state': req.state,
                'description': req.description or 'N/A',
                'date_start': req.date_start.strftime('%d %B, %Y') if req.date_start else 'Not specified'
            })

        all_data['data_list'] = data_list if data_list else []

        # Return the report action with the prepared data
        return self.env.ref('dsl_service_maintenance.purchase_request_report').report_action([], data=all_data)
