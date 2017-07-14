# -*- coding: utf-8 -*-

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date, datetime, timedelta

import geojson

from openerp import api, fields
from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields


class Parking(geo_model.GeoModel):
    _name = 'parking.parking'

    name = fields.Char('Name')
    parking_number = fields.Integer('Parking number', unique=True, required=True)
    parking_type = fields.Selection([
        ('STANDARD', 'STANDARD'),
        ('PREFERENCE', 'PREFERENCE'),
        ('VIP', 'VIP'),
    ], 'Parking type', required=True, default='STANDARD')
    zone_id = fields.Many2one('parking.zone', string="Zone", ondelete='restrict', required=True)
    street_id = fields.Many2one('parking.street', string="Street", ondelete='restrict', required=True)
    next_street_id = fields.Many2one('parking.street', string="Next street", ondelete='restrict', required=True)
    previous_street_id = fields.Many2one('parking.street', string="Previous street", ondelete='restrict', required=True)
    latitude = fields.Float('Latitude')
    longitude = fields.Float('Longitude')
    free_at = fields.Datetime('Free at')
    description = fields.Char('Description')
    active = fields.Boolean('Active', required=True, default=True)
    status = fields.Char('Status', compute='_get_status')
    last_ticket_start_time = fields.Float('Start time', compute='_get_last_ticket_start_time', store=True)
    last_ticket_end_time = fields.Float('End time', compute='_get_last_ticket_end_time', store=True)
    today_tickets_count = fields.Integer('Today tickets count', compute='_get_today_tickets_count')
    last_ticket_amount = fields.Float('Last ticket amount', digits=(8, 2), compute='_get_last_ticket_amount')
    last_ticket_date = fields.Datetime('Last ticket date', compute='_get_last_ticket_date')
    today_tickets_amount = fields.Float('Today tickets amount', digits=(8, 2), compute='_get_today_tickets_amount')
    coordinate = geo_fields.GeoPoint('Coordinate')

    @api.one
    def _get_status(self):
        dt_now = datetime.utcnow() - timedelta(hours=4)
        self.status = 'Liberado'
        if self.free_at and dt_now < datetime.strptime(self.free_at, "%Y-%m-%d %H:%M:%S"):
            self.status = 'Ocupado'

        # if not self.free_at or dt_now >= datetime.strptime(self.free_at, "%Y-%m-%d %H:%M:%S"):
        #     self.status = 'Liberado'
        # elif dt_now >= datetime.strptime(self.free_at, "%Y-%m-%d %H:%M:%S"):
        #     self.status = 'Liberado'
        # else:
        #     self.status = 'Ocupado'

    @api.one
    def _get_last_ticket_start_time(self):
        if self.status == 'Ocupado':
            last_ticket = self.env['parking.ticket'].search([('parking_id', '=', self.id)], order="id desc", limit=1)
            if len(last_ticket) > 0:
                str_time = last_ticket[0].start_time[11:16].split(":")
                self.last_ticket_start_time = float(str_time[0]) + float(str_time[1])/60
                # start_dt = datetime.strptime(last_ticket[0].start_time, "%Y-%m-%d %H:%M:%S")
                # self.last_ticket_start_time = datetime.strftime(start_dt, "%H:%M")

    @api.one
    def _get_last_ticket_end_time(self):
        if self.status == 'Ocupado':
            last_ticket = self.env['parking.ticket'].search([('parking_id', '=', self.id)], order="id desc", limit=1)
            if len(last_ticket) > 0:
                str_time = last_ticket[0].end_time[11:16].split(":")
                self.last_ticket_end_time = float(str_time[0]) + float(str_time[1])/60
                # end_dt = datetime.strptime(last_ticket[0].end_time, "%Y-%m-%d %H:%M:%S")
                # self.last_ticket_end_time = datetime.strftime(end_dt, "%H:%M")

    @api.one
    def _get_today_tickets_count(self):
        today = date.today().strftime(DF)
        self.today_tickets_count = self.env['parking.ticket'] \
            .search_count([('parking_id', '=', self.id), ('create_date', '>=', today)])

    @api.one
    def _get_last_ticket_amount(self):
        last_ticket = self.env['parking.ticket'].search([('parking_id', '=', self.id)], order="id desc", limit=1)
        if len(last_ticket) > 0:
            self.last_ticket_amount = last_ticket[0].price_hour_id.price

    @api.one
    def _get_last_ticket_date(self):
        last_ticket = self.env['parking.ticket'].search([('parking_id', '=', self.id)], order="id desc", limit=1)
        if len(last_ticket) > 0:
            self.last_ticket_date = last_ticket[0].start_time

    @api.one
    def _get_today_tickets_amount(self):
        today = date.today().strftime(DF)
        today_tickets = self.env['parking.ticket']\
            .search([('parking_id', '=', self.id), ('create_date', '>=', today)])
        for ticket in today_tickets:
            self.today_tickets_amount += ticket.price_hour_id.price

    @api.onchange('coordinate')
    def get_latitude(self):
        if self.coordinate:
            x, y = geojson.loads(self.coordinate).coordinates
            self.latitude = x
            self.longitude = y

    @api.onchange('street_id', 'parking_number')
    def _get_name(self):
        if self.street_id:
            self.name = self.street_id.code + str(self.parking_number).zfill(3)

    _sql_constraints = [
        ('number_parking_uniq', 'unique(street_id, parking_number)', 'The number of the parking must be unique per street!'),
    ]
