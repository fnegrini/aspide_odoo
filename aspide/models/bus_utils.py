# -*- coding: utf-8 -*-


def send_bus_notification(env, partner, subject, body, type):

    env['bus.bus']._sendone(partner, 'simple_notification', 
        {
            'title':subject, 
            'message':body,
            'sticky': True,
            'type': type
        })