class ScreenMap {
  static groups() {
    const ordered = [];

    SCREENS.forEach((screen, position) => {
      const last = ordered[ordered.length - 1];
      const entry = { screen: screen, position: position };

      if (last && last.name === screen.group) {
        last.entries.push(entry);
        return;
      }

      ordered.push({ name: screen.group, entries: [entry] });
    });

    return ordered;
  }

  static card(entry) {
    return `
      <a class="map-card" href="${entry.screen.slug}.html">
        <span class="map-card-index">${entry.position + 1}</span>
        <span>${entry.screen.title}</span>
      </a>
    `;
  }

  static section(group) {
    const cards = group.entries.map(ScreenMap.card).join("");
    return `
      <h2 class="map-group">${group.name}</h2>
      <div class="map-grid">${cards}</div>
    `;
  }

  static render() {
    const body = document.getElementById("map-body");
    body.innerHTML = ScreenMap.groups().map(ScreenMap.section).join("");

    document.getElementById("map-count").textContent = `${SCREENS.length} screens`;
  }
}

ScreenMap.render();
