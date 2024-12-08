from odoo import models, fields, api

class PaymentWizard(models.TransientModel):
    _name = 'payment.wizard'
    _description = 'Payment Wizard'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    amount = fields.Float(string='Amount', required=True)
    payment_type = fields.Selection([
        ('inbound', 'Receive'),
        ('outbound', 'Send'),
    ], string='Payment Type', required=True, default='inbound')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True)

    def create_payment(self):
        """
        Create a payment record in account.payment model.
        """
        # Retrieve a default payment method line for the journal and payment type
        payment_method_line = self.env['account.payment.method.line'].search([
            ('payment_method_id.payment_type', '=', self.payment_type),
            ('journal_id', '=', self.journal_id.id),
        ], limit=1)

        if not payment_method_line:
            raise ValueError("No payment method line found for the selected journal and payment type.")

        # Create the payment record
        payment = self.env['account.payment'].create({
            'partner_id': self.partner_id.id,
            'amount': self.amount,
            'payment_method_line_id': payment_method_line.id,
            'payment_type': self.payment_type,
            'journal_id': self.journal_id.id,
            'date': self.payment_date,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'domain': [('id', '=', payment.id)],
            'context': {'create': False},
        }
