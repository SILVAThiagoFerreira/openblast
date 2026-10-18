const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const context = { window: {} };
vm.runInNewContext(fs.readFileSync('public/charge.js', 'utf8'), context, { filename: 'public/charge.js' });
const distributeCharges = context.window.OpenBlastCharge.distributeCharges;

function total(values) {
  return values.reduce((sum, value) => sum + value, 0);
}

const raised = distributeCharges([5, 10, 15, 60], 100);
assert.equal(total(raised), 100);
assert.equal(raised[0], 5);
assert.equal(raised[3], 60);
assert.deepEqual(raised, distributeCharges([5, 10, 15, 60], 100));
assert.ok(raised.slice(1, 3).every(value => value >= 5 && value <= 60));

const reduced = distributeCharges([5, 20, 40, 60], 100);
assert.equal(total(reduced), 100);
assert.equal(reduced[0], 5);
assert.equal(reduced[3], 60);
assert.ok(reduced.slice(1, 3).every(value => value >= 5 && value <= 60));

const unchanged = distributeCharges([5, 10, 15, 60], 90);
assert.deepEqual(unchanged, [5, 10, 15, 60]);

assert.throws(() => distributeCharges([5, 10, 60], 200), /alvo é impossível/);
assert.throws(() => distributeCharges([5, 10, 60], 50), /alvo é impossível/);
assert.throws(() => distributeCharges([5, 60], 70), /pelo menos três furos/);
assert.throws(() => distributeCharges([5, NaN, 60], 70), /não é válida/);
assert.throws(() => distributeCharges([5, 10, 60], 0), /maior que zero/);

console.log('charge tests passed');
