# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models
from datetime import date, datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class ParkingStatus(models.Model):
    _name = "parking.status"
    _description = "Parking Status"
    _auto = False
    _order = "last_ticket_date desc, status desc"

    name = fields.Char('Name', readonly=True)
    zone = fields.Char('Zone', readonly=True)
    last_ticket_id = fields.Many2one('parking.ticket', 'Last ticket', readonly=True)
    status = fields.Char('Status', readonly=True)
    last_ticket_start_time = fields.Float('Start time', readonly=True)
    last_ticket_end_time = fields.Float('End time', readonly=True)
    last_ticket_amount = fields.Float('Last ticket amount', readonly=True)
    last_ticket_date = fields.Datetime('Last ticket date', readonly=True)
    hide_last_ticket_date = fields.Boolean()
    today = fields.Datetime('Today', readonly=True)
    today_tickets_count = fields.Integer('Today tickets count', digits=(8, 2), compute='_get_today_tickets_count')
    today_tickets_amount = fields.Float('Today tickets amount', digits=(8, 2), compute='_get_today_tickets_amount')

    @api.one
    def _get_today_tickets_count(self):
        today = date.today().strftime(DF)
        self.today_tickets_count = self.env['parking.ticket'] \
            .search_count([('parking_id', '=', self.id), ('create_date', '>=', today)])

    @api.one
    def _get_today_tickets_amount(self):
        today = date.today().strftime(DF)
        today_tickets = self.env['parking.ticket'] \
            .search([('parking_id', '=', self.id), ('create_date', '>=', today)])
        for ticket in today_tickets:
            self.today_tickets_amount += ticket.price_hour_id.price

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, 'parking_status')
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW parking_status AS (
                SELECT DISTINCT ON (tab.id) tab.id,
                    tab.name,
                    tab.zone,
                    tab.status,
                    tab.last_ticket_id,
                    CASE
                        WHEN tab.status = 'Ocupado' THEN tab.last_ticket_start_time
                        ELSE NULL
                    END AS last_ticket_start_time,
                    CASE
                        WHEN tab.status = 'Ocupado' THEN tab.last_ticket_end_time
                        ELSE NULL
                    END AS last_ticket_end_time,
                    tab.last_ticket_amount,
                    CASE
                        WHEN tab.last_ticket_date IS NULL THEN '1970-01-01 00:00:00'::timestamp
                        ELSE tab.last_ticket_date
                    END AS last_ticket_date,
                    CASE
                        WHEN tab.last_ticket_date IS NULL THEN True
                        ELSE False
                    END AS hide_last_ticket_date,
                    tab.today
                FROM
                (
                    SELECT
                        p.id AS id,
                        p.name,
                        z.name AS zone,
                        pt.id AS last_ticket_id,
                        date_part('hour', pt.start_time) + (date_part('minute', pt.start_time) / 60) AS last_ticket_start_time,
                        date_part('hour', pt.end_time) + (date_part('minute', pt.end_time) / 60) AS last_ticket_end_time,
                        h.price AS last_ticket_amount,
                        CASE
                        WHEN (p.free_at IS NOT NULL AND p.free_at > NOW()) THEN 'Ocupado'
                        ELSE 'Liberado'
                        END AS status,
                        pt.start_time AS last_ticket_date,
                        NOW() AS today
                    FROM public.parking_parking p
                    JOIN public.parking_zone z ON p.zone_id = z.id
                    LEFT JOIN public.parking_ticket pt ON p.id = pt.parking_id
                    LEFT JOIN public.parking_price_hour h ON pt.price_hour_id = h.id
                ) AS tab
                ORDER BY id, last_ticket_date desc
            )
        """)
