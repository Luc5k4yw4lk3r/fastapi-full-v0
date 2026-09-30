// TaskFlow — Frontend del tablero (s12)
//
// Ahora el tablero se conecta a la API v1 real (s10) con fetch + async/await.
// Mantenemos el enfoque de s11 (manipular el DOM a mano: crear/mover nodos), pero cada
// acción se confirma contra el servidor y el estado del cliente (array `tareas`) se
// mantiene en sincronía. La API corre en otro puerto (8000) -> por eso hace falta CORS.

const API = "http://localhost:8000";
const PROYECTO_ID = 1;
const ESTADOS = ["backlog", "en progreso", "hecho"];

// Estado del cliente: la lista de tareas que tenemos cargada en memoria.
let tareas = [];

function columnaDe(estado) {
  return document.getElementById("col-" + estado.replace(" ", "-"));
}

// --- Crea el nodo DOM de una tarjeta ---
function crearTarjeta(tarea) {
  const div = document.createElement("div");
  div.className = "tarjeta";
  div.dataset.id = tarea.id;

  const titulo = document.createElement("div");
  titulo.className = "titulo";
  titulo.textContent = tarea.titulo;
  div.appendChild(titulo);

  if (tarea.descripcion) {
    const desc = document.createElement("div");
    desc.className = "desc";
    desc.textContent = tarea.descripcion;
    div.appendChild(desc);
  }

  div.addEventListener("click", () => mover(tarea, div));
  return div;
}

// --- Pinta el tablero completo a partir del estado (solo en la carga inicial) ---
function pintarTablero() {
  for (const estado of ESTADOS) {
    // Limpia las tarjetas previas de la columna (conserva el <h2>).
    columnaDe(estado).querySelectorAll(".tarjeta").forEach((n) => n.remove());
  }
  for (const tarea of tareas) {
    columnaDe(tarea.estado).appendChild(crearTarjeta(tarea));
  }
}

// --- Cargar el tablero real desde la API (GET) ---
async function cargarTablero() {
  const resp = await fetch(`${API}/v1/tareas?proyecto_id=${PROYECTO_ID}&limit=100`);
  if (!resp.ok) {
    console.error("No se pudo cargar el tablero:", resp.status);
    return;
  }
  const pagina = await resp.json();
  tareas = pagina.items;
  pintarTablero();
}

// --- Mover: confirma el nuevo estado en la API (POST .../mover) y mueve el nodo ---
async function mover(tarea, nodo) {
  const indice = ESTADOS.indexOf(tarea.estado);
  const nuevoEstado = ESTADOS[(indice + 1) % ESTADOS.length];
  const resp = await fetch(`${API}/v1/tareas/${tarea.id}/mover`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado: nuevoEstado }),
  });
  if (!resp.ok) {
    console.error("No se pudo mover la tarea:", resp.status);
    return;
  }
  const actualizada = await resp.json();
  tarea.estado = actualizada.estado; // sincroniza el estado del cliente
  columnaDe(tarea.estado).appendChild(nodo); // mueve el mismo nodo de columna
}

// --- Crear: POST a la API y, si sale bien, agrega la tarjeta al DOM ---
async function crear(titulo, descripcion) {
  const resp = await fetch(`${API}/v1/tareas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ titulo, descripcion, proyecto_id: PROYECTO_ID }),
  });
  if (!resp.ok) {
    console.error("No se pudo crear la tarea:", resp.status);
    return;
  }
  const creada = await resp.json();
  tareas.push(creada);
  columnaDe(creada.estado).appendChild(crearTarjeta(creada));
}

// --- Cableado del form ---
const form = document.getElementById("form-tarea");
form.addEventListener("submit", (evento) => {
  evento.preventDefault();
  const inputTitulo = document.getElementById("input-titulo");
  const inputDesc = document.getElementById("input-desc");
  const titulo = inputTitulo.value.trim();
  if (!titulo) return;
  crear(titulo, inputDesc.value.trim());
  form.reset();
  inputTitulo.focus();
});

// Carga inicial del tablero desde la API.
cargarTablero();
