// ====== CONFIG ======
const ENTRY_HASH = "81d980f56d888b032ff917aca9c38fb8b72ecd652690e3ac2ab31e0ee4a5fbd1";
const LOCKOUT_MS = 10000;

const ENTRY_MSGS = [
  "ENTRY REJECTED",
  "TOKEN NOT RECOGNIZED",
  "ACCESS DENIED"
];

const RECORD_MSGS = [
  "KEY INVALID",
  "RECORD NOT AUTHORIZED",
  "VERIFICATION FAILED"
];

// ====== STATE ======
let entryFails = 0;
let recordFails = 0;
let entryLocked = false;
let recordLocked = false;
let recordsData = null;

// ====== UTIL ======
async function sha256Hex(str) {
  const enc = new TextEncoder().encode(str);
  const buf = await crypto.subtle.digest("SHA-256", enc);
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}

function lockout(type, input, button, msgEl) {
  if (type === "entry") entryLocked = true;
  if (type === "record") recordLocked = true;

  input.disabled = true;
  button.disabled = true;
  msgEl.textContent = "ACCESS TEMPORARILY SUSPENDED";

  setTimeout(() => {
    input.disabled = false;
    button.disabled = false;
    msgEl.textContent = "";
    if (type === "entry") { entryFails = 0; entryLocked = false; }
    if (type === "record") { recordFails = 0; recordLocked = false; }
  }, LOCKOUT_MS);
}

// ====== INDEX (ENTRY) ======
document.addEventListener("DOMContentLoaded", async () => {
  const entryInput = document.getElementById("entry");
  const enterBtn = document.getElementById("enter");
  const msg = document.getElementById("msg");

  if (enterBtn && entryInput) {
    enterBtn.onclick = async () => {
      if (entryLocked) return;

      const h = await sha256Hex(entryInput.value.trim());
      if (h === ENTRY_HASH) {
        window.location.href = "records.html";
      } else {
        msg.textContent = ENTRY_MSGS[Math.min(entryFails, ENTRY_MSGS.length - 1)];
        entryFails++;
        if (entryFails >= 3) lockout("entry", entryInput, enterBtn, msg);
      }
    };
  }

  // ====== RECORDS ======
  const listEl = document.getElementById("list");
  const panel = document.getElementById("record-panel");
  const titleEl = document.getElementById("record-title");
  const keyInput = document.getElementById("record-key");
  const unlockBtn = document.getElementById("unlock");
  const recordMsg = document.getElementById("record-msg");
  const recordText = document.getElementById("record-text");

  if (listEl) {
    const res = await fetch("assets/records_short.json");
    recordsData = await res.json();

    recordsData.records.forEach(rec => {
      const b = document.createElement("button");
      b.textContent = rec.id;
      b.onclick = () => {
        panel.classList.remove("hidden");
        titleEl.textContent = rec.id;
        recordText.innerHTML = "";
        recordMsg.textContent = "";
        keyInput.value = "";
        keyInput.focus();

        unlockBtn.onclick = async () => {
          if (recordLocked) return;

          const h = await sha256Hex(keyInput.value.trim());
          if (h === rec.key_hash) {
            recordText.innerHTML = `<p>${rec.lines[0]}</p><p>${rec.lines[1]}</p>`;
            recordFails = 0;
          } else {
            recordMsg.textContent = RECORD_MSGS[Math.min(recordFails, RECORD_MSGS.length - 1)];
            recordFails++;
            if (recordFails >= 3) lockout("record", keyInput, unlockBtn, recordMsg);
          }
        };
      };
      listEl.appendChild(b);
    });
  }
});

