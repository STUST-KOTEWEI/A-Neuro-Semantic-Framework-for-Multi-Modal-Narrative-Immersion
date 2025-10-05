import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from '../App';

describe('App', () => {
  it('應該要能渲染標題', () => {
    render(<App />);
    
    // 使用 screen.getByText 來尋找元素
    // 使用正規表示式 /project-holo/i 來忽略大小寫
    const headingElement = screen.getByText(/project-holo/i);
    
    // 斷言元素存在於文件中
    expect(headingElement).toBeInTheDocument();
  });

  it('應該要顯示文字輸入區', () => {
    render(<App />);
    const textareaElement = screen.getByPlaceholderText('在這裡輸入您的故事或情境...');
    expect(textareaElement).toBeInTheDocument();
  });
});
