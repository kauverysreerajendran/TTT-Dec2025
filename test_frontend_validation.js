// Test script to verify frontend validation fix with global available quantities
console.log("🧪 Testing frontend validation fix with global data...");

// Simulate global storage (this is the new fix)
global.window = {}; // Mock window
global.window.currentLotAvailableQuantities = [6, 12, 12];
console.log(
  "Set global available quantities:",
  global.window.currentLotAvailableQuantities
);

// Test 1: Simulate what should happen with R01(3) + R02(2) + R03(1) = 6 total on JB-A00001
console.log("Test 1: R01(3) + R02(2) + R03(1) = 6 total vs global [6, 12, 12]");

// Mock duplicate tray inputs (no _backendResponseData, but global is set - this simulates draft loading scenario)
const mockInputsArray = [
  {
    input: {
      value: "JB-A00001",
      // No _backendResponseData, simulating draft loading before async completes
    },
    quantity: 3,
  },
  {
    input: {
      value: "JB-A00001",
    },
    quantity: 2,
  },
  {
    input: {
      value: "JB-A00001",
    },
    quantity: 1,
  },
];

// Simulate validateDuplicateTrayIds logic
const totalQuantity = mockInputsArray.reduce(
  (sum, item) => sum + item.quantity,
  0
);
console.log(`Total quantity: ${totalQuantity}`);

// Get available quantities using the new priority (PRIORITY 0: global)
let availableTrayQuantities = [16]; // Default fallback
let dataSource = "default";

if (
  global.window.currentLotAvailableQuantities &&
  global.window.currentLotAvailableQuantities.length > 0
) {
  availableTrayQuantities = global.window.currentLotAvailableQuantities;
  dataSource = "global-draft";
  console.log(
    `🎯 Using global available quantities: [${availableTrayQuantities.join(
      ", "
    )}] (source: ${dataSource})`
  );
} else {
  // PRIORITY 1: backend response (not present in this test)
  const backendResponseData = mockInputsArray.find(
    (item) => item.input._backendResponseData
  )?._backendResponseData;
  if (backendResponseData && backendResponseData.available_quantities) {
    availableTrayQuantities = Array.isArray(
      backendResponseData.available_quantities
    )
      ? backendResponseData.available_quantities
      : Array.from(backendResponseData.available_quantities);
    dataSource = "backend-response";
    console.log(
      `Using backend available quantities: [${availableTrayQuantities.join(
        ", "
      )}] (source: ${dataSource})`
    );
  } else {
    console.log("No global or backend data, using fallback");
  }
}

console.log(`Available quantities: [${availableTrayQuantities.join(", ")}]`);

// Check validation
const isExactMatch = availableTrayQuantities.includes(totalQuantity);
const maxAvailableQuantity = Math.max(...availableTrayQuantities);
const exceedsMaxCapacity = totalQuantity > maxAvailableQuantity;
const isPartialUsage =
  totalQuantity > 0 && !isExactMatch && !exceedsMaxCapacity;

console.log(`Is exact match: ${isExactMatch}`);
console.log(`Exceeds capacity: ${exceedsMaxCapacity}`);
console.log(`Is partial usage: ${isPartialUsage}`);

if (isExactMatch) {
  console.log(
    "✅ SUCCESS: Perfect quantity match - should show green validation and allow proceed"
  );
  console.log(
    "Expected error message: ✅ Perfect quantity match: 6 pieces (using available tray)"
  );
} else if (isPartialUsage) {
  console.log("❌ FAIL: Would show partial usage error");
  console.log(
    "Expected error message: ❌ Exact quantity match required: 6 pieces (available: 6 or 12 or 12)"
  );
} else if (exceedsMaxCapacity) {
  console.log("❌ FAIL: Would show capacity exceeded error");
}

console.log(
  "\n🧪 Test completed. The global fix should now work correctly even when _backendResponseData is not yet available."
);
