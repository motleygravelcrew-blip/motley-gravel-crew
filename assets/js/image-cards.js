/* MGC image cards: render only allow-listed Commons files after metadata validation. */
(async function () {
  const mount = document.querySelector("[data-mgc-image-cards]");
  if (!mount) return;
  try {
    const response = await fetch("image-library/approved-images.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Image library unavailable");
    const library = await response.json();
    const cards = library.images || [];
    if (!cards.length) throw new Error("No approved images");
    const grid = document.createElement("div");
    grid.className = "story-grid";
    cards.forEach((item) => {
      if (!item.preview_url || !item.source_page || !item.creator || !item.licence || !item.licence_url) return;
      const card = document.createElement("article");
      card.className = "story-card";
      const img = document.createElement("img");
      img.src = item.preview_url;
      img.alt = item.alt || item.editorial_title || "Cycling photograph";
      img.loading = "lazy";
      img.decoding = "async";
      const body = document.createElement("div");
      body.className = "story-card-body";
      const label = document.createElement("span");
      label.className = "category cyan";
      label.textContent = "MGC IMAGE LIBRARY";
      const title = document.createElement("h3");
      title.textContent = item.editorial_title;
      const caption = document.createElement("p");
      caption.textContent = item.editorial_caption || "";
      const credit = document.createElement("small");
      credit.className = "image-credit";
      credit.append("Photograph: " + item.creator + " · ");
      const source = document.createElement("a");
      source.href = item.source_page;
      source.target = "_blank";
      source.rel = "noopener";
      source.textContent = "Source";
      credit.append(source, " · ");
      const licence = document.createElement("a");
      licence.href = item.licence_url;
      licence.target = "_blank";
      licence.rel = "noopener";
      licence.textContent = item.licence;
      credit.append(licence);
      if (item.credit_note) credit.append(" · " + item.credit_note);
      body.append(label, title, caption);
      card.append(img, body, credit);
      grid.append(card);
    });
    if (!grid.children.length) throw new Error("No fully credited image records");
    mount.replaceChildren(grid);
  } catch (error) {
    mount.textContent = "The cycling image library is being refreshed. Please check back shortly.";
  }
})();
