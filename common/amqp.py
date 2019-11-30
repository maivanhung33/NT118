import logging
from typing import Type, Optional, Dict

from kombu import Producer

LOGGER = logging.getLogger(__name__)


class Publisher:
    def __init__(self, producer: Producer):
        self.producer = producer

    @property
    def binding(self) -> Dict[Type, str]:
        return {}

    def publish(self, body, routing_key: Optional[str] = None):
        if routing_key is None and type(body) in self.binding:
            routing_key = self.binding[type(body)]
        if routing_key is None:
            raise ValueError('unspecified routing key')
        return self.producer.publish(body=body,
                                     routing_key=routing_key,
                                     retry=True,
                                     retry_policy={'interval_start': 0, 'interval_step': 2, 'interval_max': 30,
                                                   'max_retries': 30})
