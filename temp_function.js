// ✅ SIMPLIFIED: collectCurrentSessionAllocations function for frontend compatibility
function collectCurrentSessionAllocations(excludeInput) {
  const allocations = [];

  console.log(
    "📊 [collectCurrentSessionAllocations] Starting allocation collection..."
  );

  document.querySelectorAll(".rejection-qty-input").forEach((qtyInput) => {
    const qty = parseInt(qtyInput.value) || 0;
    const reasonId = qtyInput.getAttribute("data-reason-id");

    if (qty > 0) {
      const row = qtyInput.closest("tr");
      const reasonCell = row.cells[2];
      const reasonText = reasonCell ? reasonCell.textContent.trim() : "";

      console.log(
        `📋 [collectCurrentSessionAllocations] Processing reason ${reasonId} (${reasonText}): qty=${qty}`
      );

      // For the new simplified logic, we just need the basic rejection quantities
      allocations.push({
        reason_id: reasonId,
        reason_text: reasonText,
        qty: qty,
        rejection_qty: qty, // Add both for compatibility
      });
    }
  });

  console.log(
    "📊 [collectCurrentSessionAllocations] FINAL allocations:",
    allocations
  );
  return allocations;
}
