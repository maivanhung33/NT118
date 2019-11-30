from injector import singleton, Module, provider
from kombu import Connection, Producer
from starlette.config import Config


class AMQPPublisherProvider(Module):

    @provider
    @singleton
    def provide_connection(self, config: Config) -> Connection:
        amqp_url = config('AMQP_URL',
                          cast=str,
                          default='amqp://meete:p4ssw0rd@localhost:5672/meete')

        conn = Connection(amqp_url)
        return conn

    @provider
    @singleton
    def provide(self, conn: Connection) -> Producer:
        channel = conn.channel()
        producer = Producer(channel)
        return producer
