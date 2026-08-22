let isMoving = false;

function moveCarousel(direction, trackId) {
    if (isMoving) return;
    isMoving = true;

    const track = document.getElementById(trackId);
    const firstItem = track ? track.firstElementChild : null;
    
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

function chequearSesion() {
    const usuarioLogueado = localStorage.getItem("sesionActiva");
    const menuUsuario = document.getElementById("menu-usuario");
    const botonesSesion = document.getElementById("botones-sesion");

    if (menuUsuario) {
        menuUsuario.style.setProperty("display", usuarioLogueado === "true" ? "block" : "none", "important");
    }

    if (botonesSesion) {
        botonesSesion.style.setProperty("display", usuarioLogueado === "true" ? "none" : "flex", "important");
    }
}

document.addEventListener("DOMContentLoaded", chequearSesion);
window.addEventListener("pageshow", chequearSesion);

function cerrarSesion(event) {
    event.preventDefault();
    localStorage.removeItem("sesionActiva");
    window.location.reload();
}