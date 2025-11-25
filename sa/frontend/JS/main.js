// Valores de exemplo (substituir por dados reais do backend quando existirem)
const nome = "Pedro Henrique de Souza";
const sald = 1500.75;

// Define texto apenas se o elemento existir
const nameEl = document.getElementById("name");
if (nameEl) nameEl.textContent = nome;

const saldoEl = document.getElementById("saldo");
if (saldoEl) saldoEl.textContent = `R$: ${sald}`;


//Sistema de nome do arquivo e enviado------------------------------------------
const fileInput = document.getElementById('doc');
const fileNameDisplay = document.getElementById('fileNameDisplay');

if (fileInput && fileNameDisplay) {
  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      fileNameDisplay.textContent = `${fileInput.files[0].name}`;
    } else {
      fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
    }
  });
}
//---------------------------------------------------------------------------------


function toggleSecao() {
  const secao = document.getElementById("minhaSecao");
  if (!secao) return;
  const isHidden = secao.style.display === "none" || getComputedStyle(secao).display === "none";
  secao.style.display = isHidden ? "block" : "none";
}




document.querySelectorAll('.btn-excluir').forEach(button => {
  button.addEventListener('click', function () {
    const item = this.closest('.div9');
    if (!item) return;
    if (!confirm('Deseja excluir este item?')) return;
    item.remove();
  });
});
// Fim do código de exclusão de itens do histórico ------------------------------
//Grafico em Pizza---------------------------------------------------------------
let pizzaChart = null; // gráfico de pizza

function mostrarGraficoPizza() {
  const canvas = document.getElementById('meuGrafico');
  if (!canvas || typeof Chart === 'undefined') return;
  const ctx = canvas.getContext('2d');

  if (pizzaChart) {
    pizzaChart.destroy();
    pizzaChart = null;
  }

  pizzaChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Vermelho', 'Azul', 'Amarelo', 'Verde', 'Roxo'],
      datasets: [{
        data: [12, 19, 3, 5, 2],
        backgroundColor: ['red', 'blue', 'yellow', 'green', 'purple']
      }]
    },
    options: {
      responsive: false
    }
  });
}
// Fim do código do gráfico em pizza------------------------------------------------
//grafico em barras---------------------------------------------------------------
let barraChart = null;
const btnBarra = document.getElementById('btnBarra');

function criarOuDestruirBarra() {
  const canvas = document.getElementById('graficoBarra');
  if (!canvas || typeof Chart === 'undefined') return;
  const ctx = canvas.getContext('2d');

  if (barraChart) {
    barraChart.destroy();
    barraChart = null;
    if (btnBarra) btnBarra.classList.remove('ativo');
  } else {
    barraChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
        datasets: [{
          label: 'Vendas',
          data: [12, 19, 3, 5, 2],
          backgroundColor: [
            'rgba(255, 99, 132, 0.7)',
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 206, 86, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: false,
        scales: {
          y: { beginAtZero: true }
        }
      }
    });
    if (btnBarra) btnBarra.classList.add('ativo');
  }
}

if (btnBarra) btnBarra.addEventListener('click', criarOuDestruirBarra);
// Fim do código do gráfico em barras------------------------------------------------

// references aos canvases
const barraCanvas = document.getElementById('graficoBarra');
const pizzaCanvas = document.getElementById('meuGrafico');


// função genérica para mostrar um canvas por ID
function mostrarCanvas(idAtivo) {
  [barraCanvas, pizzaCanvas].forEach(c => {
    if (!c) return;
    if (c.id === idAtivo) c.classList.add('active');
    else c.classList.remove('active');
  });

  // força o Chart.js a redimensionar corretamente
  if (barraChart && idAtivo === 'graficoBarra') barraChart.resize();
  if (pizzaChart && idAtivo === 'meuGrafico') pizzaChart.resize();

  // destaca o botão correto
  if (idAtivo === 'graficoBarra') {
    if (btnBarra) btnBarra.classList.add('active');
    if (btnPizza) btnPizza.classList.remove('active');
  } else if (idAtivo === 'meuGrafico') {
    if (btnPizza) btnPizza.classList.add('active');
    if (btnBarra) btnBarra.classList.remove('active');
  }
}

// conecta os botões
const btnPizza = document.getElementById('btnPizza');
if (btnPizza) btnPizza.addEventListener('click', () => { mostrarCanvas('meuGrafico'); mostrarGraficoPizza(); });



// inicializa mostrando só o gráfico de barras (escolha um)
mostrarCanvas('graficoBarra');
