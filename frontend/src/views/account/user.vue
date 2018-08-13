<style src="../../static/base.css"></style>

<template>
  <div>
    <Card>
      <Row>  
        <Col span="4">
          <Input icon="search" v-model="getParams.search" placeholder="搜索" @on-click="handleGetUserList" @on-enter="handleGetUserList" />
        </Col>

        <Col span="10">
          <center>
            <Button type="primary" @click='createModal = true'>创建用户</Button>
          </center>
        </Col>
      </Row>
      </br>
      <Row>
        <Col span="22">
          <Table :columns="columnsUser" :data="userList"></Table>
        </Col>
      </Row>
      </br>
      <Page :total=total show-sizer :current=getParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>

    </Card>

    <Modal
      v-model="createModal"
      width="800"
      title="创建用户"
      @on-ok="handleCreateUser"
      @on-cancel="cancel">
      <Form ref="createUserForm" :model="createUserForm" :rules="ruleCreateUserForm" :label-width="100">
        <Row>
          <Col span="12">
            <FormItem label="用户名：" prop="username">
              <Input v-model="createUserForm.username"></Input>
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="密码：" prop="password">
              <Input type="password" v-model="createUserForm.password"></Input>
            </FormItem>
          </Col>
        </Row>
        <Row>
          <Col span="12">
            <FormItem label="角色：">
                <Select v-model="createUserForm.role">
                    <Option v-for="item in roleList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                </Select>
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="属组：">
                <Select v-model="createUserForm.groups[0]">
                    <Option v-for="item in groupList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                </Select>
            </FormItem>
          </Col>
        </Row>
        <FormItem label="权限：">          
          <Transfer
            filterable
            :data="permissionList"
            :target-keys="targetKeysCreate"
            :filter-method="filterMethod"
            @on-change="handleChangeCreate"
            :list-style="listStyle"
            :titles="transferTitles">
          </Transfer>
        </FormItem>
        <FormItem label="系统身份：" prop="systemAccount">
          <CheckboxGroup v-model="createUserForm.sysaccount">
              <Checkbox label="is_active">已激活</Checkbox>
              <Checkbox label="is_staff">登录后台</Checkbox>
              <Checkbox label="is_superuser">管理员</Checkbox>
          </CheckboxGroup>
        </FormItem>        
      </Form>  
    </Modal>      

    <Modal
      v-model="updateModal"
      width="800"
      title="修改用户"
      @on-ok="handleUpdateUser"
      @on-cancel="cancel">
      <Form ref="updateUserForm" :model="updateUserForm" :rules="ruleUpdateUserForm" :label-width="100">
        <Row>
          <Col span="12">
            <FormItem label="用户名：" prop="username">
              <Input v-model="updateUserForm.username"></Input>
            </FormItem>
          </Col>
          <Col span="12">
            <FormItem label="新密码：" prop="password">
              <Input type="password" v-model="updateUserForm.newpassword"></Input>
            </FormItem>
          </Col>
        </Row>
        <Row>
          <Col span="12">
            <FormItem label="角色：">
                <Select v-model="updateUserForm.role">
                    <Option v-for="item in roleList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                </Select>
            </FormItem>
          </Col>
          <Col span="12"> 
            <FormItem label="属组：">
                <Select v-model="updateUserForm.groups[0]">
                    <Option v-for="item in groupList" :value="item.value" :key="item.value">{{ item.label }}</Option>
                </Select>
            </FormItem>
          </Col>
        </Row>
        <FormItem label="权限：">          
          <Transfer
            :data="updateUserForm.permissionList"
            :target-keys="targetKeysupdate"
            filterable
            :filter-method="filterMethod"
            @on-change="handleChangeupdate"
            :list-style="listStyle"
            :titles="transferTitles">
          </Transfer>
        </FormItem>
        <FormItem label="系统身份：">
          <CheckboxGroup v-model="updateUserForm.sysaccount">
              <Checkbox label="is_active">已激活</Checkbox>
              <Checkbox label="is_staff">登录后台</Checkbox>
              <Checkbox label="is_superuser">管理员</Checkbox>
          </CheckboxGroup>
        </FormItem>           
      </Form>  
    </Modal>  
  
    <Modal
        v-model="showPermisson.modal"
        width="450"
        :title="showPermisson.title">
        <div class="modalcontent">
          <p v-for="item in showPermisson.permissions" :value="item.id" :key="item.id">{{ item.name }}</p>
        </div>
    </Modal>      

    <Modal
        v-model="deleteModal"
        width="450"
        title="删除用户"
        @on-ok="handleDeleteUser">
        <div>
          <center> 删除用户 {{deletedata.username}} </center>
        </div>
    </Modal>

  </div>
</template>

