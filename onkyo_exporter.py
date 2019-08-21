#!/usr/bin/env python3

import eiscp
import sys
import time

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

class onkyo_collector(object):
    def __init__(self, target):
        self._target = target
        self.up = GaugeMetricFamily('onkyo_up', 'Was the last amplifier query successful', labels=['node'])

    def collect(self):

        up = GaugeMetricFamily('onkyo_up', 'Was the last amplifier query successful', labels=['node'])
        duration = GaugeMetricFamily('onkyo_collection_duration_seconds', 'Time spent collecting data', labels=['node'])
        power = GaugeMetricFamily('onkyo_power', 'Power status', labels=['model', 'identifier', 'node'])
        mute = GaugeMetricFamily('onkyo_mute', 'Muting status', labels=['model', 'identifier', 'node'])
        volume = GaugeMetricFamily('onkyo_volume', 'Master volume', labels=['model', 'identifier', 'node'])

        start = time.time()

        try:
            with eiscp.eISCP(self._target) as receiver:
                model = receiver.info['model_name']
                identifier = receiver.info['identifier']

                try:
                    power.add_metric([model, identifier, self._target],
                        0 if receiver.command('system-power query')[1][1] == 'off' else 1)
                    mute.add_metric([model, identifier, self._target],
                        0 if receiver.command('audio-muting query')[1] == 'off' else 1)
                    volume.add_metric([model, identifier, self._target],
                        receiver.command('master-volume query')[1])
                except:
                    print('Error: {}'.format(sys.exc_info()))

                up.add_metric(labels=[self._target], value=1)
                            
                for metric in [up, power, mute, volume]:
                    yield metric
        except:
            print('Error: {}'.format(sys.exc_info()))
            up.add_metric([self._target], 0)
            yield up

        end = time.time()
        duration.add_metric([self._target], end - start)
        yield duration

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: onkyo_exporter.py [ hostname | ip ]\n")
        sys.exit(1)
    
    REGISTRY.register(onkyo_collector(sys.argv[1]))
    start_http_server(8080)
    while True: time.sleep(1)