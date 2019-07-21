<style src="../../static/base.css"></style>

<template>
  <div>
    <Card>
      <Row>  
        <Col span="4">
          <Input icon="search" v-model="getParams.search" placeholder="搜索" @on-click="handleGetGroupList" @on-enter="handleGetGroupList" />
        </Col>

        <Col span="10">
          <center>
            <Button type="primary" @click='createModal = true'>创建组</Button>
          </center>
        </Col>
      </Row>
      </br>
      <Row>
        <Col span="23">
          <Table :columns="columnsUser" :data="groupList" size="small"></Table>
        </Col>
      </Row>
      </br>
      <Page :total=total show-sizer :current=getParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>
    </Card>
    <copyright> </copyright>
    
    <Modal
      v-model="createModal"
      width="800"
      title="创建组"
      @on-ok="handleCreateGroup"
      @on-cancel="cancel">
      <Form ref="createGroupForm" :model="createGroupForm" :rules="ruleCreateGroupForm" :label-width="100">
        <Row>
          <Col span="12">
            <FormItem label="组名：" prop="name">
              <Input v-model="createGroupForm.name"></Input>
            </FormItem>
          </Col>
        </Row>
        <FormItem label="权限：">          
          <Transfer
            :data="permissionList"
            :target-keys="createGroupForm.db_id_list"
            filterable
            :filter-method="filterMethod"
            @on-change="handleChangecreate"
            :list-style="listStyle"
            :titles="transferTitles">
          </Transfer>
        </FormItem>      
      </Form>  
    </Modal>      

    <Modal
      v-model="updateModal"
      width="800"
      title="修改组"
      @on-ok="handleUpdateGroup"
      @on-cancel="cancel">
      <Form ref="updateGroupForm" :model="updateGroupForm" :rules="ruleUpdateGroupForm" :label-width="100">
        <Row>
          <Col span="12">
            <FormItem label="组名：" prop="name">
              <Input v-model="updateGroupForm.name"></Input>
            </FormItem>
          </Col>
        </Row>
        <FormItem label="数据库权限：">          
          <Transfer
            :data="updateGroupForm.sourcePerms"
            :target-keys="updateGroupForm.db_id_list"
            filterable
            :filter-method="filterMethod"
            @on-change="handleChangeupdate"
            :list-style="listStyle"
            :titles="transferTitles">
          </Transfer>
        </FormItem>         
      </Form>  
    </Modal>  
  
    <Modal
        v-model="showContent.modal"
        width="450"
        :title="showContent.title">
        <div class="modalcontent">
          <div v-for="item in showContent.data" :value="item.label" :key="item.label">
            <p v-if="item.role == 'developer'"> {{ item.name }} ( 研发 ) </p>
            <p v-else-if="item.role == 'developer_manager'"> {{ item.name }} ( 研发经理 ) </p>
            <p v-else-if="item.role == 'developer_supremo'"> {{ item.name }} ( 研发总监 ) </p>
            <p v-else> {{ item.label }} </p>
          </div>
        </div>
    </Modal>      

    <Modal
        v-model="deleteModal"
        width="450"
        title="删除组"
        @on-ok="handleDeleteGroup">
        <div>
          <center> 删除组 {{deleteData.name}} </center>
        </div>
    </Modal>

  </div>
