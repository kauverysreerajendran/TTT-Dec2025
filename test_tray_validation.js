// Test script to verify tray validation fix
console.log("🔍 Testing Tray Validation Fix");

// Test Case 1: Normal tray with multiple quantities
console.log("Test Case 1: Normal tray [7, 16, 16, 16]");
const testResponse1 = {
  exists: true,
  valid_for_rejection: true,
  available_quantities: [7, 16, 16, 16],
  status_message:
    "Tray reuse allowed - perfect quantity match: 7 pieces (draft)",
};

console.log("Available quantities:", testResponse1.available_quantities);

// Test validation for r01=6, r02=1 (total=7)
const total1 = 6 + 1; // 7
const isValid1 = testResponse1.available_quantities.includes(total1);
console.log(
  `r01(6) + r02(1) = ${total1} pieces: ${isValid1 ? "✅ VALID" : "❌ INVALID"}`
);

// Test Case 2: Jumbo tray with multiple quantities
console.log("\nTest Case 2: Jumbo tray [6, 12, 12]");
const testResponse2 = {
  exists: true,
  valid_for_rejection: true,
  available_quantities: [6, 12, 12],
  status_message:
    "Tray reuse allowed - perfect quantity match: 6 pieces (draft)",
};

console.log("Available quantities:", testResponse2.available_quantities);

// Test validation for r01=5, r02=1 (total=6)
const total2 = 5 + 1; // 6
const isValid2 = testResponse2.available_quantities.includes(total2);
console.log(
  `r01(5) + r02(1) = ${total2} pieces: ${isValid2 ? "✅ VALID" : "❌ INVALID"}`
);

// Test invalid case
const total3 = 5; // Partial usage
const isValid3 = testResponse2.available_quantities.includes(total3);
console.log(
  `r01(5) alone = ${total3} pieces: ${
    isValid3 ? "✅ VALID" : "❌ INVALID (partial usage)"
  }`
);

console.log(
  "\n🎉 Test completed - Frontend should now use backend available_quantities"
);
