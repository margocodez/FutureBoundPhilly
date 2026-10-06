const chat = document.getElementById("chat");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const button = form.querySelector("button");
const calculating = document.getElementById("calculating");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  if (role === "atlas") {
    const who = document.createElement("span");
    who.className = "who";
    who.textContent = "Atlas";
    div.appendChild(who);
  }
  const p = document.createElement("p");
  p.textContent = text;
  div.appendChild(p);
  chat.appendChild(div);
  div.scrollIntoView({ behavior: "smooth", block: "end" });
  return div;
}

function setBusy(busy) {
  input.disabled = busy;
  button.disabled = busy;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage("student", text);
  input.value = "";
  setBusy(true);
  const typing = addMessage("atlas", "...");
  typing.classList.add("typing");

  try {
    const response = await fetch(form.dataset.url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await response.json();
    typing.remove();

    if (!response.ok) {
      addMessage("atlas", data.error || "Something went wrong. Please try again.");
    } else {
      data.replies.forEach((reply) => addMessage("atlas", reply));
      if (data.done) {
        form.hidden = true;
        calculating.hidden = false;
        setTimeout(() => { window.location.href = data.redirect; }, 3000);
        return;
      }
    }
  } catch {
    typing.remove();
    addMessage("atlas", "I couldn't reach the server. Check your connection and try again.");
  }
  setBusy(false);
  input.focus();
});

chat.lastElementChild.scrollIntoView({ block: "end" });
