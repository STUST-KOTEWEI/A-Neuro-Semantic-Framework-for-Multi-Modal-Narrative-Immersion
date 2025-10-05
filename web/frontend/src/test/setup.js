import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// 擴充 expect 的功能，加入 jest-dom 的斷言方法
expect.extend(matchers);

// 在每個測試案例結束後，自動清理 DOM
afterEach(() => {
  cleanup();
});