</template>
<script>
  import {Button, Table, Modal, Message, Badge} from 'iview';
  import {GetPermissonList, GetGroupList, CreateGroup, UpdateGroup, DeleteGroup} from '@/api/account/account'
  import {contains} from '@/utils/account/account';
  import copyright from '../my-components/public/copyright'

  export default {
    components: {Button, Table, Modal, Message, Badge, copyright},
    data () {
      return {
        deleteModal:false,
        createModal:false,
        updateModal:false,
        // 创建穿梭框        
        listStyle:{
          width: '300px',
          height: '300px'
        },
        transferTitles:['可选', '已选'],
        permissionList:[],
        groupList:[],
        // 显示组权限或成员
        showContent:{
          modal:false,
          title:'',
          data:[],
        },
        // 创建组数据
        createGroupForm:{
          name:'',
          db_id_list:[],
        },
        ruleCreateGroupForm:{
          name: [{ required: true, message: '组名不能为空', trigger: 'blur' }],
        },
        // 修改组数据
        updateGroupForm:{
          id: '',
          name:'',
          sourcePerms:[],
          db_id_list:[]
        },
        ruleUpdateGroupForm:{
          name: [{ required: true, message: '组名不能为空', trigger: 'blur' }],
        },
        columnsUser: [
          {
              title: '组名',
              render: (h, params) => {
                return h('Tag', {}, params.row.name)
              }
          },
          {
              title: '权限',
              render: (h, params) => {
                let data = params.row.perms
                if (data == 0) {
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
                            this.showContent.modal = true
                            this.showContent.title = params.row.name + ' 数据库权限'
                            let permissions= []
                            for (let perm of data) {
                              for (let p of this.permissionList) {
                                if (perm.id == p.key) {
                                  permissions.push(p)
                                }
                              }
                            }
                            this.showContent.data = permissions
                            console.log(permissions)
                          }
                        }
                    }, '权限')
                  ]
                }
                return h('div', {}, subelm)
             }
          },
          {
              title: '成员',
              render: (h, params) => {
                let data = params.row.members
                if (data.length == 0) {
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
                            this.showContent.modal = true
                            this.showContent.title = params.row.name + ' 成员'
                            this.showContent.data = data
                          }
                        }
                    }, '成员')
                  ]
                }
                return h('div', {}, subelm)
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
                          this.updateModal = true
                          this.updateGroupForm.id = params.row.id
                          this.updateGroupForm.name = params.row.name
                          // 组的权限数据
                          let perms = []
                          const groupperms = params.row.perms
                          groupperms.map( (item) => {
                            perms.push(item.id)
                          })
                          this.updateGroupForm.db_id_list = perms
                          // 系统的权限数据
                          let sourceperms = []
                          this.permissionList.map( (item) => {
                            if (contains(groupperms, item.id) == false){
                              sourceperms.push(item)
                            }
                          })
                          this.updateGroupForm.sourcePerms = sourceperms
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
                        this.deleteData.id = params.row.id
                        this.deleteData.name = params.row.name
                      }
                    }
                  }, '删除')
                ])
              }
          },          

        ],
        // delete
        deleteData: {
          id:'',
          name:'',
        },
        // get
        total:1,
        userlist:[],
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
        this.handleGetGroupList()
      },

      sizeChange(size){
        this.pagesize = size
        this.handleGetGroupList()
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

      handleChangecreate (newTargetKeys) {
        this.createGroupForm.db_id_list = newTargetKeys;
      },

      handleChangeupdate (newTargetKeys) {
        this.updateGroupForm.db_id_list = newTargetKeys;
      },

      filterMethod (data, query) {
        return data.label.indexOf(query) > -1;
      },

      handleCreateGroup () {
        this.$refs.createGroupForm.validate((valid) => {
          if (!valid) {
            return
          }
          CreateGroup(this.createGroupForm)
          .then(response => {
            let httpstatus = response.status
            if (httpstatus == 201) {
              let title = '服务器提示'
              let msg = '组 ' + response.data.name + ' 创建成功'
              this.notice(title, msg)
            }
            this.handleGetGroupList()
          })
          .catch(error => {
            console.log(error)
          })
        })
      },

      handleUpdateGroup () {
        this.$refs.updateGroupForm.validate((valid) => {
          if (!valid) {
            return
          }
          delete this.updateGroupForm.sourcePerms
          UpdateGroup(this.updateGroupForm.id, this.updateGroupForm)
          .then(response => {
            let httpstatus = response.status
            if (httpstatus == 200) {
              let title = '服务器提示'
              let msg = '组 ' + response.data.name + ' 修改成功'
              this.notice(title, msg)
            }
            this.handleGetGroupList()
          })
          .catch(error => {
            console.log(error)
          })
        })
      },

      handleDeleteGroup () {
        DeleteGroup(this.deleteData.id)
        .then(response => {
          let httpstatus = response.status
          if (httpstatus == 204) {
            let title = '服务器提示'
            let msg = '组 ' + this.deleteData.name + ' 删除成功'
            this.notice(title, msg)
          }
          this.handleGetGroupList()
        })
        .catch(error => {
          console.log(error)
        })
      },

      handleGetPermissonList () {
        GetPermissonList({})
        .then(response => {
          let permissonlist = response.data.results
          this.permsFormat(permissonlist)
        })
        .catch(error => {
          console.log(error)
        })
      },

      handleGetGroupList () {
        GetGroupList(this.getParams)
        .then(response => {
          this.groupList = response.data.results
          console.log(this.groupList)
          this.total = response.data.count
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

