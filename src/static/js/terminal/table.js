// Измеряет ширину символа в текущем моноширинном шрифте.
function getMonospaceCharWidth(element) {
  const style = window.getComputedStyle(element);
  const canvas = getMonospaceCharWidth.canvas || document.createElement("canvas");
  getMonospaceCharWidth.canvas = canvas;

  const context = canvas.getContext("2d");
  if (!context) {
    return 8;
  }

  context.font = style.font;
  const sample = context.measureText("M");
  return sample.width || 8;
}

// Измеряет ширину точки в текущем шрифте.
function getDotWidth(element) {
  const style = window.getComputedStyle(element);
  const canvas = getDotWidth.canvas || document.createElement("canvas");
  getDotWidth.canvas = canvas;

  const context = canvas.getContext("2d");
  if (!context) {
    return 8;
  }

  context.font = style.font;
  const sample = context.measureText(".");
  return sample.width || 8;
}

// Собирает все строки одной терминальной таблицы.
function getTableRows(table) {
  return Array.from(table.querySelectorAll("[data-terminal-table-row]"));
}

// Берёт label-элемент строки.
function getLabel(row) {
  return row.querySelector("[data-terminal-label]");
}

// Берёт блок с точками.
function getDots(row) {
  return row.querySelector("[data-terminal-dots]");
}

// Берёт значение строки.
function getValue(row) {
  return row.querySelector("[data-terminal-value]");
}

// Заполняет точки по реальному месту между label и value.
function formatTable(table) {
  const rows = getTableRows(table);
  if (!rows.length) {
    return;
  }

  const reference = rows[0];
  const dotWidth = getDotWidth(reference);
  const gapAllowance = getMonospaceCharWidth(reference);

  rows.forEach((row) => {
    const label = getLabel(row);
    const dots = getDots(row);
    const value = getValue(row);

    if (!label || !dots || !value) {
      return;
    }

    const labelRect = label.getBoundingClientRect();
    const valueRect = value.getBoundingClientRect();
    const gapPx = Math.max(0, valueRect.left - labelRect.right - gapAllowance);
    const rowDots = Math.max(0, Math.floor(gapPx / dotWidth));

    dots.textContent = ".".repeat(rowDots);
  });
}

// Инициализирует пересчёт для всех таблиц на странице.
function initTerminalTables() {
  const tables = document.querySelectorAll("[data-terminal-table]");
  tables.forEach((table) => {
    const reformat = () => formatTable(table);
    requestAnimationFrame(reformat);

    const resizeObserver = new ResizeObserver(reformat);
    resizeObserver.observe(table);

    window.addEventListener("resize", reformat, { passive: true });
  });
}

document.addEventListener("DOMContentLoaded", initTerminalTables);
