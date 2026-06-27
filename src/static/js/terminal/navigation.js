


let selectedIndex = -1;

function getRows() {
  // Навигация работает по любым кликабельным строкам с общим атрибутом.
  return [...document.querySelectorAll("[data-keyboard-row]")];
}

function isEditableElement(target) {
  return (
    target instanceof HTMLInputElement ||
    target instanceof HTMLTextAreaElement ||
    target instanceof HTMLSelectElement ||
    target?.isContentEditable
  );
}

function isTerminalInput(target) {
  return target instanceof HTMLInputElement && target.id === "terminal-command";
}

function renderSelection(rows) {
  rows.forEach((row, index) => {
    row.classList.toggle("is-selected", index === selectedIndex);
  });

  const selectedRow = rows[selectedIndex];
  if (selectedRow) {
    selectedRow.scrollIntoView({
      block: "center",
      inline: "nearest",
    });
  }
}

function moveSelection(direction) {
  const rows = getRows();

  if (!rows.length) {
    return;
  }

  if (selectedIndex === -1) {
    // Первая стрелка выбирает край списка в зависимости от направления.
    selectedIndex = direction === "down" ? 0 : rows.length - 1;
  } else if (direction === "down") {
    selectedIndex = Math.min(selectedIndex + 1, rows.length - 1);
  } else {
    selectedIndex = Math.max(selectedIndex - 1, 0);
  }

  renderSelection(rows);
}

function clearSelection() {
  if (selectedIndex === -1) {
    return;
  }

  const rows = getRows();
  selectedIndex = -1;
  renderSelection(rows);
}

function openSelectedRow() {
  const rows = getRows();
  const row = rows[selectedIndex];

  if (!row) {
    return;
  }

  window.location.href = row.href;
}

document.addEventListener("keydown", (event) => {
  // Глобальная навигация не должна мешать редактированию текста.
  if (event.key === "ArrowDown") {
    event.preventDefault();
    moveSelection("down");
  }

  if (event.key === "ArrowUp") {
    event.preventDefault();
    moveSelection("up");
  }

  if (event.key === "Enter") {
    if (isEditableElement(event.target) || isTerminalInput(event.target)) {
      return;
    }

    openSelectedRow();
  }

  if (event.key === "Escape") {
    clearSelection();
  }
});
