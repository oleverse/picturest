<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js"></script>
// Знаходимо кнопку за допомогою ідентифікатора "backBtn"
var backButton = document.getElementById("backBtn");
backButton.addEventListener("click", function() {
    // Перенаправляємо користувача на головну сторінку (замініть "/index.html" на фактичний URL головної сторінки)
    window.location.href = "/";
});

// Функція для обробки логіну та збереження токенів у локальному сховищі
async function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  // Виконати POST-запит на сервер для логіну
  const response = await fetch('/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    headers: { 'Content-Type': 'application/json' },
  });

  const data = await response.json();

  // Зберегти токени у локальному сховищі браузера
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);

  // Перенаправити користувача на домашню сторінку
  window.location.href = "/";
}