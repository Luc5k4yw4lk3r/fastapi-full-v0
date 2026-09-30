"""Cliente mínimo de TaskFlow (s05).

Script con httpx que ejercita los tres endpoints de punta a punta contra un servidor
corriendo en localhost:8000: crea un par de tareas, lista el tablero, mueve una tarea de
estado y vuelve a listar. Sirve para probar la API sin depender del navegador ni de
Swagger. Uso: `python scripts/client.py` (con el servidor levantado).
"""

import httpx

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
        print("== health ==")
        print(client.get("/health").json())

        print("\n== crear tareas ==")
        t1 = client.post("/tasks", json={"titulo": "Diseñar el tablero"}).json()
        t2 = client.post(
            "/tasks",
            json={"titulo": "Escribir el README", "descripcion": "Breve"},
        ).json()
        print(t1)
        print(t2)

        print("\n== listar tareas ==")
        for tarea in client.get("/tasks").json():
            print(tarea)

        print("\n== mover la primera tarea a 'en progreso' ==")
        movida = client.post(
            f"/tasks/{t1['id']}/move",
            json={"estado": "en progreso"},
        ).json()
        print(movida)

        print("\n== listar tareas (después de mover) ==")
        for tarea in client.get("/tasks").json():
            print(tarea)


if __name__ == "__main__":
    main()
