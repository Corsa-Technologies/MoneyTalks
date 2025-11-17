document.addEventListener('DOMContentLoaded', function() {
  const calcButton = document.getElementById('calc_button');
  
  if (calcButton) {
    calcButton.addEventListener('click', calculateInvestment);
  }
});

function calculateInvestment() {
  // --- 1. OBTER VALORES DE ENTRADA ---
  const initialInvestment = parseFloat(document.getElementById('initial_investment').value) || 0;
  const monthlyInvestment = parseFloat(document.getElementById('monthly_investment').value) || 0;
  const term = parseFloat(document.getElementById('term').value) || 0;
  const termUnit = document.getElementById('term_unit').value;
  const profitability = parseFloat(document.getElementById('profitability').value) || 0;
  const profitabilityUnit = document.getElementById('profitability_unit').value;
  const investmentType = document.querySelector('input[name="investment_type"]:checked').value;
  const rateType = document.querySelector('input[name="rate_type"]:checked').value;
  
  const CDI_RATE_ANNUAL = 14.90 / 100;
  const IPCA_RATE_ANNUAL = 4.68 / 100; 

  if (term === 0) {
    alert('Por favor, insira um prazo válido');
    return; 
  }

  // --- 2. CÁLCULO DO PRAZO E IR ---
  const months = termUnit === 'years' ? Math.round(term * 12) : Math.round(term);
  
  // ############ AQUI ESTÁ A CORREÇÃO ############
  // Mudamos de (months * (365.25 / 12)) para (months * 30)
  // para usar o "mês comercial" de 30 dias, igual ao site de referência.
  const totalDays = months * 30;
  // ###############################################
  
  let irRate = 0; 
  if (investmentType !== 'lca') {
    // Agora, 12 meses (360 dias) vai cair na faixa <= 360
    if (totalDays <= 180) {
      irRate = 22.5;
    } else if (totalDays <= 360) {
      irRate = 20.0; // VAI CAIR AQUI AGORA!
    } else if (totalDays <= 720) {
      irRate = 17.5;
    } else {
      irRate = 15.0;
    }
  }
  // ------------------------------------

  // --- 3. CÁLCULO DA RENTABILIDADE (TAXA ANUAL) ---
  // (Nenhuma mudança aqui)
  
  let effectiveAnnualRate;

  switch (rateType) {
    case 'pre':
      effectiveAnnualRate = profitabilityUnit === 'year'
        ? profitability / 100
        : (profitability * 12) / 100;
      break;
    
    case 'pos':
      effectiveAnnualRate = (profitability / 100) * CDI_RATE_ANNUAL;
      break;

    case 'ipca':
      let addedRate = profitabilityUnit === 'year'
        ? profitability / 100
        : (profitability * 12) / 100;
      effectiveAnnualRate = addedRate + IPCA_RATE_ANNUAL;
      break;
      
    default:
      effectiveAnnualRate = profitabilityUnit === 'year'
        ? profitability / 100
        : (profitability * 12) / 100;
  }
  // ------------------------------------

  // --- 4. CÁLCULO DE JUROS COMPOSTOS ---
  // (Nenhuma mudança daqui para baixo)

  const monthlyRate = Math.pow(1 + effectiveAnnualRate, 1 / 12) - 1;
  const compound = Math.pow(1 + monthlyRate, months);
  const fvInitial = initialInvestment * compound;

  let fvMonthly_Postecipada = 0;
  if (monthlyInvestment > 0 && monthlyRate > 0) {
    fvMonthly_Postecipada =
      monthlyInvestment * ((compound - 1) / monthlyRate);
  } else if (monthlyInvestment > 0) {
    fvMonthly_Postecipada = monthlyInvestment * months;
  }

  const totalGross = fvInitial + fvMonthly_Postecipada;
  const totalInvested = initialInvestment + monthlyInvestment * months;
  const earningsBeforeIR = totalGross - totalInvested;
  const irAmount = earningsBeforeIR * (irRate / 100);
  const totalNet = totalGross - irAmount;

  displayResults(totalInvested, earningsBeforeIR, irAmount, totalNet, irRate);
}

// --- 5. FUNÇÕES DE EXIBIÇÃO ---
// (Nenhuma mudança aqui)

function displayResults(invested, earnings, ir, totalLiquido, irRateValue) {
  document.getElementById('result_invested').textContent = formatCurrency(invested);
  document.getElementById('result_earnings').textContent = formatCurrency(earnings);
  document.getElementById('result_ir').textContent = formatCurrency(ir);
  document.getElementById('result_total').textContent = formatCurrency(totalLiquido);
  document.getElementById('result_ir_rate').textContent = formatPercent(irRateValue);
  document.getElementById('result').classList.remove('hidden');
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
}

function formatPercent(value) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'decimal', 
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value) + '%';
}