const VIEWPORTS = [
  { name: "mobile", label: "Mobile", width: 390 },
  { name: "tablet", label: "Tablet", width: 834 },
  { name: "desktop", label: "Desktop", width: 1440 },
];

const VIEWPORT_STORAGE_KEY = "leffic-design-viewport";
const SVG_NAMESPACE = "http://www.w3.org/2000/svg";

class IconSprite {
  static inject() {
    const sprite = document.createElementNS(SVG_NAMESPACE, "svg");
    sprite.setAttribute("aria-hidden", "true");
    sprite.style.display = "none";

    const symbols = Object.keys(ICONS).map((name) => {
      const icon = ICONS[name];
      return `<symbol id="icon-${name}" viewBox="${icon.viewBox}">${icon.body}</symbol>`;
    });

    sprite.innerHTML = symbols.join("");
    document.body.prepend(sprite);
  }
}

class ViewportSwitcher {
  static read() {
    const stored = localStorage.getItem(VIEWPORT_STORAGE_KEY);
    const known = VIEWPORTS.some((viewport) => viewport.name === stored);
    return known ? stored : VIEWPORTS[0].name;
  }

  static apply(name) {
    const chosen = VIEWPORTS.find((viewport) => viewport.name === name);
    document.documentElement.style.setProperty(
      "--viewport-width",
      `${chosen.width}px`
    );
    localStorage.setItem(VIEWPORT_STORAGE_KEY, chosen.name);

    const buttons = document.querySelectorAll("[data-viewport]");
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.viewport === chosen.name);
    });
  }
}

class ScreenNavigator {
  static index() {
    const slug = document.body.dataset.screen;
    return SCREENS.findIndex((screen) => screen.slug === slug);
  }

  static neighbour(step) {
    const total = SCREENS.length;
    const target = (ScreenNavigator.index() + step + total) % total;
    return SCREENS[target];
  }

  static go(step) {
    window.location.href = `${ScreenNavigator.neighbour(step).slug}.html`;
  }

  static bindKeyboard() {
    document.addEventListener("keydown", (event) => {
      const typing = event.target.matches("input, textarea");
      if (typing) return;

      if (event.key === "ArrowLeft") ScreenNavigator.go(-1);
      if (event.key === "ArrowRight") ScreenNavigator.go(1);
    });
  }
}

class ShellBar {
  static viewportButtons() {
    return VIEWPORTS.map(
      (viewport) =>
        `<button data-viewport="${viewport.name}">${viewport.label}</button>`
    ).join("");
  }

  static build() {
    const position = ScreenNavigator.index();
    const screen = SCREENS[position];

    const bar = document.createElement("header");
    bar.className = "shell-bar";
    bar.innerHTML = `
      <a href="index.html">Map</a>
      <div class="shell-group">
        <button data-step="-1" title="Previous screen">&lsaquo;</button>
        <button data-step="1" title="Next screen">&rsaquo;</button>
      </div>
      <span class="shell-title">${screen.title}</span>
      <span class="shell-count">${position + 1} / ${SCREENS.length}</span>
      <div class="shell-group">${ShellBar.viewportButtons()}</div>
    `;

    document.body.prepend(bar);

    bar.querySelectorAll("[data-step]").forEach((button) => {
      button.addEventListener("click", () =>
        ScreenNavigator.go(Number(button.dataset.step))
      );
    });

    bar.querySelectorAll("[data-viewport]").forEach((button) => {
      button.addEventListener("click", () =>
        ViewportSwitcher.apply(button.dataset.viewport)
      );
    });
  }
}

class Shell {
  static start() {
    IconSprite.inject();
    ShellBar.build();
    ViewportSwitcher.apply(ViewportSwitcher.read());
    ScreenNavigator.bindKeyboard();
  }
}

Shell.start();
