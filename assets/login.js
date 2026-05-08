const API = "http://127.0.0.1:8000";

document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.querySelector("input[type=email]").value;
    const senha = document.querySelector("input[type=password]").value;

    const formData = new FormData();
    formData.append("email", email);
    formData.append("senha", senha);

    const res = await fetch(API + "/login", {
        method: "POST",
        body: formData
    });

    if (res.status === 200) {
        window.location.href = "templates/agenda.html";
    } else {
        alert("Login inválido");
    }

    window.onload = () => {
    loadPets();
    loadEventos();
    loadFuncionarios();
};
});