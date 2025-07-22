import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function fetchWithAdminAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const username = localStorage.getItem('admin_username');
  const apiKey = localStorage.getItem('admin_api_key');

  if (!username || !apiKey) {
    // 인증 정보가 없으면 로그인 페이지로 리디렉션하거나 에러 처리
    window.location.href = '/admin'; 
    throw new Error('인증 정보가 없습니다. 다시 로그인해주세요.');
  }

  const headers = new Headers(options.headers);
  headers.set('X-Admin-Username', username);
  headers.set('X-Admin-Key', apiKey);

  const newOptions: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(url, newOptions);

  if (response.status === 403) {
    // 권한 오류 발생 시 로그인 정보 삭제 및 리디렉트
    localStorage.removeItem('admin_username');
    localStorage.removeItem('admin_api_key');
    window.location.href = '/admin';
    throw new Error('인증이 만료되었거나 유효하지 않습니다. 다시 로그인해주세요.');
  }

  return response;
}
