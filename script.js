// Функция управления светом (включение/выключение)
function controlLight(action) {
    fetch(`/light/${action}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // После изменения состояния света перезагружаем страницу
        location.reload();
    });
}

// Функция для установки яркости
function setBrightness(brightness) {
    document.getElementById('brightness').textContent = brightness; // Обновляем текстовое отображение яркости
    fetch('/light/brightness', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `brightness=${brightness}`
    });
}