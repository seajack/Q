<template>
  <div class="employee-offboarding">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">离职管理</h1>
        <p class="page-description">管理员工离职流程和相关信息</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleAddOffboarding">
          <i class="el-icon-plus"></i>
          新增离职
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索员工姓名或工号"
            prefix-icon="el-icon-search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="statusFilter" placeholder="离职状态" clearable @change="handleFilter">
            <el-option label="待离职" value="pending" />
            <el-option label="已离职" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="departmentFilter" placeholder="部门" clearable @change="handleFilter">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleFilter"
          />
        </el-col>
        <el-col :span="4">
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 数据表格 -->
    <div class="table-section">
      <el-table
        :data="filteredOffboardingList"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="employeeName" label="姓名" width="120" />
        <el-table-column prop="employeeId" label="工号" width="100" />
        <el-table-column prop="department" label="部门" width="150" />
        <el-table-column prop="position" label="职位" width="150" />
        <el-table-column prop="offboardingDate" label="离职日期" width="120" />
        <el-table-column prop="reason" label="离职原因" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template slot-scope="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template slot-scope="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="success" @click="handleComplete(row)" v-if="row.status === 'pending'">
              完成
            </el-button>
            <el-button size="small" type="danger" @click="handleCancel(row)" v-if="row.status === 'pending'">
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total">
        </el-pagination>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="员工姓名" prop="employeeName">
              <el-input v-model="formData.employeeName" placeholder="请输入员工姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" prop="employeeId">
              <el-input v-model="formData.employeeId" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门" prop="departmentId">
              <el-select v-model="formData.departmentId" placeholder="请选择部门">
                <el-option
                  v-for="dept in departments"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职位" prop="positionId">
              <el-select v-model="formData.positionId" placeholder="请选择职位">
                <el-option
                  v-for="pos in positions"
                  :key="pos.id"
                  :label="pos.name"
                  :value="pos.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="离职日期" prop="offboardingDate">
              <el-date-picker
                v-model="formData.offboardingDate"
                type="date"
                placeholder="选择离职日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="离职原因" prop="reason">
              <el-select v-model="formData.reason" placeholder="请选择离职原因">
                <el-option label="个人原因" value="personal" />
                <el-option label="职业发展" value="career" />
                <el-option label="薪资待遇" value="salary" />
                <el-option label="工作环境" value="environment" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="详细说明" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入离职详细说明"
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'EmployeeOffboarding',
  data() {
    return {
      loading: false,
      searchQuery: '',
      statusFilter: '',
      departmentFilter: '',
      dateRange: [],
      currentPage: 1,
      pageSize: 20,
      total: 0,
      selectedRows: [],
      dialogVisible: false,
      dialogTitle: '',
      isEdit: false,
      formData: {
        id: null,
        employeeName: '',
        employeeId: '',
        departmentId: '',
        positionId: '',
        offboardingDate: '',
        reason: '',
        description: ''
      },
      formRules: {
        employeeName: [
          { required: true, message: '请输入员工姓名', trigger: 'blur' }
        ],
        employeeId: [
          { required: true, message: '请输入工号', trigger: 'blur' }
        ],
        departmentId: [
          { required: true, message: '请选择部门', trigger: 'change' }
        ],
        positionId: [
          { required: true, message: '请选择职位', trigger: 'change' }
        ],
        offboardingDate: [
          { required: true, message: '请选择离职日期', trigger: 'change' }
        ],
        reason: [
          { required: true, message: '请选择离职原因', trigger: 'change' }
        ]
      },
      offboardingList: [
        {
          id: 1,
          employeeName: '王五',
          employeeId: 'E003',
          department: '技术部',
          position: '后端工程师',
          offboardingDate: '2024-02-15',
          reason: 'personal',
          reasonText: '个人原因',
          status: 'pending',
          progress: 40,
          description: '因个人发展需要离职',
          createdAt: '2024-02-01 09:00:00'
        },
        {
          id: 2,
          employeeName: '赵六',
          employeeId: 'E004',
          department: '产品部',
          position: 'UI设计师',
          offboardingDate: '2024-02-20',
          reason: 'career',
          reasonText: '职业发展',
          status: 'completed',
          progress: 100,
          description: '寻求更好的职业发展机会',
          createdAt: '2024-02-05 10:00:00'
        }
      ],
      departments: [
        { id: 1, name: '技术部' },
        { id: 2, name: '产品部' },
        { id: 3, name: '运营部' },
        { id: 4, name: '人事部' }
      ],
      positions: [
        { id: 1, name: '前端工程师' },
        { id: 2, name: '后端工程师' },
        { id: 3, name: '产品经理' },
        { id: 4, name: 'UI设计师' }
      ]
    }
  },
  computed: {
    filteredOffboardingList() {
      let filtered = this.offboardingList

      if (this.searchQuery) {
        filtered = filtered.filter(item =>
          item.employeeName.includes(this.searchQuery) ||
          item.employeeId.includes(this.searchQuery)
        )
      }

      if (this.statusFilter) {
        filtered = filtered.filter(item => item.status === this.statusFilter)
      }

      if (this.departmentFilter) {
        filtered = filtered.filter(item => item.departmentId === this.departmentFilter)
      }

      return filtered
    }
  },
  methods: {
    getStatusType(status) {
      const statusMap = {
        pending: 'warning',
        completed: 'success',
        cancelled: 'danger'
      }
      return statusMap[status] || 'info'
    },
    getStatusText(status) {
      const statusMap = {
        pending: '待离职',
        completed: '已离职',
        cancelled: '已取消'
      }
      return statusMap[status] || '未知'
    },
    handleSearch() {
      // 搜索逻辑
    },
    handleFilter() {
      // 筛选逻辑
    },
    handleReset() {
      this.searchQuery = ''
      this.statusFilter = ''
      this.departmentFilter = ''
      this.dateRange = []
    },
    handleSelectionChange(selection) {
      this.selectedRows = selection
    },
    handleAddOffboarding() {
      this.dialogTitle = '新增离职'
      this.isEdit = false
      this.resetForm()
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑离职信息'
      this.isEdit = true
      Object.assign(this.formData, row)
      this.dialogVisible = true
    },
    handleView(row) {
      this.$message.info(`查看 ${row.employeeName} 的离职信息`)
    },
    handleComplete(row) {
      this.$confirm('确定要完成该员工的离职流程吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        row.status = 'completed'
        row.progress = 100
        this.$message.success('离职流程已完成')
      })
    },
    handleCancel(row) {
      this.$confirm('确定要取消该员工的离职流程吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        row.status = 'cancelled'
        this.$message.success('离职流程已取消')
      })
    },
    handleSizeChange(val) {
      this.pageSize = val
    },
    handleCurrentChange(val) {
      this.currentPage = val
    },
    handleDialogClose() {
      this.resetForm()
    },
    resetForm() {
      Object.assign(this.formData, {
        id: null,
        employeeName: '',
        employeeId: '',
        departmentId: '',
        positionId: '',
        offboardingDate: '',
        reason: '',
        description: ''
      })
      this.$refs.formRef?.resetFields()
    },
    handleSubmit() {
      this.$refs.formRef.validate((valid) => {
        if (valid) {
          if (this.isEdit) {
            // 编辑逻辑
            this.$message.success('离职信息更新成功')
          } else {
            // 新增逻辑
            const reasonTextMap = {
              personal: '个人原因',
              career: '职业发展',
              salary: '薪资待遇',
              environment: '工作环境',
              other: '其他'
            }
            const newItem = {
              id: Date.now(),
              ...this.formData,
              department: this.departments.find(d => d.id === this.formData.departmentId)?.name,
              position: this.positions.find(p => p.id === this.formData.positionId)?.name,
              reasonText: reasonTextMap[this.formData.reason],
              status: 'pending',
              progress: 0,
              createdAt: new Date().toLocaleString()
            }
            this.offboardingList.unshift(newItem)
            this.$message.success('离职信息添加成功')
          }
          this.dialogVisible = false
        }
      })
    }
  },
  mounted() {
    // 初始化数据
  }
}
</script>

