<template>
  <div class="user-manage">
    <el-card>
      <template #header>
        <div class="header-actions">
          <el-form :inline="true" :model="searchForm">
            <el-form-item label="用户名">
              <el-input v-model="searchForm.keyword" placeholder="搜索用户名/邮箱" clearable @keyup.enter="fetchUsers" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchUsers">搜索</el-button>
              <el-button type="success" @click="openAddDialog">新增用户</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <el-table :data="users" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role?.name === 'admin' ? 'danger' : 'info'">{{ row.role?.name === 'admin' ? '管理员' : '普通用户' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="150">
          <template #default="{ row }">
            <el-tag v-if="!row.is_active" type="danger">已封禁</el-tag>
            <el-tag v-else-if="row.is_muted" type="warning">已禁言</el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="80" />
        <el-table-column prop="exp" label="经验" width="80" />
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="handleEditUser(row)">编辑</el-button>
            
            <template v-if="row.is_active && !row.is_muted">
              <el-button size="small" type="warning" @click="openStatusDialog(row, 'muted')">禁言</el-button>
            </template>
            <template v-else-if="row.is_muted && row.is_active">
              <el-button size="small" type="success" @click="handleUnban(row)">解封禁言</el-button>
            </template>

            <template v-if="row.is_active">
              <el-button size="small" type="danger" @click="openStatusDialog(row, 'banned')">封号</el-button>
            </template>
            <template v-else>
              <el-button size="small" type="success" @click="handleUnban(row)">解封账号</el-button>
            </template>
            
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchUsers"
          @size-change="fetchUsers"
        />
      </div>
    </el-card>

    <!-- Edit User Dialog -->
    <el-dialog v-model="editDialogVisible" title="编辑用户" width="500px">
      <el-form :model="editForm" ref="editFormRef" :rules="editRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="经验值" prop="exp">
          <el-input-number v-model="editForm.exp" :min="0" placeholder="用户经验值" style="width: 100%" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editForm.password" type="password" placeholder="不修改请留空" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEditUser" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Add User Dialog -->
    <el-dialog v-model="addDialogVisible" title="新增用户" width="500px">
      <el-form :model="addForm" ref="addFormRef" :rules="addRules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="addForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="addForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="addForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAddUser" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Status Change Dialog -->
    <el-dialog v-model="statusDialogVisible" :title="statusType === 'banned' ? '封号设置' : '禁言设置'" width="400px">
      <el-form>
        <el-form-item label="时长 (天)">
          <el-input-number v-model="statusDuration" :min="0" :step="1" placeholder="0代表永久" style="width: 100%" />
          <div style="font-size: 12px; color: #999; margin-top: 5px;">* 设置为 0 代表永久生效</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="statusDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitStatusChange" :loading="submitLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { getUserList, updateUserStatus, updateUserRole, deleteUser, createUser, updateUser } from '@/api/admin';
import { ElMessage, ElMessageBox } from 'element-plus';

const users = ref<any[]>([]);
const loading = ref(false);
const page = ref(1);
const size = ref(10);
const total = ref(0);

const searchForm = reactive({
  keyword: ''
});

const currentUser = ref<any>(null);
const submitLoading = ref(false);

// Edit User Dialog
const editDialogVisible = ref(false);
const editFormRef = ref();
const editForm = reactive({
  username: '',
  email: '',
  exp: 0,
  password: '',
  role: 'user'
});
const editRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 3, max: 30, message: '长度在 3 到 30 个字符', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
  password: [{ min: 6, max: 64, message: '长度在 6 到 64 个字符', trigger: 'blur' }]
};

// Add User Dialog
const addDialogVisible = ref(false);
const addFormRef = ref();
const addForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'user'
});
const addRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 3, max: 30, message: '长度在 3 到 30 个字符', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, max: 64, message: '长度在 6 到 64 个字符', trigger: 'blur' }]
};

// Status Dialog
const statusDialogVisible = ref(false);
const statusType = ref('banned');
const statusDuration = ref(0);

const fetchUsers = async () => {
  loading.value = true;
  try {
    const { data } = await getUserList({
      page: page.value,
      size: size.value,
      keyword: searchForm.keyword
    });
    users.value = data.items || [];
    total.value = data.total || 0;
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const openAddDialog = () => {
  addForm.username = '';
  addForm.email = '';
  addForm.password = '';
  addForm.role = 'user';
  addDialogVisible.value = true;
};

const submitAddUser = async () => {
  if (!addFormRef.value) return;
  await addFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitLoading.value = true;
      try {
        await createUser({
          username: addForm.username,
          email: addForm.email,
          password: addForm.password
        }, addForm.role);
        ElMessage.success('用户创建成功');
        addDialogVisible.value = false;
        fetchUsers();
      } catch (error: any) {
        // error handled in interceptor
      } finally {
        submitLoading.value = false;
      }
    }
  });
};

const handleEditUser = (row: any) => {
  currentUser.value = row;
  editForm.username = row.username;
  editForm.email = row.email;
  editForm.exp = row.exp || 0;
  editForm.password = '';
  editForm.role = row.role?.name === 'admin' ? 'admin' : 'user';
  editDialogVisible.value = true;
};

const submitEditUser = async () => {
  if (!editFormRef.value || !currentUser.value) return;
  await editFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitLoading.value = true;
      try {
        const updateData: any = {
          username: editForm.username,
          email: editForm.email,
          exp: editForm.exp
        };
        if (editForm.password) {
          updateData.password = editForm.password;
        }
        await updateUser(currentUser.value.id, updateData);
        if (currentUser.value.role?.name !== editForm.role) {
          await updateUserRole(currentUser.value.id, editForm.role);
        }
        ElMessage.success('用户更新成功');
        editDialogVisible.value = false;
        fetchUsers();
      } catch (error) {
        // Error handled by interceptor
      } finally {
        submitLoading.value = false;
      }
    }
  });
};

const openStatusDialog = (row: any, type: string) => {
  currentUser.value = row;
  statusType.value = type;
  statusDuration.value = 0;
  statusDialogVisible.value = true;
};

const submitStatusChange = async () => {
  if (!currentUser.value) return;
  submitLoading.value = true;
  try {
    await updateUserStatus(currentUser.value.id, statusType.value, statusDuration.value);
    ElMessage.success(statusType.value === 'banned' ? '封号成功' : '禁言成功');
    statusDialogVisible.value = false;
    fetchUsers();
  } catch (error) {
    // cancel
  } finally {
    submitLoading.value = false;
  }
};

const handleUnban = async (row: any) => {
  try {
    await updateUserStatus(row.id, 'normal');
    ElMessage.success('已恢复正常状态');
    fetchUsers();
  } catch (error) {
    // cancel
  }
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${row.username} 吗？此操作不可恢复`, '警告', { type: 'error' });
    await deleteUser(row.id);
    ElMessage.success('已删除');
    fetchUsers();
  } catch (error) {
    // cancel
  }
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
