<template>
  <div class="category-manage">
    <el-card>
      <el-tabs v-model="activeTab" class="manage-tabs">
        <!-- 分类管理 -->
        <el-tab-pane label="分类管理" name="category">
          <div class="header-actions">
            <el-button type="primary" @click="handleCategoryAdd">新增分类</el-button>
          </div>
          <el-table :data="categories" v-loading="loadingCategory" border style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="分类名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="创建时间">
              <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="handleCategoryEdit(row)">编辑</el-button>
                <el-button size="small" type="danger" plain @click="handleCategoryDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 标签管理 -->
        <el-tab-pane label="标签管理" name="tag">
          <div class="header-actions">
            <el-button type="primary" @click="handleTagAdd">新增标签</el-button>
          </div>
          <el-table :data="tags" v-loading="loadingTag" border style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="标签名称" />
            <el-table-column prop="color" label="颜色" width="100">
              <template #default="{ row }">
                <el-color-picker v-model="row.color" disabled size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="创建时间">
              <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="handleTagEdit(row)">编辑</el-button>
                <el-button size="small" type="danger" plain @click="handleTagDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Category Dialog -->
    <el-dialog v-model="categoryDialogVisible" :title="categoryForm.id ? '编辑分类' : '新增分类'" width="500px">
      <el-form :model="categoryForm" :rules="rules" ref="categoryFormRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="categoryForm.description" placeholder="请输入分类描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCategory" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- Tag Dialog -->
    <el-dialog v-model="tagDialogVisible" :title="tagForm.id ? '编辑标签' : '新增标签'" width="500px">
      <el-form :model="tagForm" :rules="rules" ref="tagFormRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="颜色" prop="color">
          <el-color-picker v-model="tagForm.color" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="tagForm.description" placeholder="请输入标签描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTag" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getCategoryList, createCategory, updateCategory, deleteCategory, getTagList, createTag, updateTag, deleteTag } from '@/api/admin';

const activeTab = ref('category');

const categories = ref<any[]>([]);
const loadingCategory = ref(false);

const tags = ref<any[]>([]);
const loadingTag = ref(false);

const categoryDialogVisible = ref(false);
const tagDialogVisible = ref(false);
const submitLoading = ref(false);

const categoryFormRef = ref();
const tagFormRef = ref();

const rules = {
  name: [{ required: true, message: '名称不能为空', trigger: 'blur' }]
};

const categoryForm = reactive({
  id: null as number | null,
  name: '',
  description: ''
});

const tagForm = reactive({
  id: null as number | null,
  name: '',
  color: '#409EFF',
  description: ''
});

const fetchCategories = async () => {
  loadingCategory.value = true;
  try {
    const { data } = await getCategoryList();
    categories.value = data || [];
  } catch (error) {
    console.error(error);
  } finally {
    loadingCategory.value = false;
  }
};

const fetchTags = async () => {
  loadingTag.value = true;
  try {
    const { data } = await getTagList();
    tags.value = data || [];
  } catch (error) {
    console.error(error);
  } finally {
    loadingTag.value = false;
  }
};

const handleCategoryAdd = () => {
  categoryForm.id = null;
  categoryForm.name = '';
  categoryForm.description = '';
  categoryDialogVisible.value = true;
};

const handleCategoryEdit = (row: any) => {
  categoryForm.id = row.id;
  categoryForm.name = row.name;
  categoryForm.description = row.description;
  categoryDialogVisible.value = true;
};

const submitCategory = async () => {
  if (!categoryFormRef.value) return;
  await categoryFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitLoading.value = true;
      try {
        if (categoryForm.id) {
          await updateCategory(categoryForm.id, categoryForm);
          ElMessage.success('分类更新成功');
        } else {
          await createCategory(categoryForm);
          ElMessage.success('分类创建成功');
        }
        categoryDialogVisible.value = false;
        fetchCategories();
      } catch (error) {} finally {
        submitLoading.value = false;
      }
    }
  });
};

const handleCategoryDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${row.name}" 吗？`, '警告', { type: 'error' });
    await deleteCategory(row.id);
    ElMessage.success('删除成功');
    fetchCategories();
  } catch (e) {}
};

const handleTagAdd = () => {
  tagForm.id = null;
  tagForm.name = '';
  tagForm.color = '#409EFF';
  tagForm.description = '';
  tagDialogVisible.value = true;
};

const handleTagEdit = (row: any) => {
  tagForm.id = row.id;
  tagForm.name = row.name;
  tagForm.color = row.color || '#409EFF';
  tagForm.description = row.description;
  tagDialogVisible.value = true;
};

const submitTag = async () => {
  if (!tagFormRef.value) return;
  await tagFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitLoading.value = true;
      try {
        if (tagForm.id) {
          await updateTag(tagForm.id, tagForm);
          ElMessage.success('标签更新成功');
        } else {
          await createTag(tagForm);
          ElMessage.success('标签创建成功');
        }
        tagDialogVisible.value = false;
        fetchTags();
      } catch (error) {} finally {
        submitLoading.value = false;
      }
    }
  });
};

const handleTagDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除标签 "${row.name}" 吗？`, '警告', { type: 'error' });
    await deleteTag(row.id);
    ElMessage.success('删除成功');
    fetchTags();
  } catch (e) {}
};

onMounted(() => {
  fetchCategories();
  fetchTags();
});
</script>

<style scoped>
.manage-tabs {
  margin-top: -10px;
}
.header-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}
</style>