<script>
  import {Button, Table, Modal, Message, Badge, Icon} from 'iview';
  import {GetUserList, UpdateUser, CreateUser, DeleteUser, GetGroupList, GetPermissonList} from '@/api/account/account'
  import {contains} from '@/utils/account/account'

  export default {
    components: {Button, Table, Modal, Message, Badge, Icon},
    data () {
      return {
        deleteModal:false,
        createModal:false,
        updateModal:false,
        // 创建穿梭框
        targetKeysCreate:[],
        targetKeysupdate:[],
        listStyle: {
          width: '300px',
          height: '300px'
        },
        transferTitles: ['系统权限', '用户权限'],
        permissionList:[],
        groupList:[],
        roleList:[
          {
            value: 'developer',
            label: '研发'
          },
          {
            value: 'developer_manager',
            label: '研发经理'
          },
          {
            value: 'developer_supremo',
            label: '研发总监'
          },                         
        ],
        // 显示用户权限
        showPermisson:{
          title:'',
          modal:false,
          permissions:[],
        },
        // 创建用户数据
        createUserForm: {
          username:'',
          password:'',
          sysaccount:['is_active', 'is_staff'],
          role:'developer',
          groups:[],
        },
        ruleCreateUserForm: {
          username: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
          password: [{ required: true, message: '密码不能为空', trigger: 'blur' }],
        },
        // 修改用户数据
        updateUserForm: {
          id: '',
          username:'',
          password:'',
          newpassword:'',
          permissionList:[],  //  此处赋值'' ，会引起 vue.esm.js:591 [Vue warn]: Invalid prop: type check failed for prop "data". Expected Array, got String.
          sysaccount:[],
          role:'',
          groups:[],
        },
        ruleUpdateUserForm: {
          username: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
        },
        columnsUser: [
          {
              title: '用户名',
              render: (h, params) => {
                return h('Avatar', {style:{color: "#f56a00",backgroundColor: "#fde3cf"}}, params.row.username)
              }
          },
          {
              title: '角色',
              render: (h, params) => {
                const roleMap = {
                  developer:'研发',
                  developer_manager:'研发经理',
                  developer_supremo:'研发总监'
                }
                let role = params.row.role
                return h('span', {}, roleMap[role])
              }
          },
          {
              title: '属组',
              key: 'groups',
              render: (h, params) => {
                return h('span', {}, params.row.groups.name)
              }
          },
          {
              title: '权限',
              render: (h, params) => {
                let perms = params.row.perms
                if (perms.length == 0) {
                  var subelm = []
                } else {
                  var subelm = [
                    h(Button, {
                        props: {
                          type: 'info',
                          size: 'small'
                        },
                        style: {
                          marginRight: '12px'
                        },
                        on: {
                          click: () => {
                            console.log(params.row)
                            this.showPermisson.modal = true
                            this.showPermisson.title = params.row.username + ' 用户权限'
                            this.showPermisson.permissions = params.row.perms
                          }
                        }
                    }, '查看')
                  ]
                }
                return h('div', {}, subelm)
             }
          },
          {
              title: '系统身份',
              width: 220,
              render: (h, params) => {
                const iconMap = {
                  true: 'checkmark-circled',
                  false: 'close-circled'
                }
                let sysele = []
                let superuser = params.row.is_superuser
                let active = params.row.is_active
                let staff = params.row.is_staff
                sysele.push(h('span', {}, '管理员'))
                sysele.push(h('Icon', {props:{type:iconMap[superuser]}, style:{marginRight:'10px'}}, ''))
                sysele.push(h('span', {}, '已激活'))
                sysele.push(h('Icon', {props:{type:iconMap[active]}, style:{marginRight:'10px'}}, ''))
                sysele.push(h('span', {}, '登录后台'))
                sysele.push(h('Icon', {props:{type:iconMap[staff]}}, ''))
                return h('div', {}, sysele)
              }
          },
          {
              title: '操作',
              key: 'action',
              width: 150,
              align: 'center',
              render: (h, params) => {
                return h('div', [
                  h(Button, {
                      props: {
                        type: 'primary',
                        size: 'small'
                      },
                      style: {
                        marginRight: '12px'
                      },
                      on: {
                        click: () => {
                          console.log(params.row)
                          this.updateModal = true
                          this.updateUserForm.id = params.row.id
                          this.updateUserForm.username = params.row.username
                          this.updateUserForm.role = params.row.role
                          this.updateUserForm.groups = JSON.stringify(params.row.groups) == "{}" ? [] : [params.row.groups.id]
                          console.log(this.updateUserForm.role)
                          this.updateUserForm.password = params.row.password
                          this.updateUserForm.newpassword = ''
                          // 系统身份
                          let sysaccount = []
                          if (params.row.is_superuser == true) {
                            sysaccount.push('is_superuser')
                          }
                          if (params.row.is_active == true) {
                            sysaccount.push('is_active')
                          }
                          if (params.row.is_staff == true) {
                            sysaccount.push('is_staff')
                          }
                          this.updateUserForm.sysaccount = sysaccount
                          // 用户的权限数据
                          let perms = []
                          let userperms = params.row.perms
                          for (let i in userperms) {
                            perms.push(userperms[i].id)
                          }
                          this.targetKeysupdate = perms
                          // 系统的权限数据
                          let sourceperms = []
                          let permissionList = this.permissionList
                          for ( let i in permissionList) {
                            if (contains(userperms, permissionList[i].id) == false ){
                              sourceperms.push(permissionList[i])
                            }
                          }
                          this.updateUserForm.permissionList = sourceperms
                        }
                      }
                  }, '修改'),
                  h(Button, {
                    props: {
                      type: 'error',
                      size: 'small'
                    },
                    on: {
                      click: () => {
                        this.deleteModal = true
                        this.deletedata.id = params.row.id
                        this.deletedata.username = params.row.username
                      }
                    }
                  }, '删除')
                ])
              }
          },          

        ],
        // delete
        deletedata: {
          id:'',
          username:'',
        },
        // get
        total:1,
        userList:[],
        getParams:{
          page:1,
          pagesize:10,
          search:'',
        }
      }
    },

    created (){
      this.handleGetPermissonList()
      this.handleGetGroupList()
      this.handleGetUserList()
    },

    methods: {

      notice (title, msg) {
        this.$Notice.success({
          title: title,
          duration: 6,
          desc: msg
        });
      },

      pageChange (page) {
        this.getParams.page = page
        this.handleGetUserList()
      },

      sizeChange(size){
        this.getParams.pagesize = size
        this.handleGetUserList()
      },

      permsFormat (permissonlist) {
        let perms = []
        permissonlist.map( (item) => {
            perms.push({
              key: item.id,
              label: item.perm_name,
              description: item.codename,
              //disabled: Math.random() * 3 < 1
            });
        });
        this.permissionList = perms
      },

      groupsFormat (grouplist) {
        console.log(grouplist)
        let groups = []
        grouplist.map( (item) => {
          groups.push({
            value:item.id,
            label:item.name
          })
        })
        this.groupList = groups
        this.createUserForm.groups = groups.length > 0 ? [groups[0].value] : [] // 设置 groups 默认值 
        console.log(this.createUserForm.groups)
      },

      handleChangeCreate (newTargetKeys) {
        this.targetKeysCreate = newTargetKeys;
      },

      handleChangeupdate (newTargetKeys) {
        this.targetKeysupdate = newTargetKeys;
      },

      filterMethod (data, query) {
        return data.label.indexOf(query) > -1;
      },

      handleCreateUser () {
        this.$refs.createUserForm.validate((valid) => {
          if (!valid) {
            return
          }
          let data = this.createUserForm
          data.user_permissions = this.targetKeysCreate
          CreateUser(data)
          .then(response => {
            let httpstatus = response.status
            if (httpstatus = 201) {
              let title = '服务器提示'
              let msg = '用户 ' + response.data.username + ' 创建成功'
              this.notice(title, msg)
            }
            this.handleGetUserList()
          })
          .catch(error => {
            console.log(error)
          })
        })
      },

      handleUpdateUser () {
        this.$refs.updateUserForm.validate((valid) => {
          if (!valid) {
            return
          }
          let data = this.updateUserForm
          data.user_permissions = this.targetKeysupdate
          delete data.permissionList
          console.log('----- ', data)
          UpdateUser(this.updateUserForm.id, data)
          .then(response => {
            console.log(response)
            let httpstatus = response.status
            if (httpstatus = 200) {
              let title = '服务器提示'
              let msg = '用户 ' + response.data.username + ' 修改成功'
              this.notice(title, msg)
            }
            this.handleGetUserList()
          })
          .catch(error => {
            console.log(error)
          })
        })
      },

      handleDeleteUser () {
        DeleteUser(this.deletedata.id)
        .then(response => {
          console.log(response)
          let httpstatus = response.status
          if (httpstatus = 204) {
            let title = '服务器提示'
            let msg = '用户 ' + this.deletedata.username + ' 删除成功'
            this.notice(title, msg)
          }
          this.handleGetUserList()
        })
        .catch(error => {
          console.log(error)
        })
      },

      handleGetPermissonList () {
        GetPermissonList({})
        .then(response => {
          console.log(response)
          let permissonlist = response.data.results
          this.permsFormat(permissonlist)
        })
        .catch(error => {
          console.log(error)
        })
      },

      handleGetUserList () {
        GetUserList(this.getParams)
        .then(response => {
          console.log(response)
          this.userList = response.data.results
          this.total = response.data.count
        })
        .catch(error => {
          console.log(error)
        })
      },

      handleGetGroupList () {
        GetGroupList(this.getParams)
        .then(response => {
          this.groupsFormat(response.data.results)
        })
        .catch(error => {
          console.log(error)
        })
      },

      cancel () {
        Message.info('Clicked cancel');
      },

    },


  }
</script>

