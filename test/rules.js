const assert = require('assert');
const eslint = require('eslint');
const fs = require('fs');
const path = require('path');

describe('Base config no deprecations', () => {
  it('should return empty messages', (done) => {
    // eslint-disable-next-line handle-callback-err
    fs.readFile(path.join(__dirname, '../.eslintrc'), (err, data) => {
      const config = JSON.parse(data);
      const messages = eslint.linter.verify('', config, { filename: 'foo.js' });

      assert.deepEqual(messages, []);
      done();
    });
  });

  it('react, should return empty messages', (done) => {
    // eslint-disable-next-line handle-callback-err
    fs.readFile(path.join(__dirname, '../.react-eslintrc'), (err, data) => {
      const config = JSON.parse(data);
      const messages = eslint.linter.verify('', config, { filename: 'foo.js' });

      assert.deepEqual(messages, []);
      done();
    });
  });
});
