import request from '@/utils/request';

// 获取好友列表
export const getFriends = () => {
  return request.get('/chat/friends');
};

// 获取与某个好友的聊天记录
export const getMessages = (friendId: number) => {
  return request.get(`/chat/messages/${friendId}`);
};

// 发送好友请求
export const sendFriendRequest = (userId: number) => {
  return request.post(`/chat/friend-request/${userId}`);
};

// 接受好友请求
export const acceptFriendRequest = (userId: number) => {
  return request.put(`/chat/friend-request/${userId}/accept`);
};

// 拒绝好友请求
export const rejectFriendRequest = (userId: number) => {
  return request.put(`/chat/friend-request/${userId}/reject`);
};

// 解除好友关系
export const removeFriend = (userId: number) => {
  return request.delete(`/chat/friend/${userId}`);
};

// 获取好友状态
export const getFriendStatus = (userId: number) => {
  return request.get(`/chat/friend-status/${userId}`);
};

// 清空聊天记录
export const clearMessages = (friendId: number) => {
  return request.delete(`/chat/messages/${friendId}`);
};

// 获取通知列表
export const getNotifications = () => {
  return request.get('/chat/notifications');
};
