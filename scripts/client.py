"""Cliente mínimo de TaskFlow contra la API v1 (s10).

Script con httpx que ejercita los endpoints principales de /v1 de punta a punta contra un
servidor en localhost:8000: crea un par de tareas, lista el tablero, mueve una tarea,
comenta y consulta el tablero del proyecto. Uso: `python scripts/client.py`
(con el servidor levantado y los seeds cargados).
"""

import httpx

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        print("== health ==")
        print(client.get("/health").json())

        print("\n== crear tareas (proyecto 1) ==")
        t1 = client.post("/v1/tareas", json={"titulo": "Diseñar el tablero"}).json()
        t2 = client.post(
            "/v1/tareas",
            json={"titulo": "Escribir el README", "descripcion": "Breve"},
        ).json()
        print(t1)
        print(t2)

        print("\n== listar tareas (paginado) ==")
        print(client.get("/v1/tareas", params={"proyecto_id": 1, "limit": 5}).json())

        print("\n== mover la primera tarea a 'en progreso' ==")
        print(client.post(f"/v1/tareas/{t1['id']}/mover", json={"estado": "en progreso"}).json())

        print("\n== comentar la primera tarea (autor 1) ==")
        print(client.post(f"/v1/tareas/{t1['id']}/comentarios", json={"autor_id": 1, "texto": "Arranco"}).json())

        print("\n== tablero del proyecto 1 ==")
        tablero = client.get("/v1/proyectos/1/tablero").json()
        for columna, tareas in tablero["columnas"].items():
            print(f"  {columna}: {[t['titulo'] for t in tareas]}")


if __name__ == "__main__":
    main()
