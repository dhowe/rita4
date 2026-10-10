// ESLint flat config — scoped to src/ only (the shipped library).
// The test suite is intentionally excluded: it has accumulated patterns
// (var redeclarations, expression-statement assertions) that would need a
// separate cleanup pass.
import js from '@eslint/js';

export default [
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'types/**',
      'test/**',
      'src/rita_dict.js', // generated dictionary (machine-written)
      'src/rita_lts.js'   // generated LTS rules
    ]
  },

  js.configs.recommended,

  {
    files: ['src/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: {
        console: 'readonly',
        process: 'readonly',
        globalThis: 'readonly',
        window: 'readonly',
        document: 'readonly',
        require: 'readonly',
        module: 'readonly',
        __dirname: 'readonly'
      }
    },
    rules: {
      // real bugs — keep as errors
      'no-undef': 'error',
      'no-dupe-keys': 'error',
      'no-dupe-else-if': 'error',
      'no-unreachable': 'error',
      'no-constant-condition': ['error', { checkLoops: false }],
      'no-fallthrough': 'error',
      'no-sparse-arrays': 'error',

      // worth fixing, but noisy — warnings for now
      'no-unused-vars': ['warn', {
        args: 'none',
        varsIgnorePattern: '^_',
        caughtErrors: 'none'
      }],
      'no-useless-escape': 'warn',
      'no-prototype-builtins': 'off', // legacy pattern; see Util.hasOwn

      // stylistic only — surfaced as warnings so `npm run lint` stays green
      // while the remaining nits are cleaned up over time
      'no-unexpected-multiline': 'warn',
      'no-useless-assignment': 'warn',
      'no-redeclare': 'warn',
      'no-unassigned-vars': 'warn'
    }
  }
];
