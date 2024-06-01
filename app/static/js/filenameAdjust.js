const targetNames = document.querySelectorAll('.uploaded-filenames');
const firstLength = 20;
const secondLength = 40;

targetNames.forEach((item) => {
  const first = item.textContent.slice(0, firstLength);
  const second = item.textContent.slice(firstLength, secondLength);
  const third = item.textContent.slice(secondLength);
  item.textContent = `${first}\n${second}\n${third}`;
  });