# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools


class ParkingAnalysis(models.Model):
    """ Parking Analysis """
    _name = 'parking.analysis'
    _auto = False

    ticket_type = fields.Char('Ticket type')
    start_time = fields.Datetime('Start time')
    end_time = fields.Datetime('End time')
    status = fields.Char('Status')
    create_date = fields.Datetime('Create date')
    description = fields.Char('Description')
    source = fields.Char('Source')
    amount = fields.Float('Amount', digits=(8, 2))
    parking_name = fields.Char('Parking name')
    parking_type = fields.Char('Parking type')
    zone_name = fields.Char('Zone name')
    date_created = fields.Datetime('Date Created')

    def init(self):

        """
            CRM Lead Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(self._cr, 'parking_analysis')
        self._cr.execute("""
                    CREATE OR REPLACE VIEW parking_analysis AS (
                    select s.a as date_created,
                    case when t.id is null then 1000 else t.id end,
                    t.ticket_type,
                    t.start_time,
                    t.end_time,
                    t.status,
                    t.create_date,
                    t.description,
                    t.source,
                    t.amount,
                    t.parking_name,
                    t.parking_type,
                    t.zone_name
                from
                (select	pt.id,
                    pt.ticket_type,
                    pt.start_time,
                    pt.end_time,
                    pt.status,
                    pt.create_date,
                    pt.description,
                    pt.source,
                    ph.price as amount,
                    p.parking_name,
                    p.parking_type,
                    z.name as zone_name
                    from parking_ticket pt
                    join parking p on pt.parking = p.id
                    join zone z on p.zone = z.id
                    join ticket_machine tm on pt.ticket_machine = tm.id
                    join price_hour ph on pt.price_hour = ph.id
                    join price_schedule_detail psd on ph.price_schedule_detail = psd.id
                    join payment_method pm on pt.payment_method = pm.id
                    WHERE pt.active = 'true') t
                    right join generate_series((select min(create_date::date) from parking_ticket)::timestamp,
                                              (select max(create_date::date) from parking_ticket), '1 days') as s(a)
                                              on t.create_date::date = s.a)
                    """)


        # tools.drop_view_if_exists(cr, 'parking_analysis')
        # cr.execute("""
        #             CREATE OR REPLACE VIEW parking_analysis AS (
        #             select s.a as date_created, t.*
        #             from
        #             (select	pt.id,
        #                 pt.ticket_type,
        #                 pt.start_time,
        #                 pt.end_time,
        #                 pt.status,
        #                 pt.create_date,
        #                 pt.description,
        #                 pt.source,
        #                 ph.price as amount,
        #                 p.parking_name,
        #                 p.parking_type,
        #                 z.name as zone_name
        #                 from parking_ticket pt
        #                 join parking p on pt.parking = p.id
        #                 join zone z on p.zone = z.id
        #                 join ticket_machine tm on pt.ticket_machine = tm.id
        #                 join price_hour ph on pt.price_hour = ph.id
        #                 join price_schedule_detail psd on ph.price_schedule_detail = psd.id
        #                 join payment_method pm on pt.payment_method = pm.id
        #                 WHERE pt.active = 'true') t
        #                 right join generate_series((select min(create_date::date) from parking_ticket)::timestamp,
        #                                           (select max(create_date::date) from parking_ticket), '1 days') as s(a)
        #                                           on t.create_date::date = s.a)
        #             """)


        # tools.drop_view_if_exists(cr, 'parking_analysis')
        # cr.execute("""
        #     CREATE OR REPLACE VIEW parking_analysis AS (
        #     select	pt.id,
        #         pt.ticket_type,
        #         pt.start_time,
        #         pt.end_time,
        #         pt.status,
        #         pt.create_date,
        #         pt.description,
        #         pt.source,
        #         ph.price as amount,
        #         p.parking_name,
        #         p.parking_type,
        #         z.name as zone_name
        #     from parking_ticket pt
        #     join parking p on pt.parking = p.id
        #     join zone z on p.zone = z.id
        #     join ticket_machine tm on pt.ticket_machine = tm.id
        #     join price_hour ph on pt.price_hour = ph.id
        #     join price_schedule_detail psd on ph.price_schedule_detail = psd.id
        #     join payment_method pm on pt.payment_method = pm.id
        #     WHERE pt.active = 'true')
        #     """)
