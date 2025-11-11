document.addEventListener('DOMContentLoaded', function () {
  const cepInput = document.getElementById('cep');
  const logradouroInput = document.getElementById('logradouro');
  const bairroInput = document.getElementById('bairro');
  const cidadeInput = document.getElementById('cidade');
  const estadoInput = document.getElementById('estado');
  const complementoInput = document.getElementById('complemento');

  if (!cepInput) return;

  function normalizeCEP(value) {
    return (value || '').replace(/\D/g, '').slice(0, 8);
  }

  function formatCEP(value) {
    const digits = normalizeCEP(value);
    if (digits.length <= 5) return digits;
    return `${digits.slice(0, 5)}-${digits.slice(5)}`;
  }

  // Máscara de CEP no input
  cepInput.addEventListener('input', function () {
    const start = cepInput.selectionStart;
    const prev = cepInput.value;
    const formatted = formatCEP(prev);
    cepInput.value = formatted;
    // tentativa simples de manter o caret próximo ao final
    if (document.activeElement === cepInput) {
      const pos = Math.min(formatted.length, start + (formatted.length - prev.length));
      cepInput.setSelectionRange(pos, pos);
    }
  });

  async function buscarEnderecoPorCEP(cepDigits) {
    try {
      const resp = await fetch(`https://viacep.com.br/ws/${cepDigits}/json/`);
      if (!resp.ok) return null;
      const data = await resp.json();
      if (data && !data.erro) return data;
      return null;
    } catch (e) {
      return null;
    }
  }

  cepInput.addEventListener('blur', async function () {
    const digits = normalizeCEP(cepInput.value);
    if (digits.length !== 8) return;

    const endereco = await buscarEnderecoPorCEP(digits);
    if (!endereco) return;

    if (logradouroInput) logradouroInput.value = endereco.logradouro || '';
    if (bairroInput) bairroInput.value = endereco.bairro || '';
    if (cidadeInput) cidadeInput.value = endereco.localidade || '';
    if (estadoInput) estadoInput.value = endereco.uf || '';
    if (complementoInput && endereco.complemento) complementoInput.value = endereco.complemento;
  });
});