window.addEventListener("load", () => {
  document.querySelectorAll(".save-button").forEach((button) => {
    button.addEventListener("click", async () => {
      const playerId = parseInt(button.getAttribute("data-player-id"));
      const usernameInputId = `#player-${playerId}-username-input`;
      const commentInputId = `#player-${playerId}-comment-input`;
      const usernameInput = document.querySelector(usernameInputId);
      const commentInput = document.querySelector(commentInputId);
      const username = usernameInput.value;
      const comment = commentInput.value;

      const payload = {
        player_id: playerId,
        username: username,
        comment: comment,
      };
      const csrftoken = Cookies.get("csrftoken");
      await fetch(UPDATE_URL, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify(payload),
      });
    });
  });
});