<style scoped>
.employee-offboarding {
  padding: 12px;
  background: var(--bg);
  min-height: 100vh;
  font-size: 13px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 12px;
  background: var(--card-bg);
  border-radius: 6px;
  box-shadow: var(--shadow-sm);
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 4px 0;
}

.page-description {
  color: var(--muted);
  margin: 0;
}

.filter-section {
  margin-bottom: 8px;
  padding: 12px;
  background: var(--card-bg);
  border-radius: 6px;
  box-shadow: var(--shadow-sm);
}

.table-section {
  background: var(--card-bg);
  border-radius: 6px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.pagination-section {
  padding: 12px;
  display: flex;
  justify-content: center;
}

/* 表格字体调整 */
:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  font-size: 13px;
  padding: 8px 0;
}

:deep(.el-table td) {
  font-size: 13px;
  padding: 8px 0;
}

/* 表单元素字体调整 */
:deep(.el-input__inner) {
  font-size: 13px;
}

:deep(.el-select .el-input__inner) {
  font-size: 13px;
}

:deep(.el-button) {
  font-size: 13px;
}

:deep(.el-form-item__label) {
  font-size: 13px;
}

/* 暗色主题适配 */
.dark-theme .employee-offboarding {
  background: var(--surface-primary);
}

.dark-theme .page-header,
.dark-theme .filter-section,
.dark-theme .table-section {
  background: var(--surface-secondary);
  border: 1px solid var(--border-default);
}

.dark-theme .page-title {
  color: var(--text-primary);
}

.dark-theme .page-description {
  color: var(--text-secondary);
}
</style>
