import request from '@/utils/request';

export function getUserList(params: { page: number; size: number; keyword?: string }) {
  return request({
    url: '/auth/users',
    method: 'get',
    params: {
      skip: (params.page - 1) * params.size,
      limit: params.size,
      keyword: params.keyword
    }
  });
}

export function createUser(data: any, roleName: string = 'user') {
  return request({
    url: '/auth/users',
    method: 'post',
    params: { role_name: roleName },
    data
  });
}

export function updateUserStatus(userId: number, status: string, duration?: number) {
  return request({
    url: `/auth/users/${userId}/status`,
    method: 'put',
    params: { status, duration }
  });
}

export function updateUserRole(userId: number, roleName: string) {
  return request({
    url: `/auth/users/${userId}/role`,
    method: 'put',
    params: { role_name: roleName }
  });
}

export function updateUser(userId: number, data: any) {
  return request({
    url: `/auth/users/${userId}`,
    method: 'put',
    data
  });
}

export function deleteUser(userId: number) {
  return request({
    url: `/auth/users/${userId}`,
    method: 'delete'
  });
}

// Article Management
export function getArticleList(params: { page: number; size: number; search?: string }) {
  return request({
    url: '/posts/admin',
    method: 'get',
    params: {
      skip: (params.page - 1) * params.size,
      limit: params.size,
      search: params.search
    }
  });
}

export function updateArticleStatus(id: number, status: string) {
  return request({
    url: `/posts/admin/${id}/status`,
    method: 'put',
    params: { status }
  });
}

export function deleteArticle(id: number) {
  return request({
    url: `/posts/admin/${id}`,
    method: 'delete'
  });
}

// Category Management
export function getCategoryList() {
  return request.get('/categories/');
}

export function createCategory(data: any) {
  return request.post('/categories/', data);
}

export function updateCategory(id: number, data: any) {
  return request.put(`/categories/${id}`, data);
}

export function deleteCategory(id: number) {
  return request.delete(`/categories/${id}`);
}

// Tag Management
export function getTagList() {
  return request.get('/tags/');
}

export function createTag(data: any) {
  return request.post('/tags/', data);
}

export function updateTag(id: number, data: any) {
  return request.put(`/tags/${id}`, data);
}

export function deleteTag(id: number) {
  return request.delete(`/tags/${id}`);
}

// System Management
export function getDashboardStats() {
  return request.get('/admin/stats');
}

export function getSystemSettings() {
  return request.get('/admin/settings');
}

export function updateSystemSettings(settings: any) {
  return request.put('/admin/settings', { settings });
}

export function publishAnnouncement(data: { title: string; content: string }) {
  return request.post('/admin/announcements', data);
}
