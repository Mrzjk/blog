import request from '@/utils/request';

export const getArticleList = (params: any) => {
  return request.get('/posts/', { params });
};

export const getArticleDetail = (id: string | number) => {
  return request.get(`/posts/${id}`);
};

export const getUserPosts = (userId: number) => {
  return request.get(`/posts/user/${userId}`);
};

export const getUserBookmarks = (userId: number) => {
  return request.get(`/posts/user/${userId}/bookmarks`);
};

export const getCategories = () => {
  return request.get('/categories/');
};

export const getTags = () => {
  return request.get('/tags/');
};

export const getHotArticles = () => {
  return request.get('/posts/hot', { params: { limit: 10 } });
};

export const publishArticle = (data: any) => {
  return request.post('/posts/', data);
};
