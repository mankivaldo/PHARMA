function updatePrice(select) {
  const produitId = select.value;
  const unitPriceInput = select
    .closest("tr")
    .querySelector("input[name$=unit_price]");

  if (produitId) {
    fetch(`/get_produit_price/${produitId}/`)
      .then((response) => response.json())
      .then((data) => {
        unitPriceInput.value = data.price; // Mettez à jour le champ du prix unitaire
      });
  } else {
    unitPriceInput.value = ""; // Réinitialisez si aucun produit n'est sélectionné
  }
}
