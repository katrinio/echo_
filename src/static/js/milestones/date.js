function getLocalDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function fillTimezoneField() {
  const field = document.getElementById("timezone");
  if (!field) {
    return;
  }

  field.value = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
}

function syncDateLimits() {
  const dateInput = document.getElementById("happened_at");
  if (!dateInput) {
    return;
  }

  const today = getLocalDateString();
  dateInput.max = today;
  if (!dateInput.value) {
    dateInput.value = today;
  }
}

fillTimezoneField();
syncDateLimits();
