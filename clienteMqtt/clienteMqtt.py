import asyncio, ssl, certifi, logging, os
import aiomqtt

logging.basicConfig(format='%(asctime)s - cliente mqtt - %(levelname)s:%(message)s', level=logging.INFO, datefmt='%d/%m/%Y %H:%M:%S %z')

async def suscribir(client, topico):
    await client.subscribe(topico)
    async for message in client.messages:
        logging.info(str(message.topic) + ": " + message.payload.decode("utf-8"))
    await asyncio.sleep(0)

async def publicar(client, topico):
    while True:
        await asyncio.sleep(5)
        await client.publish(topico, payload=2024)

async def main():
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    tls_context.verify_mode = ssl.CERT_REQUIRED
    tls_context.check_hostname = True
    tls_context.load_default_certs()

    async with aiomqtt.Client(
        os.environ['SERVIDOR'],
        port=8883,
        tls_context=tls_context,
    ) as client:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(publicar(client, os.environ['TOPICO_PUB']))
            tg.create_task(suscribir(client, os.environ['TOPICO_SUB']))
        
            contador = 0
            while True:
                logging.info("contador: " + str(contador))
                contador += 1
                await asyncio.sleep(3)
        
if __name__ == "__main__":
    asyncio.run(main())
