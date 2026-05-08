const CACHE_NAME = "salvar-v1";
// Lista de archivos vitales para que la app cargue
const ASSETS = ["/", "https://jsdelivr.net", "https://unpkg.com"];

// Instalación: Guarda los archivos en caché
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

// Estrategia: Cache First (Busca en caché, si no hay, ve a internet)
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
