// js/theme-switcher.js
(function(){
  const KEY = 'modo'; // Chave para o localStorage
  const LIGHT_CLASS = 'light-theme'; // Classe CSS que ativa o tema claro

  // 1. Função que aplica o modo (claro/escuro)
  // m = 1 (Claro), m = 0 (Escuro)
  function applyModo(m) {
    
    // *** MUDANÇA IMPORTANTE: Aplicar na tag <html> (documentElement) ***
    document.documentElement.classList.toggle(LIGHT_CLASS, m === 1);
    
    // Atualiza o ícone do botão
    const button = document.getElementById('themeToggleButton');
    if (button) {
      button.innerHTML = (m === 1) ? '🌙' : '☀️';
    }
  }

  // 2. Função global para LER o modo salvo
  window.getModo = function() {
    try {
      return Number(localStorage.getItem(KEY)) || 0; 
    } catch(e){ 
      return 0; // Fallback para modo escuro
    }
  };
  
  // 3. Função global para DEFINIR o modo
  window.setModo = function(m) {
    m = Number(m) === 1 ? 1 : 0; // Garante que seja 0 ou 1
    try {
      localStorage.setItem(KEY, String(m)); // Salva no localStorage
    } catch(e){}
    
    applyModo(m); // Aplica a mudança visual
  };

  // 4. LÓGICA DE INICIALIZAÇÃO REMOVIDA
  // (O script "inline" no <head> agora cuida disto)
  
  // 5. Adicionar listeners quando o HTML estiver pronto
  document.addEventListener('DOMContentLoaded', function() {
    
    // A inicialização do ícone ainda é necessária aqui
    const button = document.getElementById('themeToggleButton');
    if (button) {
      // Define o ícone inicial com base no modo que já foi definido no <head>
      button.innerHTML = (window.getModo() === 1) ? '🌙' : '☀️';
    
      // Adiciona o evento de clique
      button.addEventListener('click', function() {
        const newModo = (window.getModo() === 1) ? 0 : 1;
        window.setModo(newModo); // Chama a função global para salvar e aplicar
      });
    }
  });

  // 6. Sincronização entre abas (igual a antes)
  window.addEventListener('storage', function(ev){
    if (ev.key !== KEY) return;
    const newModo = (ev.newValue === '1') ? 1 : 0;
    applyModo(newModo); 
  });

})();