# Cierre conceptual (s12): SPA vs multipágina, y dónde encajan React/Next

Cierre sin código del proyecto TaskFlow. Ubica lo que construimos (frontend vanilla que
consume la API v1 por `fetch`) dentro del panorama más amplio del desarrollo web.

## Multipágina (MPA) tradicional
- El **servidor** genera una página HTML completa por cada navegación; cada click a otra
  sección es una request que devuelve un documento nuevo y el navegador **recarga**.
- Simple, muy buen SEO y primer render rápido; el estado vive en el servidor/URL.
- Contra: cada interacción "grande" implica recargar y volver a pedir todo.

## Single Page Application (SPA)
- Se carga **una** página y, a partir de ahí, JavaScript actualiza el DOM y pide **datos**
  (no HTML) a una API por `fetch`. La navegación no recarga la página.
- Es exactamente el modelo de TaskFlow en s12: un `index.html` + `app.js` que trae las
  tareas de `/v1/...` y re-dibuja el tablero manteniendo el estado en el cliente.
- Pro: interacción fluida, la API queda desacoplada del frontend (misma API para web, móvil
  o agentes). Contra: más JS en el cliente, SEO y primer render requieren más cuidado.

## ¿Dónde encajan React / Next?
- **React** es una librería para construir UIs a partir de **componentes** y un **estado**;
  en vez de mover nodos del DOM a mano (lo que hicimos en s11/s12), describís cómo se ve la
  UI para un estado y React calcula y aplica los cambios mínimos al DOM. Es la versión
  industrializada del "re-render desde el estado" que discutimos como trade-off en s11.
- **Next.js** es un framework sobre React que suma ruteo, renderizado en el servidor
  (SSR) / generación estática (SSG), y convenciones de proyecto. Sirve para tener lo mejor
  de MPA (SEO, primer render) y de SPA (interacción rica) a la vez.
- **Cuándo dar el salto:** cuando la UI crece (muchas vistas, estado compartido, formularios
  complejos) y mantener el DOM a mano se vuelve costoso y propenso a errores. Para TaskFlow,
  hacerlo a mano fue lo correcto **pedagógicamente**: se ve el mecanismo real (HTML → DOM →
  fetch → render) que los frameworks luego abstraen.

## Qué queda construido (entregable final)
TaskFlow full-stack: **frontend vanilla** (tablero interactivo) → **API v1 REST** (FastAPI,
en capas) → **PostgreSQL** (en Docker), con CORS resuelto para conectar front y API en
puertos distintos. Todo evolucionado de forma incremental, una sesión = un tag (s05 → s12).
