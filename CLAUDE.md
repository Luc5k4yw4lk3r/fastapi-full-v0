# TaskFlow — Guía del proyecto

TaskFlow es una aplicación de gestión de tareas para equipos (tipo mini-Trello),
**sin ningún componente de IA/LLM**. Es el hilo conductor de las sesiones **S05 a S12**
del Módulo 7 (Fundamentos de Software + System Design). Se construye de forma
**incremental**: una sesión = un incremento = un tag de git.

El alumno debe poder **defender** el código, no solo ejecutarlo.

---

## Reglas del proyecto

- **Regla de oro — no te adelantes:** solo implementás el alcance de la sesión activa,
  definido en `sessions/sXX.md`. Si algo pertenece a una sesión futura (auth, RBAC,
  caching, load balancing, CI, tests exhaustivos, frameworks de frontend como
  React/Next/Vite), lo mencionás como "viene después" pero NO lo implementás, aunque
  parezca buena práctica.

- **Stack de infraestructura:** PostgreSQL en Docker (docker-compose) desde el inicio
  del proyecto. El compose se crea en s05 y es la única forma soportada de levantar la
  base; la app se conecta a Postgres recién en s07 (antes usa almacenamiento en memoria,
  para entender la capa repository sin ruido).

- **Arquitectura en capas siempre:** router → service → repository → datos. El dominio
  nunca importa detalles de persistencia.

- **Frontend en vanilla JS:** cuando llegue (s11-s12), el frontend es HTML + JavaScript
  puro manipulando el DOM. Nada de frameworks ni build tools.

- **Enseñás mientras construís:** cada archivo que generás o modificás lo explicás en
  2-3 líneas (qué es, qué componente resuelve, por qué va en esa capa). El usuario es un
  alumno que debe poder defender el código, no solo ejecutarlo.

- **Trade-offs explícitos:** antes de cada decisión de diseño (almacenamiento,
  estructura, protocolo), presentás las alternativas y preguntás; la decisión tomada se
  registra en `docs/trade-offs.md`.

- **Diagramas como entregable:** los diagramas se escriben en Mermaid dentro de
  `docs/diagrams/` y se actualizan en la misma sesión en que cambia lo que describen.

- **Commits:** mensajes en español, imperativos, con prefijo de la sesión activa
  (`s05: agregar endpoint de mover tarea`), un commit por avance coherente. Sin líneas
  `Co-Authored-By` ni menciones a Claude.

---

## Protocolo de sesión

- **Inicio de sesión.** El usuario inicia con "arrancamos la sesión sXX". Vos: leés
  `sessions/sXX.md`, verificás que el tag de la sesión anterior existe, proponés un plan
  de trabajo para la sesión y esperás confirmación antes de tocar código.

- **Cierre de sesión** ("cerramos la sesión"): verificás que los entregables del archivo
  de alcance están completos (código + diagramas + bitácora), hacés el commit final y
  creás el tag `sXX`.

---

## Referencia rápida

| Sesión | Foco | Tag |
|--------|------|-----|
| s05 | Prototipo mínimo (FastAPI en capas, memoria) + compose Postgres | `s05` |
| s06 | Decisión de almacenamiento + modelo de dominio | `s06` |
| s07 | PostgreSQL real (ORM en repository) | `s07` |
| s08 | Datos para agentes (frescura, seeds, endpoint autocontenido) | `s08` |
| s09 | Contrato de la API v1 (top-down) | `s09` |
| s10 | API v1 completa (cierra el backend) | `s10` |
| s11 | Frontend: del HTML al DOM (estático) | `s11` |
| s12 | Conectar frontend a la API (**entregable final**) | `s12` |

El alcance detallado de cada sesión vive en `sessions/sXX.md`.
