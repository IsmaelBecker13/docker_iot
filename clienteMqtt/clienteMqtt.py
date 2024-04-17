import asyncio, ssl, certifi, logging, os
import aiomqtt
import types

# https://github.com/python/typeshed/pull/11609
logging.basicConfig(format='%(asctime)s - task: %(taskName)s - %(levelname)s:%(message)s', level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S %z')

async def suscribir(client, topico):
    await client.subscribe(topico)
    async for message in client.messages:
        logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))

async def publicar(client, topico, contador):
    while True:
        await asyncio.sleep(5)
        await client.publish(topico, payload=contador.valor)
        logging.info(" publicando: " + str(contador.valor))

async def contar(contador):
    while True:
        contador.valor += 1
        logging.info(" el valor es: " + str(contador.valor))
        await asyncio.sleep(3)

async def main():
    # https://stackoverflow.com/a/41765294
    contador = types.SimpleNamespace()
    contador.valor = 0

    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    async with aiomqtt.Client(
        os.environ['SERVIDOR'],
        port = 8883,
        tls_context = tls_context,
    ) as client:
        # https://sbtinstruments.github.io/aiomqtt/subscribing-to-a-topic.html#multiple-queues
        async with asyncio.TaskGroup() as tg:
            tg.create_task(publicar(client, os.environ['TOPICO_PUB'],contador), name='publicador')
            tg.create_task(suscribir(client, os.environ['TOPICO_SUB']), name='suscriptor')
            tg.create_task(contar(contador), name='contador')                
        
if __name__ == "__main__":
    # https://stackoverflow.com/questions/70399670/how-to-shutdown-gracefully-on-keyboard-interrupt-when-an-asyncio-task-is-perform
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt. Canceling tasks...")
