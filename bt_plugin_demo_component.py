import bt2
import datetime
from termcolor import colored


@bt2.plugin_component_class
class backtracer(bt2._UserSinkComponent):
    def __init__(self, params):
        self._indent = 0
        self._add_input_port('my_input_port')
        self._last_timestamp = None

    def _port_connected(self, port, other_port):
        self._iterator = port.connection.create_notification_iterator(
            [bt2.EventNotification])
        return True

    def _on_entry(self, notification):
        self._indent += 1
        self._print_time(notification)
        print(colored(notification.event['debug_info']['func'][:-2],
                      attrs=['bold']) + '() {')

    def _on_exit(self, notification):
        self._print_time(notification)
        print('}')
        self._indent -= 1

    def _print_time(self, notification):
        event = notification.event
        clock_class = list(notification.clock_class_priority_map)[0]
        timestamp_ns = event.clock_value(clock_class).ns_from_epoch
        if self._last_timestamp is None:
            time_ui = str(datetime.datetime.fromtimestamp(
                event.clock_value(clock_class).ns_from_epoch / 1E9))
        else:
            delta = timestamp_ns - self._last_timestamp
            time_ui = '+{} ns'.format(delta)
            time_ui = '{:>26}'.format(time_ui)
            if delta >= 2000:
                time_ui = colored(time_ui, 'red', attrs=['bold'])

        print(time_ui + '  ' * self._indent, end='')
        self._last_timestamp = timestamp_ns

    def _consume(self):
        notification = next(self._iterator)
        if notification.event.name == 'lttng_ust_cyg_profile_fast:func_entry':
            self._on_entry(notification)
        elif notification.event.name == 'lttng_ust_cyg_profile_fast:func_exit':
            self._on_exit(notification)


bt2.register_plugin(__name__, 'demo')
