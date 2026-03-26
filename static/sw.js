self.addEventListener('install', (e) => {
  console.log('[Service Worker] Instalado com sucesso!');
});

self.addEventListener('fetch', (e) => {
  // Mantém a requisição normal para a internet/API
});