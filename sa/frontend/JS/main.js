let nome = "Pedro Henrique de Souza"; //Atualizar puxando o nome do banco de dados
document.getElementById("name").innerHTML = nome;

let sald = 1500.75; //Atualizar puxando o saldo do banco de dados
document.getElementById("saldo").textContent = `R$: ${sald}`;


//Sistema de nome do arquivo e enviado------------------------------------------
const fileInput = document.getElementById('doc');
  const fileNameDisplay = document.getElementById('fileNameDisplay');

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      fileNameDisplay.textContent = `${fileInput.files[0].name}`;} 
      else {
      fileNameDisplay.textContent = 'Nenhum arquivo selecionado';}
      });
//---------------------------------------------------------------------------------


function toggleSecao() {
  const secao = document.getElementById("minhaSecao");
  if (secao.style.display === "none") {
    secao.style.display = "block";
  } else {
    secao.style.display = "none";
  }
}




    document.querySelectorAll('.btn-excluir').forEach(button => {
  button.addEventListener('click', function () {
    const item = this.closest('.div9');
    if (!item) return;
    // confirmação simples
    if (!confirm('Deseja excluir este item?')) return;
    // remove do DOM
    item.remove();
  });
});
// Fim do código de exclusão de itens do histórico ------------------------------
//Grafico em Pizza---------------------------------------------------------------
    let grafico; // variável global para armazenar o gráfico

    function mostrarGrafico() {
      const ctx = document.getElementById('meuGrafico').getContext('2d');

      // Se já existir um gráfico, destrói antes de criar outro
      if (grafico) {
        grafico.destroy();
      }

      grafico = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: ['Vermelho', 'Azul', 'Amarelo', 'Verde', 'Roxo'],
          datasets: [{
            data: [12, 19, 3, 5, 2],// da pra usar variaveis aqui
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
let graficoBarra;
const btnBarra = document.getElementById('btnBarra');

btnBarra.addEventListener('click', () => {
  const ctx = document.getElementById('graficoBarra').getContext('2d');

  if (graficoBarra) {
    // Se já existe, destrói e desativa o botão
    graficoBarra.destroy();
    graficoBarra = null;
    btnBarra.classList.remove('ativo');
  } else {
    // Cria o gráfico em barra
    graficoBarra = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
        datasets: [{
          label: 'Vendas',
          data: [12, 19, 3, 5, 2], // aqui você pode usar variáveis
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
          y: {
            beginAtZero: true
          }
        }
      }
    });
    btnBarra.classList.add('ativo');
  }
});
// Fim do código do gráfico em barras------------------------------------------------

// references aos canvases
const barraCanvas = document.getElementById('graficoBarra');
const pizzaCanvas = document.getElementById('meuGrafico');


// função genérica para mostrar um canvas por ID
function mostrarCanvas(idAtivo) {
  [barraCanvas, pizzaCanvas].forEach(c => {
    if (c.id === idAtivo) c.classList.add('active');
    else c.classList.remove('active');
  });

  // força o Chart.js a redimensionar e redesenhar corretamente
  if (typeof barraChart !== 'undefined' && idAtivo === 'graficoBarra') barraChart.resize();
  if (typeof pizzaChart !== 'undefined' && idAtivo === 'meuGrafico') pizzaChart.resize();

    // destaca o botão correto e remove destaque dos outros
  if (idAtivo === 'graficoBarra') {
    btnBarra.classList.add('active');
    btnPizza.classList.remove('active');
  } else if (idAtivo === 'meuGrafico') {
    btnPizza.classList.add('active');
    btnBarra.classList.remove('active');
  }


}

// conecta os botões
document.getElementById('btnBarra').addEventListener('click', () => mostrarCanvas('graficoBarra'));

const btnPizza = document.getElementById('btnPizza'); // certifique-se de ter id="btnPizza" no HTML
if (btnPizza) btnPizza.addEventListener('click', () => mostrarCanvas('meuGrafico'));



// inicializa mostrando só o gráfico de barras (escolha um)
mostrarCanvas('graficoBarra');
