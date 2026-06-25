const input = document.getElementById("tags-input");
const suggestions = document.getElementById("tag-suggestions");

function isSeparator(char) {
  return char === " " || char === ",";
}

function getTokenRange(value, cursor) {
  let start = cursor;
  while (start > 0 && !isSeparator(value[start - 1])) {
    start -= 1;
  }

  let end = cursor;
  while (end < value.length && !isSeparator(value[end])) {
    end += 1;
  }

  return [start, end];
}

function normalizeSpacing(value, insertedEnd) {
  if (insertedEnd >= value.length) {
    return "";
  }

  const next = value[insertedEnd];
  return isSeparator(next) ? "" : " ";
}

if (input && suggestions) {
  const tags = (input.dataset.tags || "")
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);

  function renderSuggestions() {
    const value = input.value;
    const cursor = input.selectionStart ?? value.length;
    const [start, end] = getTokenRange(value, cursor);
    const currentToken = value.slice(start, cursor).trim().toUpperCase();

    suggestions.innerHTML = "";

    if (!currentToken) {
      return;
    }

    const matches = tags.filter((tag) => tag.startsWith(currentToken)).slice(0, 5);

    for (const tag of matches) {
      const option = document.createElement("button");
      option.type = "button";
      option.className = "tag-suggestion";
      option.textContent = tag;

      option.addEventListener("click", () => {
        const left = value.slice(0, start);
        const right = value.slice(end);
        const separator = normalizeSpacing(value, end);

        input.value = `${left}${tag}${separator}${right}`.replace(/\s+,/g, ",");
        suggestions.innerHTML = "";
        input.focus();
      });

      suggestions.appendChild(option);
    }
  }

  input.addEventListener("input", renderSuggestions);
  input.addEventListener("keyup", renderSuggestions);
  input.addEventListener("click", renderSuggestions);
}
