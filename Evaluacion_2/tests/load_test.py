import asyncio
import time
import statistics

import httpx


URL = "http://127.0.0.1:9102/productos"

TOTAL_REQUESTS = 100
CONCURRENCY = 10


latencies = []
errors = 0


async def make_request(client, semaphore):
    global errors

    async with semaphore:
        start = time.perf_counter()

        try:
            response = await client.get(URL)

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(elapsed)

            if response.status_code != 200:
                errors += 1

        except Exception:
            elapsed = (
                time.perf_counter() - start
            ) * 1000

            latencies.append(elapsed)

            errors += 1


async def main():

    semaphore = asyncio.Semaphore(
        CONCURRENCY
    )

    start_total = time.perf_counter()

    async with httpx.AsyncClient(
        timeout=10.0
    ) as client:

        tasks = [
            make_request(
                client,
                semaphore
            )
            for _ in range(TOTAL_REQUESTS)
        ]

        await asyncio.gather(*tasks)

    total_time = (
        time.perf_counter()
        - start_total
    )

    successful_requests = (
        TOTAL_REQUESTS - errors
    )

    throughput = (
        successful_requests / total_time
        if total_time > 0
        else 0
    )

    average_latency = (
        statistics.mean(latencies)
        if latencies
        else 0
    )

    sorted_latencies = sorted(
        latencies
    )

    if sorted_latencies:
        index_p95 = int(
            len(sorted_latencies) * 0.95
        ) - 1

        p95 = sorted_latencies[
            max(index_p95, 0)
        ]
    else:
        p95 = 0

    print()
    print("=== PRUEBA DE CARGA ===")
    print(
        f"URL: {URL}"
    )
    print(
        f"Solicitudes totales: {TOTAL_REQUESTS}"
    )
    print(
        f"Concurrencia: {CONCURRENCY}"
    )
    print(
        f"Tiempo total: {total_time:.2f} s"
    )
    print(
        f"Solicitudes exitosas: {successful_requests}"
    )
    print(
        f"Errores: {errors}"
    )
    print(
        f"Latencia promedio: {average_latency:.2f} ms"
    )
    print(
        f"Latencia p95: {p95:.2f} ms"
    )
    print(
        f"Throughput: {throughput:.2f} req/s"
    )
    print()


if __name__ == "__main__":
    asyncio.run(main())