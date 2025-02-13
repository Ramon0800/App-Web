/* Evento para recibir imagenes */
const eventSource = new EventSource("/events");
eventSource.onmessage = function (event) {
  const imageurl = event.data;
  document.getElementById("image").src = imageurl;
};

/* eliminacion de rutas*/
document.addEventListener("DOMContentLoaded", function () {
  const deletebutton = document.querySelectorAll(".delete-btn");
  deletebutton.forEach((button) => {
    button.addEventListener("click", function () {
      const Id = this.getAttribute("data-id");
      deleteId(Id);
    });
  });
});

function deleteId(itemid) {
  const url = `/flug/eliminar/${itemid}`;
  fetch(url, { method: "DELETE" });
  const button = document.querySelector(`button[data-id='${itemid}']`);
  const container = button.closest(".container");
  container.remove();
}

/* Seleccion de ruta para dar inicio a la grabacion*/

document.addEventListener("DOMContentLoaded", function () {
  const postbutton = document.querySelectorAll(".post-btn");
  postbutton.forEach((button) => {
    button.addEventListener("click", function () {
      const Id = this.getAttribute("post-id");
      postId(Id);
    });
  });
});

function postId(itemid) {
  const url = `/flug/Ejecution/${itemid}`;
  fetch(url, { method: "POST" });
  const detenerbutton = document.getElementById("detener-btn");
  detenerbutton.disabled = false;
}

/*Control para detener la grabacion*/

document.addEventListener("DOMContentLoaded", function () {
  const detenerbutton = document.getElementById("detener-btn");
  detenerbutton.addEventListener("click", function () {
    const url = `/flug/detener_ejecution`;
    fetch(url, { method: "GET" });
    detenerbutton.disabled = true;
  });
});

/* Evento para recibir notificaciones */

const notificationSource = new EventSource("/flug/notifications");
notificationSource.onmessage = function (event) {
  const message = event.data;
  const notificationdiv = document.getElementById("notifications");
  const newnotification = document.createElement("p");
  newnotification.textContent = message;
  notificationdiv.appendChild(newnotification);
  setTimeout(() => {
    notificationdiv.removeChild(newnotification);
  }, 3000);
};
