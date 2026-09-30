// TaskFlow — Frontend del tablero (s11)
//
// Tablero ESTÁTICO y AISLADO: los datos son un array hardcodeado y toda la interacción
// manipula el DOM a mano (createElement / appendChild / mover nodos). Sin fetch, sin API,
// sin frameworks. El objetivo es entender el flujo HTML -> DOM -> render.

// --- Estado en memoria (fuente de datos hardcodeada) ---
const ESTADOS = ["backlog", "en progreso", "hecho"];

let siguienteId = 4;
const tareas = [
  { id: 1, titulo: "Diseñar el tablero", descripcion: "Columnas y tarjetas", estado: "hecho" },
  { id: 2, titulo: "Mover tarjetas con click", descripcion: "", estado: "en progreso" },
  { id: 3, titulo: "Escribir el README", descripcion: "Breve", estado: "backlog" },
];

// Mapa estado -> elemento de columna (el id del DOM reemplaza el espacio por guión).
function columnaDe(estado) {
  return document.getElementById("col-" + estado.replace(" ", "-"));
}

// --- Render: crea el nodo de una tarjeta a partir de una tarea ---
function crearTarjeta(tarea) {
  const div = document.createElement("div");
  div.className = "tarjeta";
  div.dataset.id = tarea.id; // guardamos el id en el DOM para reconocer la tarjeta

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

  // Click: avanza la tarea a la siguiente columna (y vuelve a backlog al final).
  div.addEventListener("click", () => avanzarEstado(tarea, div));
  return div;
}

// --- Mover: cambia el estado y MUEVE el nodo existente a la columna destino ---
function avanzarEstado(tarea, nodo) {
  const indice = ESTADOS.indexOf(tarea.estado);
  const nuevoEstado = ESTADOS[(indice + 1) % ESTADOS.length];
  tarea.estado = nuevoEstado; // actualizamos el estado en memoria
  columnaDe(nuevoEstado).appendChild(nodo); // movemos el mismo nodo de columna
}

// --- Crear: agrega una tarea al array y una tarjeta nueva al DOM (columna backlog) ---
function agregarTarea(titulo, descripcion) {
  const tarea = { id: siguienteId++, titulo, descripcion, estado: "backlog" };
  tareas.push(tarea);
  columnaDe(tarea.estado).appendChild(crearTarjeta(tarea));
}

// --- Render inicial: pinta las tarjetas hardcodeadas en sus columnas ---
function renderInicial() {
  for (const tarea of tareas) {
    columnaDe(tarea.estado).appendChild(crearTarjeta(tarea));
  }
}

// --- Cableado del form: submit crea la tarea en memoria (sin recargar la página) ---
const form = document.getElementById("form-tarea");
form.addEventListener("submit", (evento) => {
  evento.preventDefault(); // evita que el navegador recargue al enviar el form
  const inputTitulo = document.getElementById("input-titulo");
  const inputDesc = document.getElementById("input-desc");
  const titulo = inputTitulo.value.trim();
  if (!titulo) return;
  agregarTarea(titulo, inputDesc.value.trim());
  form.reset();
  inputTitulo.focus();
});

renderInicial();
