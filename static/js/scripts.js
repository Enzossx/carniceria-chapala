let isMoving = false;

function moveCarousel(direction, trackId) {
    if (isMoving) return;
    isMoving = true;

    const track = document.getElementById(trackId);
    const firstItem = track.firstElementChild;
    
    if (!firstItem) {
        isMoving = false;
        return;
    }

    const itemStyle = window.getComputedStyle(firstItem);
    const marginRight = parseFloat(itemStyle.marginRight) || 0;
    const marginLeft = parseFloat(itemStyle.marginLeft) || 0;
    const itemWidth = firstItem.offsetWidth + marginRight + marginLeft; 

    const trackStyle = window.getComputedStyle(track);
    const gap = parseFloat(trackStyle.gap) || 0;
    const itemFullWidth = itemWidth + gap; 

    if (direction === 1) {
        track.style.transition = "transform 0.4s cubic-bezier(0.25, 1, 0.5, 1)";
        track.style.transform = `translateX(-${itemFullWidth}px)`;

        setTimeout(() => {
            track.style.transition = "none";
            track.appendChild(track.firstElementChild);
            track.style.transform = `translateX(0)`;
            isMoving = false;
        }, 400);
    } else {
        track.style.transition = "none";
        track.prepend(track.lastElementChild);
        track.style.transform = `translateX(-${itemFullWidth}px)`;

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                track.style.transition = "transform 0.4s cubic-bezier(0.25, 1, 0.5, 1)";
                track.style.transform = `translateX(0)`;
                setTimeout(() => { isMoving = false; }, 400);
            });
        });
    }
}

function irAlJuego(elemento) {
    const url = elemento.getAttribute("data-url");
    if (url) {
        window.location.href = url;
    } else {
        console.error("No se definió una URL");
    }
}

// --- LOGICA PARA MOSTRAR / OCULTAR EL DESPLEGABLE DE USUARIO ---

// Actualiza esta función en tu inicio.js

function chequearSesion() {
    const usuarioLogueado = localStorage.getItem("sesionActiva");
    const menuUsuario = document.getElementById("menu-usuario");
    const botonesSesion = document.getElementById("botones-sesion"); // <-- Capturamos los botones

    // Control del menú desplegable del usuario
    if (menuUsuario) {
        if (usuarioLogueado === "true") {
            menuUsuario.style.setProperty("display", "block", "important");
            console.log("Sesión activa detectada: Mostrando menú.");
        } else {
            menuUsuario.style.setProperty("display", "none", "important");
            console.log("Sin sesión: Ocultando menú.");
        }
    }

    // Control de los botones de Iniciar Sesión y Registrarse
    if (botonesSesion) {
        if (usuarioLogueado === "true") {
            // Si ya inició sesión, ocultamos los botones de ingreso
            botonesSesion.style.setProperty("display", "none", "important");
            console.log("Sesión activa: Ocultando botones de ingreso.");
        } else {
            // Si no hay sesión, los botones deben ser visibles usando flex de Bootstrap
            botonesSesion.style.setProperty("display", "flex", "important");
            console.log("Sin sesión: Mostrando botones de ingreso.");
        }
    }
}

// Ejecutar cuando el HTML termine de cargar
document.addEventListener("DOMContentLoaded", chequearSesion);

// Ejecutar por si acaso el navegador recupera la página desde el historial/caché
window.addEventListener("pageshow", chequearSesion);
function cerrarSesion(event) {
    event.preventDefault();
    localStorage.removeItem("sesionActiva"); // Elimina la marca de la sesión
    window.location.reload(); // Recarga la página para aplicar los cambios visuales
}