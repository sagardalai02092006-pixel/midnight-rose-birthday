document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.theme-option input').forEach((input) => {
    input.addEventListener('change', () => {
      document.querySelectorAll('.theme-option').forEach((label) => label.classList.remove('selected'));
      input.closest('.theme-option')?.classList.add('selected');
    });
  });
  const copyButton = document.getElementById('copy-link');
  if (copyButton) {
    copyButton.addEventListener('click', async () => {
      const url = copyButton.dataset.copy;
      const status = document.getElementById('copy-status');
      try {
        await navigator.clipboard.writeText(url);
        copyButton.innerHTML = 'Copied! ✓';
        if (status) status.textContent = 'Link copied. Send it to your favorite person.';
      } catch (_) {
        if (status) status.textContent = 'Copy this link manually: ' + url;
      }
    });
  }
  const reveal = document.getElementById('reveal-button');
  const letter = document.getElementById('letter');
  if (reveal && letter) reveal.addEventListener('click', () => {
    letter.scrollIntoView({ behavior: 'smooth', block: 'start' });
    burstConfetti();
    reveal.textContent = 'A little love, just for you ♡';
  });
  const finalButton = document.getElementById('final-reveal');
  const finalMessage = document.getElementById('final-message');
  if (finalButton && finalMessage) finalButton.addEventListener('click', () => {
    finalMessage.hidden = false;
    finalButton.hidden = true;
    burstConfetti();
  });
  function burstConfetti() {
    if (typeof window.confetti !== 'function') return;
    window.confetti({ particleCount: 90, spread: 70, origin: { y: 0.68 }, colors: ['#e8a0b5', '#f6d9a8', '#fff0f4', '#b67a91'] });
  }
});
