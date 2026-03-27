import request from '@/utils/request';

export const getUserInfo = () => {
  return request.get('/auth/me');
};

export const updateUserInfo = (data: any) => {
  return request.put('/auth/me', data);
};

export const login = (data: any) => {
  const formData = new URLSearchParams();
  formData.append('username', data.username);
  formData.append('password', data.password);
  return request.post('/auth/login', formData);
};

export const register = (data: any) => {
  return request.post('/auth/register', data);
};

export const getFriends = () => {
  return request.get('/friends/');
};
